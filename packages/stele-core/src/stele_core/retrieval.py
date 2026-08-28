"""Hybrid retrieval over promoted entries (C2)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from stele_core.index.lexical import LexicalIndex, tokenize
from stele_core.index.semantic import SemanticIndex
from stele_core.index.temporal import is_stale, parse_ts
from stele_core.schema import validate_scope
from stele_core.store import SteleStore


def _scope_allows(
    entry_scope: str,
    consumer_scope: str,
    *,
    consumer_domain: str | None,
    scope_override: Sequence[str] | None,
) -> bool:
    """TECH_SPEC §4.3: exact project ∪ matching domain ∪ universal; else override."""
    if scope_override and entry_scope in scope_override:
        return True
    if entry_scope == "universal":
        return True
    if entry_scope == consumer_scope:
        return True
    if consumer_domain:
        validate_scope(consumer_domain)
        if not consumer_domain.startswith("domain:"):
            raise ValueError("consumer_domain must be domain:<name>")
        if entry_scope == consumer_domain:
            return True
    return False


def rrf_fuse(
    rankings: list[list[tuple[str, float]]],
    *,
    k: int = 60,
) -> list[str]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, (eid, _) in enumerate(ranking):
            scores[eid] = scores.get(eid, 0.0) + 1.0 / (k + rank + 1)
    return [eid for eid, _ in sorted(scores.items(), key=lambda x: (-x[1], x[0]))]


def estimate_tokens(entry: dict[str, Any], *, body: str | None = None) -> int:
    text = f"{entry.get('title', '')} {body if body is not None else entry.get('body', '')}"
    return max(1, len(text.split()))


def _usage_score(entry: dict[str, Any]) -> tuple[int, int, int]:
    """Sort key: pinned first, then helpful-harmful, then helpful."""
    u = entry.get("usage") or {}
    pinned = 1 if u.get("pinned") else 0
    helpful = int(u.get("helpful") or 0)
    harmful = int(u.get("harmful") or 0)
    return (pinned, helpful - harmful, helpful)


def _match_reasons(
    entry: dict[str, Any],
    *,
    query: str,
    via_link: bool,
    linked_from: str | None,
    stale: bool,
    model_mismatch: bool,
    env_mismatch: bool,
) -> list[str]:
    reasons: list[str] = []
    q = set(tokenize(query))
    doc = set(tokenize(f"{entry.get('title', '')} {entry.get('body', '')}"))
    overlap = sorted(q & doc)[:8]
    if overlap:
        reasons.append("terms:" + ",".join(overlap))
    reasons.append(f"scope:{entry.get('scope')}")
    if via_link and linked_from:
        reasons.append(f"via_link:{linked_from}")
    if stale:
        reasons.append("stale")
    if model_mismatch:
        reasons.append("model_mismatch")
    if env_mismatch:
        reasons.append("env_mismatch")
    u = entry.get("usage") or {}
    if u.get("pinned"):
        reasons.append("pinned")
    if int(u.get("helpful") or 0) > 0:
        reasons.append(f"helpful:{u['helpful']}")
    return reasons


def _clip_body(body: str, body_max_chars: int | None) -> tuple[str, bool]:
    if body_max_chars is None or body_max_chars < 1 or len(body) <= body_max_chars:
        return body, False
    return body[: body_max_chars].rstrip() + "…", True


def _valid_at_point(entry: dict[str, Any], as_of: str) -> bool:
    """True if the belief was in force at as_of (including later-superseded)."""
    t = entry["temporal"]
    if parse_ts(t["valid_from"]) > parse_ts(as_of):
        return False
    expiry = t.get("expiry")
    if expiry and parse_ts(expiry) <= parse_ts(as_of):
        return False
    superseded_at = t.get("superseded_at")
    if superseded_at and parse_ts(superseded_at) <= parse_ts(as_of):
        return False
    revoked_at = t.get("revoked_at")
    if revoked_at and parse_ts(revoked_at) <= parse_ts(as_of):
        return False
    if entry.get("state") == "quarantined":
        return False
    return True


class Retriever:
    def __init__(
        self,
        store: SteleStore,
        *,
        embedder: Any | None = None,
        staleness_horizon: str | None = None,
    ):
        self.store = store
        self.embedder = embedder
        self.staleness_horizon = staleness_horizon
        self.lexical = LexicalIndex()
        self.semantic = SemanticIndex()
        self.rebuild(lexical_only=True)

    def rebuild(self, *, lexical_only: bool = False) -> None:
        promoted = list(
            self.store.iter_entries(
                states={"promoted", "contested", "expired", "superseded", "revoked"}
            )
        )
        self.lexical.rebuild(promoted)
        if not lexical_only and self.embedder is not None:
            self.semantic.rebuild(promoted, self.embedder)

    def search(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        as_of: str | None = None,
        include_contested: bool = False,
        scope_override: Sequence[str] | None = None,
        consumer_domain: str | None = None,
        now: str | None = None,
        consumer_env: Sequence[str] | None = None,
        stale_policy: str = "flag",
        consumer_model_id: str | None = None,
        model_policy: str = "flag",
        follow_links: bool = False,
        follow_link_depth: int = 1,
        body_max_chars: int | None = None,
        prefer_helpful: bool = True,
        with_rank_detail: bool = False,
    ) -> list[dict[str, Any]]:
        validate_scope(consumer_scope)
        if stale_policy not in {"flag", "withhold"}:
            raise ValueError("stale_policy must be 'flag' or 'withhold'")
        if model_policy not in {"flag", "withhold"}:
            raise ValueError("model_policy must be 'flag' or 'withhold'")
        if follow_link_depth < 1 or follow_link_depth > 3:
            raise ValueError("follow_link_depth must be 1..3")
        # Empty query → ∅ is first-class (C2); never dump the ledger (OP-9 Compress).
        if not query.strip():
            return []

        # Lazy semantic refresh — never on the write path (C5).
        if self.embedder is not None:
            promoted = list(
                self.store.iter_entries(
                    states={"promoted", "contested", "expired", "superseded", "revoked"}
                )
            )
            if set(self.semantic.vectors.keys()) != {e["id"] for e in promoted}:
                self.semantic.rebuild(promoted, self.embedder)

        point = as_of or now
        if point is None:
            point = "9999-12-31T23:59:59Z"

        by_id = {e["id"]: e for e in self.store.iter_entries()}
        lex = self.lexical.search(query)
        lex_rank = {eid: i for i, (eid, _) in enumerate(lex)}
        lex_score = {eid: score for eid, score in lex}
        rankings = [lex]
        semantic_rank: dict[str, int] = {}
        if self.embedder is not None:
            qvec = self.embedder.embed([query])[0]
            sem = self.semantic.search(qvec)
            rankings.append(sem)
            semantic_rank = {eid: i for i, (eid, _) in enumerate(sem)}

        fused = rrf_fuse(rankings)
        rrf_rank = {eid: i for i, eid in enumerate(fused)}
        if prefer_helpful:
            fused = sorted(
                fused,
                key=lambda eid: (
                    -(_usage_score(by_id[eid])[0] if eid in by_id else 0),
                    -(_usage_score(by_id[eid])[1] if eid in by_id else 0),
                    -(_usage_score(by_id[eid])[2] if eid in by_id else 0),
                    rrf_rank[eid],
                ),
            )

        slices: list[dict[str, Any]] = []
        used = 0
        historical_mode = (
            as_of is not None and now is not None and parse_ts(as_of) != parse_ts(now)
        )
        consumer_env_set = {x.lower() for x in (consumer_env or [])}

        for eid in fused:
            entry = by_id.get(eid)
            if entry is None:
                continue
            state = entry["state"]

            if as_of is not None:
                if not _valid_at_point(entry, as_of):
                    continue
                # Point-in-time may surface expired/superseded/revoked beliefs; always flag.
                hist = (
                    True
                    if state in {"expired", "superseded", "revoked", "archived"}
                    or historical_mode
                    else False
                )
            else:
                if state == "quarantined":
                    continue
                if state == "contested" and not include_contested:
                    continue
                if state in {"expired", "superseded", "revoked", "archived"}:
                    continue
                if state != "promoted" and not (include_contested and state == "contested"):
                    continue
                hist = False

            if not _scope_allows(
                entry["scope"],
                consumer_scope,
                consumer_domain=consumer_domain,
                scope_override=scope_override,
            ):
                continue

            stale = is_stale(entry, point, self.staleness_horizon)
            if stale and stale_policy == "withhold":
                continue
            assumptions = [str(a) for a in (entry.get("env_assumptions") or [])]
            missing = []
            if assumptions and consumer_env_set:
                missing = [a for a in assumptions if a.lower() not in consumer_env_set]
            elif assumptions and consumer_env is not None and not consumer_env_set:
                missing = list(assumptions)
            entry_model = entry.get("provenance", {}).get("model_id")
            model_mismatch = bool(
                consumer_model_id
                and entry_model
                and str(entry_model) != str(consumer_model_id)
            )
            if model_mismatch and model_policy == "withhold":
                continue
            body, truncated = _clip_body(str(entry["body"]), body_max_chars)
            tok = estimate_tokens(entry, body=body)
            if used + tok > budget and slices:
                break
            if used + tok > budget and not slices:
                break
            env_mismatch = bool(missing)
            reasons = _match_reasons(
                entry,
                query=query,
                via_link=False,
                linked_from=None,
                stale=stale,
                model_mismatch=model_mismatch,
                env_mismatch=env_mismatch,
            )
            if entry.get("conflict_key"):
                reasons.append(f"conflict_key:{entry['conflict_key']}")
            slice_row = {
                "id": entry["id"],
                "title": entry["title"],
                "body": body,
                "body_truncated": truncated,
                "layer": entry["layer"],
                "scope": entry["scope"],
                "state": state,
                "links": entry.get("links") or [],
                "provenance": entry["provenance"],
                "env_assumptions": assumptions,
                "env_mismatch": env_mismatch,
                "missing_env_assumptions": missing,
                "model_mismatch": model_mismatch,
                "stale": stale,
                "historical": hist,
                "contested": state == "contested",
                "via_link": False,
                "usage": entry.get("usage") or {},
                "match_reasons": reasons,
            }
            if entry.get("conflict_key"):
                slice_row["conflict_key"] = entry["conflict_key"]
            if with_rank_detail:
                slice_row["rank_detail"] = {
                    "rrf_rank": rrf_rank.get(eid),
                    "lexical_rank": lex_rank.get(eid),
                    "lexical_score": lex_score.get(eid),
                    "semantic_rank": semantic_rank.get(eid),
                }
            slices.append(slice_row)
            used += tok

        if follow_links and slices:
            for _hop in range(follow_link_depth):
                before = len(slices)
                slices = self._expand_entry_links(
                    slices,
                    by_id=by_id,
                    query=query,
                    consumer_scope=consumer_scope,
                    consumer_domain=consumer_domain,
                    scope_override=scope_override,
                    include_contested=include_contested,
                    as_of=as_of,
                    point=point,
                    historical_mode=historical_mode,
                    consumer_env=consumer_env,
                    consumer_env_set=consumer_env_set,
                    stale_policy=stale_policy,
                    consumer_model_id=consumer_model_id,
                    model_policy=model_policy,
                    body_max_chars=body_max_chars,
                    budget=budget,
                    used=sum(estimate_tokens({"title": s["title"], "body": s["body"]}) for s in slices),
                )
                if len(slices) == before:
                    break

        return slices

    def _expand_entry_links(
        self,
        slices: list[dict[str, Any]],
        *,
        by_id: dict[str, Any],
        query: str,
        consumer_scope: str,
        consumer_domain: str | None,
        scope_override: Sequence[str] | None,
        include_contested: bool,
        as_of: str | None,
        point: str,
        historical_mode: bool,
        consumer_env: Sequence[str] | None,
        consumer_env_set: set[str],
        stale_policy: str,
        consumer_model_id: str | None,
        model_policy: str,
        body_max_chars: int | None,
        budget: int,
        used: int,
    ) -> list[dict[str, Any]]:
        """One-hop LINK kind=entry expansion (FF-6 / Karsenty) within budget."""
        seen = {s["id"] for s in slices}
        out = list(slices)
        for base in list(slices):
            for link in base.get("links") or []:
                if link.get("kind") != "entry":
                    continue
                eid = link.get("ref")
                if not isinstance(eid, str) or eid in seen:
                    continue
                entry = by_id.get(eid)
                if entry is None:
                    continue
                state = entry["state"]
                if as_of is not None:
                    if not _valid_at_point(entry, as_of):
                        continue
                    hist = True if state in {"expired", "superseded"} or historical_mode else False
                else:
                    if state == "quarantined":
                        continue
                    if state == "contested" and not include_contested:
                        continue
                    if state in {"expired", "superseded"}:
                        continue
                    if state != "promoted" and not (
                        include_contested and state == "contested"
                    ):
                        continue
                    hist = False
                if not _scope_allows(
                    entry["scope"],
                    consumer_scope,
                    consumer_domain=consumer_domain,
                    scope_override=scope_override,
                ):
                    continue
                stale = is_stale(entry, point, self.staleness_horizon)
                if stale and stale_policy == "withhold":
                    continue
                assumptions = [str(a) for a in (entry.get("env_assumptions") or [])]
                missing: list[str] = []
                if assumptions and consumer_env_set:
                    missing = [a for a in assumptions if a.lower() not in consumer_env_set]
                elif assumptions and consumer_env is not None and not consumer_env_set:
                    missing = list(assumptions)
                entry_model = entry.get("provenance", {}).get("model_id")
                model_mismatch = bool(
                    consumer_model_id
                    and entry_model
                    and str(entry_model) != str(consumer_model_id)
                )
                if model_mismatch and model_policy == "withhold":
                    continue
                body, truncated = _clip_body(str(entry["body"]), body_max_chars)
                tok = estimate_tokens(entry, body=body)
                if used + tok > budget:
                    continue
                env_mismatch = bool(missing)
                out.append(
                    {
                        "id": entry["id"],
                        "title": entry["title"],
                        "body": body,
                        "body_truncated": truncated,
                        "layer": entry["layer"],
                        "scope": entry["scope"],
                        "state": state,
                        "links": entry.get("links") or [],
                        "provenance": entry["provenance"],
                        "env_assumptions": assumptions,
                        "env_mismatch": env_mismatch,
                        "missing_env_assumptions": missing,
                        "model_mismatch": model_mismatch,
                        "stale": stale,
                        "historical": hist,
                        "contested": state == "contested",
                        "via_link": True,
                        "linked_from": base["id"],
                        "usage": entry.get("usage") or {},
                        "match_reasons": _match_reasons(
                            entry,
                            query=query,
                            via_link=True,
                            linked_from=base["id"],
                            stale=stale,
                            model_mismatch=model_mismatch,
                            env_mismatch=env_mismatch,
                        ),
                    }
                )
                seen.add(eid)
                used += tok
        return out
