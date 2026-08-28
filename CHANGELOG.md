# Changelog

All notable changes to Stele are documented here.

## [18.15.0] — 2026-08-28

### Added
- **SDT** (arXiv:2410.09016): dim, mask, tune, score (`sdt_*`).
- **MEFT** (arXiv:2406.04984): adapt, route, fetch, score (`mef_*`).
- Harness: `sdt_mef_shaped_report`. MCP +12 → **2003**.

### Fixed
- Pin `mcp>=1.0,<2` (`stele-mcp` + `requirements-dev.txt`). mcp 2.x drops
  `mcp.server.fastmcp` and broke the `stele-mcp` console entrypoint.
- Runtime smoke: `test_mcp_runtime.py` imports FastMCP + live tool registry
  (AST-only checks could not catch the import failure).

### Docs
- PRD / TECH_SPEC **v18.15.0** (UC-1968–1978). ROADMAP Phase 191. Frontiers §§406–407.

## [18.14.0] — 2026-08-24

### Added
- **C3A** (arXiv:2407.19342): kernel, circ, fft, score (`c3a_*`).
- **BOFT** (arXiv:2311.06243): block, orth, butter, score (`bof_*`).
- Harness: `c3a_bof_shaped_report`. MCP +12 → **1991**.

### Docs
- PRD / TECH_SPEC **v18.14.0** (UC-1957–1967). ROADMAP Phase 190. Frontiers §§404–405.

## [18.13.0] — 2026-08-22

### Added
- **CaRA** (ICML 2025, OpenReview:vexHifrbJg): mha, ffn, cpd, score (`cra_*`).
- **LoRETTA** (arXiv:2402.11417): adp, rep, tt, score (`ltt_*`).
- Harness: `cra_ltt_shaped_report`. MCP +12 → **1979**.

### Docs
- PRD / TECH_SPEC **v18.13.0** (UC-1946–1956). ROADMAP Phase 189. Frontiers §§402–403.

## [18.12.0] — 2026-08-22

### Added
- **FacT** (arXiv:2212.03145): tensor, tt, tucker, score (`fct_*`).
- **LoTR** (arXiv:2402.01376): stack, core, share, score (`ltr_*`).
- Harness: `fct_ltr_shaped_report`. MCP +12 → **1967**.

### Docs
- PRD / TECH_SPEC **v18.12.0** (UC-1935–1945). ROADMAP Phase 188. Frontiers §§400–401.

## [18.11.0] — 2026-08-22

### Added
- **TensLoRA** (arXiv:2509.19391): stack, tucker, mode, score (`tnl_*`).
- **AdaZeta** (arXiv:2406.18060): tt, ff, query, score (`azt_*`).
- Harness: `tnl_azt_shaped_report`. MCP +12 → **1955**.

### Docs
- PRD / TECH_SPEC **v18.11.0** (UC-1924–1934). ROADMAP Phase 187. Frontiers §§398–399.

## [18.10.0] — 2026-08-22

### Added
- **LoRAFusion** (arXiv:2510.00206): split, fuse, batch, score (`lfu_*`).
- **TeRA** (arXiv:2509.03234): tucker, freeze, scale, score (`ter_*`).
- Harness: `lfu_ter_shaped_report`. MCP +12 → **1943**.

### Docs
- PRD / TECH_SPEC **v18.10.0** (UC-1913–1923). ROADMAP Phase 186. Frontiers §§396–397.

## [18.9.0] — 2026-08-22

### Added
- **ALoRA** (arXiv:2403.16187): init, ablate, prune, score (`alo_*`).
- **LN Tuning** (arXiv:2312.11420): attn, scale, train, score (`lnt_*`).
- Harness: `alo_lnt_shaped_report`. MCP +12 → **1931**.

### Docs
- PRD / TECH_SPEC **v18.9.0** (UC-1902–1912). ROADMAP Phase 185. Frontiers §§394–395.

## [18.8.0] — 2026-08-22

### Added
- **LoRTA** (arXiv:2410.04060): tensor, cp, share, score (`lrt_*`).
- **C-LoRA** (arXiv:2502.17920): route, task, ortho, score (`clo_*`).
- Harness: `lrt_clo_shaped_report`. MCP +12 → **1919**.

### Docs
- PRD / TECH_SPEC **v18.8.0** (UC-1891–1901). ROADMAP Phase 184. Frontiers §§392–393.

## [18.7.0] — 2026-08-22

### Added
- **HRA** (arXiv:2405.17484): house, reflect, train, score (`hra_*`).
- **Hybrid PEFT** (arXiv:2507.18076): lora, boft, fuse, score (`hyb_*`).
- Harness: `hra_hyb_shaped_report`. MCP +12 → **1907**.

### Docs
- PRD / TECH_SPEC **v18.7.0** (UC-1880–1890). ROADMAP Phase 183. Frontiers §§390–391.

## [18.6.0] — 2026-08-22

### Added
- **NLoRA** (arXiv:2502.14482): landmark, nystrom, init, score (`nlr_*`).
- **ROSA** random subspace (arXiv:2407.07802): subspace, project, train, score (`rsa_*`).
- Harness: `nlr_rsa_shaped_report`. MCP +12 → **1895**.

### Docs
- PRD / TECH_SPEC **v18.6.0** (UC-1869–1879). ROADMAP Phase 182. Frontiers §§388–389.

## [18.5.0] — 2026-08-21

### Added
- **LongLoRA** (arXiv:2309.12307): window, shift, lora, score (`llr_*`).
- **LISA** (arXiv:2403.17919): layers, sample, unfreeze, score (`lis_*`).
- Harness: `llr_lis_shaped_report`. MCP +12 → **1883**.

### Docs
- PRD / TECH_SPEC **v18.5.0** (UC-1858–1868). ROADMAP Phase 181. Frontiers §§386–387.

## [18.4.0] — 2026-08-21

### Added
- **HiRA** (ICLR 2025 Oral, OpenReview:TwJrTz9cRS; no arXiv after live fetch): base, factors, hadamard, score (`hir_*`).
- **PLoRA concurrent** (arXiv:2508.02932): pack, fuse, train, score (`cnl_*`).
- Harness: `hir_cnl_shaped_report`. MCP +12 → **1871**.

### Docs
- PRD / TECH_SPEC **v18.4.0** (UC-1847–1857). ROADMAP Phase 180. Frontiers §§384–385.

## [18.3.0] — 2026-08-21

### Added
- **GLoRA** (arXiv:2306.07967): prompt, scale, search, score (`glo_*`).
- **PeriodicLoRA** (arXiv:2402.16141): stage, merge, reset, score (`plr_*`).
- Harness: `glo_plr_shaped_report`. MCP +12 → **1859**.

### Docs
- PRD / TECH_SPEC **v18.3.0** (UC-1836–1846). ROADMAP Phase 179. Frontiers §§382–383.

## [18.2.0] — 2026-08-21

### Added
- **BoHA** (arXiv:2509.21637): split, hadamard, train, score (`bha_*`).
- **SMoA** (arXiv:2601.07507): struct, mod, train, score (`smo_*`).
- Harness: `bha_smo_shaped_report`. MCP +12 → **1847**.

### Docs
- PRD / TECH_SPEC **v18.2.0** (UC-1825–1835). ROADMAP Phase 178. Frontiers §§380–381.

## [18.1.0] — 2026-08-21

### Added
- **RoSA** (arXiv:2401.04679): rank, sparse, train, score (`ros_*`).
- **ABBA** (arXiv:2505.14238): left, right, hadamard, score (`abb_*`).
- Harness: `ros_abb_shaped_report`. MCP +12 → **1835**.

### Docs
- PRD / TECH_SPEC **v18.1.0** (UC-1814–1824). ROADMAP Phase 177. Frontiers §§378–379.

## [18.0.0] — 2026-08-21

### Added
- **Q-GaLore** (arXiv:2407.08296): weight, proj, lazy, score (`qga_*`).
- **LoRA-Flow** (arXiv:2402.11455): pool, gate, token, score (`lfw_*`).
- Harness: `qga_lfw_shaped_report`. MCP +12 → **1823**.

### Docs
- PRD / TECH_SPEC **v18.0.0** (UC-1803–1813). ROADMAP Phase 176. Frontiers §§376–377.

## [17.9.0] — 2026-08-21

### Added
- **Uni-LoRA** (arXiv:2506.00799): space, iso, vec, score (`ulo_*`).
- **BoRA** (arXiv:2412.06441): row, col, train, score (`bor_*`).
- Harness: `ulo_bor_shaped_report`. MCP +12 → **1811**.

### Docs
- PRD / TECH_SPEC **v17.9.0** (UC-1792–1802). ROADMAP Phase 175. Frontiers §§374–375.

## [17.8.0] — 2026-08-21

### Added
- **Tied-LoRA** (arXiv:2311.09578): tie, select, scale, score (`tld_*`).
- **QA-LoRA** (arXiv:2309.14717): group, quant, adapt, score (`qal_*`).
- Harness: `tld_qal_shaped_report`. MCP +12 → **1799**.

### Docs
- PRD / TECH_SPEC **v17.8.0** (UC-1781–1791). ROADMAP Phase 174. Frontiers §§372–373.

## [17.7.0] — 2026-08-21

### Added
- **MixLoRA** (arXiv:2404.15159): experts, route, attn, score (`mxl_*`).
- **SuperLoRA** (arXiv:2403.11887): group, fold, factor, score (`spr_*`).
- Harness: `mxl_spr_shaped_report`. MCP +12 → **1787**.

### Docs
- PRD / TECH_SPEC **v17.7.0** (UC-1770–1780). ROADMAP Phase 173. Frontiers §§370–371.

## [17.6.0] — 2026-08-21

### Added
- **FlyLoRA** (arXiv:2510.08396): proj, topk, train, score (`fly_*`).
- **NOLA** (arXiv:2310.02556): basis, coeff, train, score (`nla_*`).
- Harness: `fly_nla_shaped_report`. MCP +12 → **1775**.

### Docs
- PRD / TECH_SPEC **v17.6.0** (UC-1759–1769). ROADMAP Phase 172. Frontiers §§368–369.

## [17.5.0] — 2026-08-21

### Added
- **LoRA.rar** (arXiv:2412.05148): pair, hyper, merge, score (`lrr_*`).
- **SVFT** (arXiv:2405.19597): svd, sparse, train, score (`svf_*`).
- Harness: `lrr_svf_shaped_report`. MCP +12 → **1763**.

### Docs
- PRD / TECH_SPEC **v17.5.0** (UC-1748–1758). ROADMAP Phase 171. Frontiers §§366–367.

## [17.4.0] — 2026-08-21

### Added
- **LoRA-Composer** (arXiv:2403.11627): concepts, inject, isolate, score (`lco_*`).
- **CARE-LoRA** (arXiv:2607.11940): compress, recon, train, score (`car_*`).
- Harness: `lco_car_shaped_report`. MCP +12 → **1751**.

### Docs
- PRD / TECH_SPEC **v17.4.0** (UC-1737–1747). ROADMAP Phase 170. Frontiers §§364–365.

## [17.3.0] — 2026-08-21

### Added
- **ReLoRA** (arXiv:2307.05695): warm, merge, jagged, score (`rlr_*`).
- **ETHER** (arXiv:2405.20271): plane, reflect, train, score (`eth_*`).
- Harness: `rlr_eth_shaped_report`. MCP +12 → **1739**.

### Docs
- PRD / TECH_SPEC **v17.3.0** (UC-1726–1736). ROADMAP Phase 169. Frontiers §§362–363.

## [17.2.0] — 2026-08-21

### Added
- **DeLoRA** (arXiv:2503.18225): norm, bound, train, score (`dlr_*`).
- **MELoRA** (arXiv:2402.17263): mini, diag, train, score (`meo_*`).
- Harness: `dlr_meo_shaped_report`. MCP +12 → **1727**.

### Docs
- PRD / TECH_SPEC **v17.2.0** (UC-1715–1725). ROADMAP Phase 168. Frontiers §§360–361.

## [17.1.0] — 2026-08-21

### Added
- **SwitchLoRA** (arXiv:2406.06564): alloc, switch, train, score (`swl_*`).
- **Chain of LoRA / COLA** (arXiv:2401.04151): tune, knot, extend, score (`col_*`).
- Harness: `swl_col_shaped_report`. MCP +12 → **1715**.

### Docs
- PRD / TECH_SPEC **v17.1.0** (UC-1704–1714). ROADMAP Phase 167. Frontiers §§358–359.

## [17.0.0] — 2026-08-21

### Added
- **Punica** (arXiv:2310.18547): backbone, sgmv, sched, score (`pun_*`).
- **mLoRA** (arXiv:2312.02515): pipe, batch, train, score (`mla_*`).
- Harness: `pun_mla_shaped_report`. MCP +12 → **1703**.

### Docs
- PRD / TECH_SPEC **v17.0.0** (UC-1693–1703). ROADMAP Phase 166. Frontiers §§356–357.

## [16.9.0] — 2026-08-21

### Added
- **Compress then Serve** (arXiv:2407.00066): collect, basis, scale, score (`cts_*`).
- **FLoRA** (arXiv:2409.05976): clients, stack, agg, score (`flo_*`).
- Harness: `cts_flo_shaped_report`. MCP +12 → **1691**.

### Docs
- PRD / TECH_SPEC **v16.9.0** (UC-1682–1692). ROADMAP Phase 165. Frontiers §§354–355.

## [16.8.0] — 2026-08-21

### Added
- **LoRA-TSD** (arXiv:2409.01035): tsd, init, dash, score (`lts_*`).
- **S-LoRA** (arXiv:2311.03285): pool, page, batch, score (`slr_*`).
- Harness: `lts_slr_shaped_report`. MCP +12 → **1679**.

### Docs
- PRD / TECH_SPEC **v16.8.0** (UC-1671–1681). ROADMAP Phase 164. Frontiers §§352–353.

## [16.7.0] — 2026-08-21

### Added
- **LoRA-Mini** (arXiv:2411.15804): split, inner, train, score (`lmi_*`).
- **QDyLoRA** (arXiv:2402.10462): range, quant, train, score (`qdy_*`).
- Harness: `lmi_qdy_shaped_report`. MCP +12 → **1667**.

### Docs
- PRD / TECH_SPEC **v16.7.0** (UC-1660–1670). ROADMAP Phase 163. Frontiers §§350–351.

## [16.6.0] — 2026-08-21

### Added
- **MTL-LoRA** (arXiv:2410.09437): task, spec, share, score (`mtl_*`).
- **MALoRA** (arXiv:2410.22782): mix, down, up, score (`mal_*`).
- Harness: `mtl_mal_shaped_report`. MCP +12 → **1655**.

### Docs
- PRD / TECH_SPEC **v16.6.0** (UC-1649–1659). ROADMAP Phase 162. Frontiers §§348–349.

## [16.5.0] — 2026-08-21

### Added
- **LoraHub** (arXiv:2307.13269): pool, compose, adapt, score (`lhb_*`).
- **MultiLoRA** (arXiv:2311.11501): scale, init, train, score (`mlr_*`).
- Harness: `lhb_mlr_shaped_report`. MCP +12 → **1643**.

### Docs
- PRD / TECH_SPEC **v16.5.0** (UC-1638–1648). ROADMAP Phase 161. Frontiers §§346–347.

## [16.4.0] — 2026-08-21

### Added
- **LoRAMoE** (arXiv:2312.09979): plugin, balance, route, score (`lme_*`).
- **MoELoRA** (arXiv:2402.12851): experts, contrast, gate, score (`mel_*`).
- Harness: `lme_mel_shaped_report`. MCP +12 → **1631**.

### Docs
- PRD / TECH_SPEC **v16.4.0** (UC-1627–1637). ROADMAP Phase 160. Frontiers §§344–345.

## [16.3.0] — 2026-08-21

### Added
- **HydraLoRA** (arXiv:2404.19245): shared A, multi-B, MoE route (`hyd_*`).
- **LoRA-LEGO** (arXiv:2409.16167): MSU cluster merge (`llg_*`).
- Harness: `hyd_llg_shaped_report`. MCP +12 → **1619**.

### Docs
- PRD / TECH_SPEC **v16.3.0** (UC-1616–1626). ROADMAP Phase 159. Frontiers §§342–343.

## [16.2.0] — 2026-08-21

### Added
- **LoRA-Init** (arXiv:2409.01035): TSD init, train, score (`lin_*`).
- **LoRA-Null** (arXiv:2503.02659): activation null-space init (`lnu_*`).
- Harness: `lin_lnu_shaped_report`. MCP +12 → **1607**.

### Docs
- PRD / TECH_SPEC **v16.2.0** (UC-1605–1615). ROADMAP Phase 158. Frontiers §§340–341.

## [16.1.0] — 2026-08-21

### Added
- **LoRAShear** (arXiv:2310.18356): graph, prune, recover, score (`lsh_*`).
- **Alternating OPLoRA** (arXiv:2509.19977): sub, alt, train, score (`aop_*`).
- Harness: `lsh_aop_shaped_report`. MCP +12 → **1595**.

### Docs
- PRD / TECH_SPEC **v16.1.0** (UC-1594–1604). ROADMAP Phase 157. Frontiers §§338–339.

## [16.0.0] — 2026-08-21

### Added
- **GeoLoRA** (arXiv:2410.18720): dyn, budget, train, score (`geo_*`).
- **RandLoRA** (arXiv:2502.00987): bases, scale, train, score (`rlo_*`).
- Harness: `geo_rlo_shaped_report`. MCP +12 → **1583**.

### Docs
- PRD / TECH_SPEC **v16.0.0** (UC-1583–1593). ROADMAP Phase 156. Frontiers §§336–337.

## [15.9.0] — 2026-08-21

### Added
- **OPLoRA** (arXiv:2510.13003): proj, constrain, train, score (`opl_*`).
- **GeLoRA** (arXiv:2412.09250): idim, rank, train, score (`gel_*`).
- Harness: `opl_gel_shaped_report`. MCP +12 → **1571**.

### Docs
- PRD / TECH_SPEC **v15.9.0** (UC-1572–1582). ROADMAP Phase 155. Frontiers §§334–335.

## [15.8.0] — 2026-08-21

### Added
- **LoRA-drop** (arXiv:2402.07721): eval, keep, share, score (`ldr_*`).
- **VB-LoRA** (arXiv:2405.15179): bank, topk, compose, score (`vbl_*`).
- Harness: `ldr_vbl_shaped_report`. MCP +12 → **1559**.

### Docs
- PRD / TECH_SPEC **v15.8.0** (UC-1561–1571). ROADMAP Phase 154. Frontiers §§332–333.

## [15.7.0] — 2026-08-21

### Added
- **QPiSSA** (arXiv:2404.02948): quant, principal, train, score (`qps_*`).
- **MoSLoRA** (arXiv:2406.11909): split, mixer, train, score (`msl_*`).
- Harness: `qps_msl_shaped_report`. MCP +12 → **1547**.

### Docs
- PRD / TECH_SPEC **v15.7.0** (UC-1550–1560). ROADMAP Phase 153. Frontiers §§330–331.

## [15.6.0] — 2026-08-21

### Added
- **OLoRA** (arXiv:2406.01775): qr, ortho, train, score (`olr_*`).
- **LoRA-SP** (arXiv:2403.08822): select, freeze, train, score (`lsp_*`).
- Harness: `olr_lsp_shaped_report`. MCP +12 → **1535**.

### Docs
- PRD / TECH_SPEC **v15.6.0** (UC-1539–1549). ROADMAP Phase 152. Frontiers §§328–329.

## [15.5.0] — 2026-08-21

### Added
- **Delta-LoRA** (arXiv:2309.02411): adapters, delta, propagate, score (`dlo_*`).
- **LoRA-One** (arXiv:2502.01235): grad, align, train, score (`lon_*`).
- Harness: `dlo_lon_shaped_report`. MCP +12 → **1523**.

### Docs
- PRD / TECH_SPEC **v15.5.0** (UC-1528–1538). ROADMAP Phase 151. Frontiers §§326–327.

## [15.4.0] — 2026-08-21

### Added
- **LoftQ** (arXiv:2310.08659): quant, init, train, score (`lfq_*`).
- **LoRA-Dash** (arXiv:2409.01035): prelaunch, tsd, dash, score (`lds_*`).
- Harness: `lfq_lds_shaped_report`. MCP +12 → **1511**.

### Docs
- PRD / TECH_SPEC **v15.4.0** (UC-1517–1527). ROADMAP Phase 150. Frontiers §§324–325.

## [15.3.0] — 2026-08-21

### Added
- **MiLoRA** (arXiv:2406.09044): svd, minor, freeze, score (`mil_*`).
- **CorDA** (arXiv:2506.13187): cov, mode, adapt, score (`cda_*`).
- Harness: `mil_cda_shaped_report`. MCP +12 → **1499**.

### Docs
- PRD / TECH_SPEC **v15.3.0** (UC-1506–1516). ROADMAP Phase 149. Frontiers §§322–323.

## [15.2.0] — 2026-08-21

### Added
- **LoRA-Pro** (arXiv:2407.18242): equiv, adjust, train, score (`lpr_*`).
- **Kron-LoRA** (arXiv:2508.01961): kron, lora, train, score (`krl_*`).
- Harness: `lpr_krl_shaped_report`. MCP +12 → **1487**.

### Docs
- PRD / TECH_SPEC **v15.2.0** (UC-1495–1505). ROADMAP Phase 148. Frontiers §§320–321.

## [15.1.0] — 2026-08-21

### Added
- **SHiRA** (arXiv:2406.13175): mask, tune, switch, score (`shr_*`).
- **WaveFT** (arXiv:2505.12532): wave, sparse, idwt, score (`wft_*`).
- Harness: `shr_wft_shaped_report`. MCP +12 → **1475**.

### Docs
- PRD / TECH_SPEC **v15.1.0** (UC-1484–1494). ROADMAP Phase 147. Frontiers §§318–319.

## [15.0.0] — 2026-08-21

### Added
- **DropLoRA** (arXiv:2508.17337): rank, mask, train, score (`drl_*`).
- **GaLore** (arXiv:2403.03507): grad, project, step, score (`gal_*`).
- Harness: `drl_gal_shaped_report`. MCP +12 → **1463**.

### Docs
- PRD / TECH_SPEC **v15.0.0** (UC-1473–1483). ROADMAP Phase 146. Frontiers §§316–317.

## [14.9.0] — 2026-08-21

### Added
- **OFT/BOFT** (arXiv:2306.07280 / 2311.06243): ortho, butterfly, train, score (`oft_*`).
- **MiSS** (arXiv:2409.15371): shard, share, train, score (`mss_*`).
- Harness: `oft_mss_shaped_report`. MCP +12 → **1451**.

### Docs
- PRD / TECH_SPEC **v14.9.0** (UC-1462–1472). ROADMAP Phase 145. Frontiers §§314–315.

## [14.8.0] — 2026-08-21

### Added
- **Houlsby adapters** (arXiv:1902.00751): insert, freeze, train, score (`had_*`).
- **ReFT** (arXiv:2404.03592): repr, edit, train, score (`rft_*`).
- Harness: `had_rft_shaped_report`. MCP +12 → **1439**.

### Docs
- PRD / TECH_SPEC **v14.8.0** (UC-1451–1461). ROADMAP Phase 144. Frontiers §§312–313.

## [14.7.0] — 2026-08-21

### Added
- **LoHa** (arXiv:2108.06098): pair, hadamard, train, score (`lha_*`).
- **FourierFT** (arXiv:2405.03003): basis, coeff, idft, score (`fft_*`).
- Harness: `lha_fft_shaped_report`. MCP +12 → **1427**.

### Docs
- PRD / TECH_SPEC **v14.7.0** (UC-1440–1450). ROADMAP Phase 143. Frontiers §§310–311.

## [14.6.0] — 2026-08-21

### Added
- **rsLoRA** (arXiv:2312.03732): rank, scale, train, score (`rsl_*`).
- **LoKr** (arXiv:2309.14859): factors, kron, vectorize, score (`lkr_*`).
- Harness: `rsl_lkr_shaped_report`. MCP +12 → **1415**.

### Docs
- PRD / TECH_SPEC **v14.6.0** (UC-1429–1439). ROADMAP Phase 142. Frontiers §§308–309.

## [14.5.0] — 2026-08-21

### Added
- **LoRA-GA** (arXiv:2407.05000): grad, svd, scale, score (`lga_*`).
- **MoRA** (arXiv:2405.12130): square, compress, expand, score (`mor_*`).
- Harness: `lga_mor_shaped_report`. MCP +12 → **1403**.

### Docs
- PRD / TECH_SPEC **v14.5.0** (UC-1418–1428). ROADMAP Phase 141. Frontiers §§306–307.

## [14.4.0] — 2026-08-21

### Added
- **LoRA-XS** (arXiv:2405.17604): svd, r, train, score (`lxs_*`).
- **AsymmetryLoRA** (arXiv:2402.16842): role, freeze_a, train_b, score (`asy_*`).
- Harness: `lxs_asy_shaped_report`. MCP +12 → **1391**.

### Docs
- PRD / TECH_SPEC **v14.4.0** (UC-1407–1417). ROADMAP Phase 140. Frontiers §§304–305.

## [14.3.0] — 2026-08-21

### Added
- **LoRA-FA** (arXiv:2308.03303): freeze_a, train_b, merge, score (`lfa_*`).
- **DyLoRA** (arXiv:2210.07558): range, sample, select, score (`dyl_*`).
- Harness: `lfa_dyl_shaped_report`. MCP +12 → **1379**.

### Docs
- PRD / TECH_SPEC **v14.3.0** (UC-1395–1406). ROADMAP Phase 139. Frontiers §§302–303.

## [14.2.0] — 2026-08-21

### Added
- **Tied-LoRA** (arXiv:2311.09578): base, tie, train, score (`tlo_*`).
- **LoRA+** (arXiv:2402.12354): split, ratio, train, score (`lrp_*`).
- Harness: `tlo_lrp_shaped_report`. MCP +12 → **1367**.

### Docs
- PRD / TECH_SPEC **v14.2.0** (UC-1383–1394). ROADMAP Phase 138. Frontiers §§300–301.

## [14.1.0] — 2026-08-21

### Added
- **PiSSA** (arXiv:2404.02948): svd, principal, residual, score (`psa_*`).
- **Diff Pruning** (arXiv:2012.07463): diff, mask, prune, score (`dpr_*`).
- Harness: `psa_dpr_shaped_report`. MCP +12 → **1355**.

### Docs
- PRD / TECH_SPEC **v14.1.0** (UC-1371–1382). ROADMAP Phase 137. Frontiers §§298–299.

## [14.0.0] — 2026-08-21

### Added
- **VeRA** (arXiv:2310.11454): share, scale, train, score (`vra_*`).
- **AdapterDrop** (arXiv:2010.11918): insert, drop, infer, score (`adp_*`).
- Harness: `vra_adp_shaped_report`. MCP +12 → **1343**.

### Docs
- PRD / TECH_SPEC **v14.0.0** (UC-1359–1370). ROADMAP Phase 136. Frontiers §§296–297.

## [13.9.0] — 2026-08-21

### Added
- **QLoRA** (arXiv:2305.14314): quantize, nf4, adapter, score (`qlo_*`).
- **AdaLoRA** (arXiv:2303.10512): init, svd, prune, score (`adl_*`).
- Harness: `qlo_adl_shaped_report`. MCP +12 → **1331**.

### Docs
- PRD / TECH_SPEC **v13.9.0** (UC-1347–1358). ROADMAP Phase 135. Frontiers §§294–295.

## [13.8.0] — 2026-08-21

### Added
- **BitFit** (arXiv:2106.10199): freeze, bias, train, score (`bft_*`).
- **DoRA** (arXiv:2402.09353): decompose, magnitude, direction, score (`dora_*`).
- Harness: `bft_dora_shaped_report`. MCP +12 → **1319**.

### Docs
- PRD / TECH_SPEC **v13.8.0** (UC-1335–1346). ROADMAP Phase 134. Frontiers §§292–293.

## [13.7.0] — 2026-08-21

### Added
- **Compacter** (arXiv:2106.04647): insert, kronecker, train, score (`cmp_*`).
- **(IA)^3** (arXiv:2205.05638): vector, scale, train, score (`ia3_*`).
- Harness: `cmp_ia3_shaped_report`. MCP +12 → **1307**.

### Docs
- PRD / TECH_SPEC **v13.7.0** (UC-1323–1334). ROADMAP Phase 133. Frontiers §§290–291.

## [13.6.0] — 2026-08-21

### Added
- **LoRA** (arXiv:2106.09685): freeze, rank, train, merge (`lora_*`).
- **AdapterFusion** (arXiv:2005.00247): extract, compose, attend, score (`adf_*`).
- Harness: `lora_adf_shaped_report`. MCP +12 → **1295**.

### Docs
- PRD / TECH_SPEC **v13.6.0** (UC-1311–1322). ROADMAP Phase 132. Frontiers §§288–289.

## [13.5.0] — 2026-08-21

### Added
- **ATTEMPT** (arXiv:2205.11961): source, target, attend, mix (`atm_*`).
- **Multitask Prompt Tuning** (arXiv:2303.02861): shared, factor, transfer, score (`mptp_*`).
- Harness: `atm_mptp_shaped_report`. MCP +12 → **1283**.

### Docs
- PRD / TECH_SPEC **v13.5.0** (UC-1299–1310). ROADMAP Phase 131. Frontiers §§286–287.

## [13.4.0] — 2026-08-21

### Added
- **Soft Prompt Mixtures** (arXiv:2104.06599): soft, mix, ensemble, probe (`msp_*`).
- **SPoT** (arXiv:2110.07904): source, init, embed, retrieve (`spot_*`).
- Harness: `msp_spot_shaped_report`. MCP +12 → **1271**.

### Docs
- PRD / TECH_SPEC **v13.4.0** (UC-1287–1298). ROADMAP Phase 130. Frontiers §§284–285.

## [13.3.0] — 2026-08-21

### Added
- **P-Tuning v2** (arXiv:2110.07602): deep, inject, tune, seqtag (`ptv_*`).
- **Prompt Tuning** (arXiv:2104.08691): soft, prepend, optimize, scale (`ptl_*`).
- Harness: `ptv_ptl_shaped_report`. MCP +12 → **1259**.

### Docs
- PRD / TECH_SPEC **v13.3.0** (UC-1275–1286). ROADMAP Phase 129. Frontiers §§282–283.

## [13.2.0] — 2026-08-21

### Added
- **AutoPrompt** (arXiv:2010.15980): template, trigger, search, score (`aup_*`).
- **Prefix-Tuning** (arXiv:2101.00190): task, prefix, optimize, generate (`pfx_*`).
- Harness: `aup_pfx_shaped_report`. MCP +12 → **1247**.

### Docs
- PRD / TECH_SPEC **v13.2.0** (UC-1263–1274). ROADMAP Phase 128. Frontiers §§280–281.

## [13.1.0] — 2026-08-21

### Added
- **TEMPERA** (arXiv:2211.11890): state, act, reward, adapt (`tmpa_*`).
- **RLPrompt** (arXiv:2205.12548): init, sample, reward, update (`rlp_*`).
- Harness: `tmpa_rlp_shaped_report`. MCP +12 → **1235**.

### Docs
- PRD / TECH_SPEC **v13.1.0** (UC-1251–1262). ROADMAP Phase 127. Frontiers §§278–279.

## [13.0.0] — 2026-08-21

### Added
- **MAPO** (arXiv:2410.19499): posgrad, momentum, beam, ucb (`mapo_*`).
- **GrIPS** (arXiv:2203.07281): seed, edit, score, accept (`grips_*`).
- Harness: `mapo_grips_shaped_report`. MCP +12 → **1223**.

### Docs
- PRD / TECH_SPEC **v13.0.0** (UC-1239–1250). ROADMAP Phase 126. Frontiers §§276–277.

## [12.9.0] — 2026-08-21

### Added
- **ProTeGi** (arXiv:2305.03495): gradient, edit, beam, bandit (`ptg_*`).
- **PromptAgent** (arXiv:2310.16427): state, reflect, expand, backprop (`pag_*`).
- Harness: `ptg_pag_shaped_report`. MCP +12 → **1211**.

### Docs
- PRD / TECH_SPEC **v12.9.0** (UC-1227–1238). ROADMAP Phase 125. Frontiers §§274–275.

## [12.8.0] — 2026-08-21

### Added
- **OPRO** (arXiv:2309.03409): meta, propose, score, append (`opro_*`).
- **EvoPrompt** (arXiv:2309.08532): init, cross, mutate, select (`evp_*`).
- Harness: `opro_evp_shaped_report`. MCP +12 → **1199**.

### Docs
- PRD / TECH_SPEC **v12.8.0** (UC-1215–1226). ROADMAP Phase 124. Frontiers §§272–273.

## [12.7.0] — 2026-08-21

### Added
- **Automatic Prompt Engineer** (arXiv:2211.01910): propose, score, select, steer (`ape_*`).
- **Promptbreeder** (arXiv:2309.16797): init, mutate, fitness, diversity (`pbr_*`).
- Harness: `ape_pbr_shaped_report`. MCP +12 → **1187**.

### Docs
- PRD / TECH_SPEC **v12.7.0** (UC-1203–1214). ROADMAP Phase 123. Frontiers §§270–271.

## [12.6.0] — 2026-08-21

### Added
- **Hint-before-Solving** (arXiv:2402.14310): hint, solve, answer, compose (`hsp_*`).
- **EmotionPrompt** (arXiv:2307.11760): stimulus, append, run, truth (`emo_*`).
- Harness: `hsp_emo_shaped_report`. MCP +12 → **1175**.

### Docs
- PRD / TECH_SPEC **v12.6.0** (UC-1191–1202). ROADMAP Phase 122. Frontiers §§268–269.

## [12.5.0] — 2026-08-21

### Added
- **Self-Verification** (arXiv:2212.09561): forward, mask, repredict, score (`sve_*`).
- **Chain of Density** (arXiv:2309.04269): sparse, entities, fuse, length (`cod_*`).
- Harness: `sve_cod_shaped_report`. MCP +12 → **1163**.

### Docs
- PRD / TECH_SPEC **v12.5.0** (UC-1179–1190). ROADMAP Phase 121. Frontiers §§266–267.

## [12.4.0] — 2026-08-21

### Added
- **Chain-of-Verification** (arXiv:2309.11495): draft, plan, answer, final.
- **Verify-and-Edit** (arXiv:2305.03268): uncertain, search, edit, predict (`ved_*`).
- Harness: `cove_ved_shaped_report`. MCP +12 → **1151**.

### Docs
- PRD / TECH_SPEC **v12.4.0** (UC-1167–1178). ROADMAP Phase 120. Frontiers §§264–265.

## [12.3.0] — 2026-08-21

### Added
- **Tab-CoT** (arXiv:2305.17812): tabular 2D CoT header/row/infer/extract.
- **Everything of Thoughts / XoT** (arXiv:2311.04254): MCTS/revise/map proxies.
- Harness: `tabcot_xot_shaped_report`. MCP +12 → **1139**.

### Docs
- PRD / TECH_SPEC **v12.3.0** (UC-1155–1166). ROADMAP Phase 119. Frontiers §§262–263.

## [12.2.0] — 2026-08-21

### Added
- **System 2 Attention** (arXiv:2311.11829): regenerate, attend, respond, factuality.
- **Contrastive CoT** (arXiv:2311.09277): valid/invalid demos, contrast, reason (`ccot_*`).
- Harness: `s2a_ccot_shaped_report`. MCP +12 → **1127**.

### Docs
- PRD / TECH_SPEC **v12.2.0** (UC-1143–1154). ROADMAP Phase 118. Frontiers §§260–261.

## [12.1.0] — 2026-08-21

### Added
- **Thread of Thought** (arXiv:2311.08734): segment, analyze, select, synthesize.
- **Thought Propagation** (arXiv:2310.03965): propose, solve, reuse, amend (`tprop_*`).
- Harness: `thot_tprop_shaped_report`. MCP +12 → **1115**.

### Docs
- PRD / TECH_SPEC **v12.1.0** (UC-1131–1142). ROADMAP Phase 117. Frontiers §§258–259.

## [12.0.0] — 2026-08-21

### Added
- **Self-Refine** (arXiv:2303.17651): generate, feedback, refine, iterate.
- **Metacognitive Prompting** (arXiv:2308.05342): recognize, interpret, reevaluate, confidence.
- Harness: `sr_mcp_shaped_report`. MCP +12 → **1103**.

### Docs
- PRD / TECH_SPEC **v12.0.0** (UC-1119–1130). ROADMAP Phase 116. Frontiers §§256–257.

## [11.9.0] — 2026-08-21

### Added
- **Multimodal-CoT** (arXiv:2302.00923): fuse, rationale, infer (no vision I/O on core).
- **Maieutic Prompting** (arXiv:2205.11822): abduce, recurse, SAT, consistency.
- Harness: `mmcot_mai_shaped_report`. MCP +12 → **1091**.

### Docs
- PRD / TECH_SPEC **v11.9.0** (UC-1107–1118). ROADMAP Phase 115. Frontiers §§254–255.

## [11.8.0] — 2026-08-21

### Added
- **Complexity-Based Prompting** (arXiv:2210.00720): score, select, sample, vote complex chains.
- **Step-Back Prompting** (arXiv:2310.06117): abstract, principle, reason (≠ Least-to-Most).
- Harness: `cbp_sb_shaped_report`. MCP +12 → **1079**.

### Docs
- PRD / TECH_SPEC **v11.8.0** (UC-1095–1106). ROADMAP Phase 114. Frontiers §§252–253.

## [11.7.0] — 2026-08-21

### Added
- **Active-Prompt** (arXiv:2302.12246): sample, uncertainty, select, annotate (≠ Auto-CoT).
- **Analogical Prompting** (arXiv:2310.01714): recall, knowledge, solve without labels.
- Harness: `ap_ana_shaped_report`. MCP +12 → **1067**.

### Docs
- PRD / TECH_SPEC **v11.7.0** (UC-1083–1094). ROADMAP Phase 113. Frontiers §§250–251.

## [11.6.0] — 2026-08-21

### Added
- **Chameleon** (arXiv:2304.09842): inventory, plan, compose, execute (≠ HuggingGPT).
- **Recursion of Thought** (arXiv:2306.06891): trigger, divide, conquer, merge (≠ Least-to-Most).
- Harness: `cham_rot_shaped_report`. MCP +12 → **1055**.

### Docs
- PRD / TECH_SPEC **v11.6.0** (UC-1071–1082). ROADMAP Phase 112. Frontiers §§248–249.

## [11.5.0] — 2026-08-21

### Added
- **Auto-CoT** (arXiv:2210.03493): cluster, sample, generate demos automatically.
- **CAMEL** (arXiv:2303.17760): roles, inception, turns, society (≠ Multiagent Debate).
- Harness: `autocot_camel_shaped_report`. MCP +12 → **1043**.

### Docs
- PRD / TECH_SPEC **v11.5.0** (UC-1059–1070). ROADMAP Phase 111. Frontiers §§246–247.

## [11.4.0] — 2026-08-21

### Added
- **HuggingGPT** (arXiv:2303.17580): plan, select, execute, summarize across modalities.
- **Multiagent Debate** (arXiv:2305.14325): propose, debate, critique, converge (≠ Meta-Prompting).
- Harness: `hgpt_mad_shaped_report`. MCP +12 → **1031**.

### Docs
- PRD / TECH_SPEC **v11.4.0** (UC-1047–1058). ROADMAP Phase 110. Frontiers §§244–245.

## [11.3.0] — 2026-08-21

### Added
- **CRITIC** (arXiv:2305.11738): draft, tool critique, revise, iterate (≠ Reflexion).
- **Deductive Verification** (arXiv:2306.03872): Natural Program, step verify, unanimity.
- Harness: `critic_dv_shaped_report`. MCP +12 → **1019**.

### Docs
- PRD / TECH_SPEC **v11.3.0** (UC-1035–1046). ROADMAP Phase 109. Frontiers §§242–243.

## [11.2.0] — 2026-08-21

### Added
- **Voyager** (arXiv:2305.16291): curriculum, skill store/retrieve, self-verify, compose.
- **ReWOO** (arXiv:2305.18323): plan, worker, solver, decouple from observation (≠ ReAct).
- Harness: `voy_rewoo_shaped_report`. MCP +12 → **1007**.

### Docs
- PRD / TECH_SPEC **v11.2.0** (UC-1023–1034). ROADMAP Phase 108. Frontiers §§240–241.

## [11.1.0] — 2026-08-21

### Added
- **Faithful CoT** (arXiv:2301.13379): translate, deterministic solve, faithfulness.
- **LATS** (arXiv:2310.04406): expand, value, reflect, select with env feedback (≠ RAP).
- Harness: `fcot_lats_shaped_report`. MCP +12 → **995**.

### Docs
- PRD / TECH_SPEC **v11.1.0** (UC-1011–1022). ROADMAP Phase 107. Frontiers §§238–239.

## [11.0.0] — 2026-08-21

### Added
- **AgentCoder** (arXiv:2312.13010): programmer, test designer, executor, refine loop.
- **PAL** (arXiv:2211.10435): emit program, offload solve, read answer (≠ PoT).
- Harness: `ac_pal_shaped_report`. MCP +12 → **983**.

### Docs
- PRD / TECH_SPEC **v11.0.0** (UC-999–1010). ROADMAP Phase 106. Frontiers §§236–237.

## [10.9.0] — 2026-08-21

### Added
- **Plan-and-Solve** (arXiv:2305.04091): devise plan, execute, PS+ extract, calc guard.
- **Progressive-Hint Prompting** (arXiv:2304.09797): base answer, emit hint, reask, stable stop.
- Harness: `ps_php_shaped_report`. MCP +12 → **971**.

### Docs
- PRD / TECH_SPEC **v10.9.0** (UC-987–998). ROADMAP Phase 105. Frontiers §§234–235.

## [10.8.0] — 2026-08-21

### Added
- **STaR** (arXiv:2203.14465): generate, filter correct, rationalize, finetune proxy, bootstrap.
- **Cumulative Reasoning** (arXiv:2308.04371): propose, verify, accumulate, report, roles.
- Harness: `star_cr_shaped_report`. MCP +12 → **959**.

### Docs
- PRD / TECH_SPEC **v10.8.0** (UC-975–986). ROADMAP Phase 104. Frontiers §§232–233.

## [10.7.0] — 2026-08-21

### Added
- **Quiet-STaR** (arXiv:2403.09629): thought bounds, parallel sample, mix head, hard-token aid.
- **Decomposed Prompting** (arXiv:2210.02406): decompose, delegate, recurse, symbolic swap, library.
- Harness: `qs_dep_shaped_report`. MCP +12 → **947**.

### Docs
- PRD / TECH_SPEC **v10.7.0** (UC-963–974). ROADMAP Phase 103. Frontiers §§230–231.

## [10.6.0] — 2026-08-21

### Added
- **Self-Discover** (arXiv:2402.03620): select, adapt, implement, apply, compute ratio.
- **Meta-Prompting** (arXiv:2401.12954): break, assign expert, oversee, verify, task-agnostic.
- Harness: `sd_mp_shaped_report`. MCP +12 → **935**.

### Docs
- PRD / TECH_SPEC **v10.6.0** (UC-951–962). ROADMAP Phase 102. Frontiers §§228–229.

## [10.5.0] — 2026-08-21

### Added
- **Skeleton-of-Thought** (arXiv:2307.15337): skeleton, extract, parallel expand, router, latency.
- **Buffer of Thoughts** (arXiv:2406.04271): distill, retrieve, instantiate, buffer update, cost.
- Harness: `sot_bot_shaped_report`. MCP +12 → **923**.

### Docs
- PRD / TECH_SPEC **v10.5.0** (UC-939–950). ROADMAP Phase 101. Frontiers §§226–227.

## [10.4.0] — 2026-08-21

### Added
- **Algorithm of Thoughts** (arXiv:2308.10379): load algo, explore, tunnel, query budget.
- **Reasoning via Planning** (arXiv:2305.14992): world state, expand, reward, select, balance.
- Harness: `aot_rap_shaped_report`. MCP +12 → **911**.

### Docs
- PRD / TECH_SPEC **v10.4.0** (UC-927–938). ROADMAP Phase 100. Frontiers §§224–225.

## [10.3.0] — 2026-08-21

### Added
- **Graph of Thoughts** (arXiv:2308.09687): add, link, aggregate, feedback, score.
- **Program of Thoughts** (arXiv:2211.12588): emit program, sandbox proxy, read, self-consistency.
- Harness: `got_pot_shaped_report`. MCP +12 → **899**.

### Docs
- PRD / TECH_SPEC **v10.3.0** (UC-915–926). ROADMAP Phase 99. Frontiers §§222–223.

## [10.2.0] — 2026-08-21

### Added
- **Tree of Thoughts** (arXiv:2305.10601): propose, evaluate, expand, backtrack, select.
- **Least-to-Most** (arXiv:2205.10625): decompose, solve sub, carry forward, compose.
- Harness: `tot_ltm_shaped_report`. MCP +12 → **887**.

### Docs
- PRD / TECH_SPEC **v10.2.0** (UC-903–914). ROADMAP Phase 98. Frontiers §§220–221.

## [10.1.0] — 2026-08-21

### Added
- **Reflexion** (arXiv:2303.11366): trial, evaluate, verbal reflect, episodic store, next trial.
- **Self-Consistency** (arXiv:2203.11171): sample paths, collect, majority vote, marginalize.
- Harness: `reflexion_selfcons_shaped_report`. MCP +12 → **875**.

### Docs
- PRD / TECH_SPEC **v10.1.0** (UC-891–902). ROADMAP Phase 97. Frontiers §§218–219.

## [10.0.0] — 2026-08-21

### Added
- **Think-on-Graph** (arXiv:2307.07697): entity seed, explore, beam prune, path score, answer.
- **Toolformer** (arXiv:2302.04761): API candidate, filter, proxy execute, incorporate, demos.
- Harness: `tog_toolformer_shaped_report`. MCP +12 → **863**.

### Docs
- PRD / TECH_SPEC **v10.0.0** (UC-879–890). ROADMAP Phase 96. Frontiers §§216–217.

## [9.9.0] — 2026-08-21

### Added
- **Self-Ask** (arXiv:2210.04695): follow-up, search intercept, compose, stop, demos.
- **ReAct** (arXiv:2210.03629): thought, action, observe, finish, trajectory.
- Harness: `selfask_react_shaped_report`. MCP +12 → **851**.

### Docs
- PRD / TECH_SPEC **v9.9.0** (UC-867–878). ROADMAP Phase 95. Frontiers §§214–215.

## [9.8.0] — 2026-08-21

### Added
- **DSP** (arXiv:2212.14024): bootstrap demos, search, predict, compose program, multi-hop.
- **GenRead** (arXiv:2302.08468): generate context, optional ground, answer, compare, hybrid.
- Harness: `dsp_genread_shaped_report`. MCP +12 → **839**.

### Docs
- PRD / TECH_SPEC **v9.8.0** (UC-855–866). ROADMAP Phase 94. Frontiers §§212–213.

## [9.7.0] — 2026-08-21

### Added
- **PlanRAG** (arXiv:2406.12430): decision plan, analysis query, retrieve data, replan, decide.
- **Rewrite-Retrieve-Read** (arXiv:2305.14283): rewrite, retrieve, read, reader feedback, rewriter train plan.
- Harness: `planrag_rrr_shaped_report`. MCP +12 → **827**.

### Docs
- PRD / TECH_SPEC **v9.7.0** (UC-843–854). ROADMAP Phase 93. Frontiers §§210–211.

## [9.6.0] — 2026-08-21

### Added
- **REPLUG** (arXiv:2301.12652): retrieve, prepend, ensemble, LM-supervise retriever, black-box forward.
- **Iter-RetGen** (arXiv:2305.15294): generate→query→retrieve iterate, adapt plan.
- Harness: `replug_iterretgen_shaped_report`. MCP +12 → **815**.

### Docs
- PRD / TECH_SPEC **v9.6.0** (UC-831–842). ROADMAP Phase 92. Frontiers §§208–209.

## [9.5.0] — 2026-08-21

### Added
- **RQ-RAG** (arXiv:2404.00610): rewrite, decompose, disambiguate, refine mode, retrieve refined.
- **IRCoT** (arXiv:2212.10509): CoT step, guided retrieve, interleave, answer-ready, grounded check.
- Harness: `rqrag_ircot_shaped_report`. MCP +12 → **803**.

### Docs
- PRD / TECH_SPEC **v9.5.0** (UC-819–830). ROADMAP Phase 91. Frontiers §§206–207.

## [9.4.0] — 2026-08-20

### Added
- **GraphReader** (arXiv:2406.14550): build node, read/neighbors, note insight, reflect plan.
- **G-Retriever** (arXiv:2402.07630): node prize, PCST select proxy, subgraph, soft-prompt plan, highlight.
- Harness: `graphreader_gretriever_shaped_report`. MCP +12 → **791**.

### Docs
- PRD / TECH_SPEC **v9.4.0** (UC-807–818). ROADMAP Phase 90. Frontiers §§204–205.

## [9.3.0] — 2026-08-20

### Added
- **Adaptive-RAG** (arXiv:2403.14403): complexity classify, strategy select, no/single/multi-step paths.
- **FLARE** (arXiv:2305.06983): anticipate sentence, low-confidence gate, retrieve-for-regen, active step.
- Harness: `adaptiverag_flare_shaped_report`. MCP +12 → **779**.

### Docs
- PRD / TECH_SPEC **v9.3.0** (UC-795–806). ROADMAP Phase 89. Frontiers §§202–203.

## [9.2.0] — 2026-08-20

### Added
- **CRAG** (arXiv:2401.15884): retrieval evaluator actions, refine, web fallback plan, ambiguous blend.
- **HyDE** (arXiv:2212.10496): hypothetical doc, encode proxy, retrieve by hyp, hallucination filter, ground corpus.
- Harness: `crag_hyde_shaped_report`. MCP +12 → **767**.

### Docs
- PRD / TECH_SPEC **v9.2.0** (UC-783–794). ROADMAP Phase 88. Frontiers §§200–201.

## [9.1.0] — 2026-08-20

### Added
- **Self-RAG** (arXiv:2310.11511): on-demand retrieve decide, relevance/support/utility critique, select best continuation.
- **MemoBrain** (arXiv:2601.08079): dependency edges, prune invalid, fold sub-trajectories, flush under budget, salience keep.
- Harness: `selfrag_memobrain_shaped_report`. MCP +12 → **755**.

### Docs
- PRD / TECH_SPEC **v9.1.0** (UC-771–782). ROADMAP Phase 87. Frontiers §§198–199.

## [9.0.0] — 2026-08-20

### Added
- **MemoRAG** (arXiv:2409.05591): global memorize, clue/draft, clue-guided retrieve, dual memory/generator, generate plan.
- **PageIndex** (VectifyAI, 2025): TOC tree, natural sections, reasoning nav, select/prune, traceable path (vectorless).
- Harness: `memorag_pageindex_shaped_report`. MCP +12 → **743**.

### Docs
- PRD / TECH_SPEC **v9.0.0** (UC-759–770). ROADMAP Phase 86. Frontiers §§196–197.

## [8.9.0] — 2026-08-20

### Added
- **RAPTOR** (arXiv:2401.18059): embed/cluster/summarize tree, tree traverse, collapsed-tree retrieve.
- **LightRAG** (EMNLP 2025 Findings): entity/relation index, dual-level retrieve, incremental update, graph-vector fuse.
- Harness: `raptor_lightrag_shaped_report`. MCP +12 → **731**.

### Docs
- PRD / TECH_SPEC **v8.9.0** (UC-747–758). ROADMAP Phase 85. Frontiers §§194–195.

## [8.8.0] — 2026-08-20

### Added
- **MemWalker** (arXiv:2310.05029): segment, summary-tree nodes, navigate (child/revert), gather under budget, path gate.
- **MemGraphRAG** (arXiv:2606.00610): ontology/fact/passage layers, conflict detect/resolve plans, multilayer retrieve, PPR-style propagate.
- Harness: `memwalker_memgraphrag_shaped_report`. MCP +12 → **719**.

### Docs
- PRD / TECH_SPEC **v8.8.0** (UC-735–746). ROADMAP Phase 84. Frontiers §§192–193.

## [8.7.0] — 2026-08-20

### Added
- **AgeMem** (arXiv:2601.01885): unified LTM/STM tool actions — store, STM capacity, retrieve, summarize/discard plans.
- **MemGAS** (arXiv:2505.19549): multi-granularity units, cluster associate, entropy route, granularity select, filter plan.
- Harness: `agemem_memgas_shaped_report`. MCP +12 → **707**.

### Docs
- PRD / TECH_SPEC **v8.7.0** (UC-723–734). ROADMAP Phase 83. Frontiers §§190–191.

## [8.6.0] — 2026-08-20

### Added
- **MemoryBank** (arXiv:2305.10250): store/summon, personality synth, Ebbinghaus forget curve (report-only), reinforce.
- **RF-Mem** (arXiv:2603.09250): familiarity score, path route, top-K familiarity, recollection expand, alpha-mix.
- Harness: `memorybank_rfmem_shaped_report`. MCP +12 → **695**.

### Docs
- PRD / TECH_SPEC **v8.6.0** (UC-711–722). ROADMAP Phase 82. Frontiers §§188–189.

## [8.5.0] — 2026-08-20

### Added
- **VikingMem** (arXiv:2605.29640): event extract, entity update, timeline compress, time-weighted recall, rerank.
- **RecMem** (arXiv:2605.16045): subconscious buffer, recurrence gate, episodic consolidate, semantic refine, merge retrieve.
- Harness: `vikingmem_recmem_shaped_report`. MCP +12 → **683**.

### Docs
- PRD / TECH_SPEC **v8.5.0** (UC-699–710). ROADMAP Phase 81. Frontiers §§186–187.

## [8.4.0] — 2026-08-20

### Added
- **FluxMem** (arXiv:2605.28773): connect, feedback refine, consolidate, repair, prune, maturity gate.
- **QUMem** (arXiv:2608.16168): episode segment, typed decompose, multi-query plan, user-state infer, temporal validity.
- Harness: `fluxmem_qumem_shaped_report`. MCP +13 → **671**.

### Docs
- PRD / TECH_SPEC **v8.4.0** (UC-686–698). ROADMAP Phase 80. Frontiers §§184–185.

## [8.3.0] — 2026-08-20

### Added
- **MemGPT** (arXiv:2310.08560): main-context capacity, page-out/in, recall + archival search, loop plan (distinct from MemoryOS).
- **RippleMem** (arXiv:2608.13334): episodic units, entity links, seed retrieve, associative expand, recollect gate.
- Harness: `memgpt_ripple_shaped_report`. MCP +12 → **658**.

### Docs
- PRD / TECH_SPEC **v8.3.0** (UC-674–685). ROADMAP Phase 79. Frontiers §§182–183.

## [8.2.0] — 2026-08-20

### Added
- **Memanto** (arXiv:2604.22085): typed categories, conflict resolve, versioning, single-query retrieve, latency gate.
- **Zep/Graphiti** (arXiv:2501.13956): episodes, entity links, bi-temporal stamps, convo+business synthesize, cross-session.
- Harness: `memanto_zep_shaped_report`. MCP +12 → **646**.

### Docs
- PRD / TECH_SPEC **v8.2.0** (UC-662–673). ROADMAP Phase 78. Frontiers §§180–181.

## [8.1.0] — 2026-08-20

### Added
- **O-Mem** (arXiv:2511.13593): persona/event profiling, hierarchical retrieve, profile gate, memory-time density.
- **Mandol** (arXiv:2606.29778): basic→abstract agglomeration, SemanticMap, hybrid retrieve, query route, token budget.
- Harness: `omem_mandol_shaped_report`. MCP +13 → **634**.

### Docs
- PRD / TECH_SPEC **v8.1.0** (UC-649–661). ROADMAP Phase 77. Frontiers §§178–179.

## [8.0.0] — 2026-08-20

### Added
- **MemEngine** (arXiv:2505.02099): function/operation/model stack, config, reflect, pluggable gate.
- **SimpleMem** (arXiv:2601.02553): compress, synthesize, intent-aware depth, multiview index, token ratio.
- Harness: `memengine_simplemem_shaped_report`. MCP +13 → **621**.

### Docs
- PRD / TECH_SPEC **v8.0.0** (UC-636–648). ROADMAP Phase 76. Frontiers §§176–177.

## [7.9.0] — 2026-08-20

### Added
- **CMA** (arXiv:2601.09913): persist, selective retain, associative route, temporal chain, consolidate, probe gates.
- **AgentFold** (arXiv:2510.24699): workspace split, fold commands, granular/deep condense, context budget.
- Harness: `cma_agentfold_shaped_report`. MCP +13 → **608**.

### Docs
- PRD / TECH_SPEC **v7.9.0** (UC-623–635). ROADMAP Phase 75. Frontiers §§174–175.

## [7.8.0] — 2026-08-20

### Added
- **MemOS** (arXiv:2507.03724): MemCube create/schedule/lifecycle/compose/migrate/fuse.
- **SkillCraft** (arXiv:2603.00718): Skill Mode save/get/list/execute + verifier + token-efficiency proxy.
- Harness: `memos_skillcraft_shaped_report`. MCP +14 → **595**.

### Docs
- PRD / TECH_SPEC **v7.8.0** (UC-609–622). ROADMAP Phase 74. Frontiers §§172–173.

## [7.7.0] — 2026-08-20

### Added
- **HyperSkill** (arXiv:2608.16114): hypergraph subtask/skill nodes, dual-path retrieve, co-occurrence rank, maintain plans.
- **DCPM** (arXiv:2606.09483): day/night dual-process, supersedes chains, cross-domain collision → core schema.
- Harness: `hyperskill_dcpm_shaped_report`. MCP +13 → **581**.

### Docs
- PRD / TECH_SPEC **v7.7.0** (UC-596–608). ROADMAP Phase 73. Frontiers §§170–171.

## [7.6.0] — 2026-08-20

### Added
- **HiMem** (arXiv:2601.06377): episode/note hierarchy, hybrid/best-effort retrieve, conflict-aware reconsolidation.
- **H-MEM levels** (arXiv:2507.22925): four-level index routing (`hmeml_*`); distinct from hybrid H-Mem.
- Harness: `himem_hmeml_shaped_report`. MCP +12 → **568**.

### Docs
- PRD / TECH_SPEC **v7.6.0** (UC-584–595). ROADMAP Phase 72. Frontiers §§168–169.

## [7.5.0] — 2026-08-20

### Added

- **SMITH** (arXiv:2512.11303) — `smith_store_memory` / `smith_create_tool` / `smith_retrieve_episode` / `smith_curriculum_difficulty` / `smith_tool_reuse_gate` / `smith_loop_plan`.
- **H-Mem** (arXiv:2605.15701) — `hmem_leaf_event` / `hmem_consolidate_nodes` / `hmem_link_entities` / `hmem_decompose_query` / `hmem_hybrid_retrieve` / `hmem_evolution_gate`.
- **`smith_hmem_shaped_report`** harness.
- MCP tools → **556**; CLI: `smith-store`, `smith-tool`, `smith-episode`, `smith-curriculum`, `smith-reuse`, `smith-loop`, `hmem-leaf`, `hmem-consolidate`, `hmem-link`, `hmem-decompose`, `hmem-hybrid`, `hmem-evolution`.
- Research frontiers §§166–167.

### Docs

- PRD / TECH_SPEC **v7.5.0** (UC-572–583). ROADMAP Phase 71.

### Tests

- `test_v750_features.py`

## [7.4.0] — 2026-08-20

### Added

- **Socratic-Zero** (arXiv:2509.24726) — `socratic_teacher_craft` / `socratic_solver_preference` / `socratic_generator_distill` / `socratic_seed_bootstrap` / `socratic_weakness_target` / `socratic_closed_loop`.
- **SPIRAL** (arXiv:2506.24119) — `spiral_self_play_match` / `spiral_rae_advantage` / `spiral_baseline_ema` / `spiral_transfer_pattern` / `spiral_opponent_strength` / `spiral_multi_game_plan`.
- **`socratic_spiral_shaped_report`** harness.
- MCP tools → **544**; CLI: `socratic-teach`, `socratic-prefer`, `socratic-distill`, `socratic-seed`, `socratic-weakness`, `socratic-loop`, `spiral-match`, `spiral-rae`, `spiral-ema`, `spiral-pattern`, `spiral-opponent`, `spiral-plan`.
- Research frontiers §§164–165.

### Docs

- PRD / TECH_SPEC **v7.4.0** (UC-560–571). ROADMAP Phase 70.

### Tests

- `test_v740_features.py`

## [7.3.0] — 2026-08-20

### Added

- **SAMULE** (arXiv:2509.20562) — `single_trajectory_reflect` / `intra_task_taxonomy` / `inter_task_transfer` / `foresight_reflect` / `failure_centric_gate` / `merge_reflections`.
- **LIVE-EVO** (arXiv:2602.02369) — `experience_bank_record` / `meta_guideline_record` / `compile_task_guideline` / `update_experience_weight` / `forget_stale_experience` / `liveevo_online_round`.
- **`samule_liveevo_shaped_report`** harness.
- MCP tools → **532**; CLI: `samule-micro`, `samule-meso`, `samule-macro`, `samule-foresight`, `samule-fail-gate`, `samule-merge`, `liveevo-exp`, `liveevo-meta`, `liveevo-compile`, `liveevo-weight`, `liveevo-forget`, `liveevo-round`.
- Research frontiers §§162–163.

### Docs

- PRD / TECH_SPEC **v7.3.0** (UC-548–559). ROADMAP Phase 69.

### Tests

- `test_v730_features.py`

## [7.2.0] — 2026-08-20

### Added

- **MemGen** (arXiv:2509.24704) — `memory_trigger_decide` / `weave_latent_memory` / `interweave_cycle_plan` / `faculty_classify` / `weaver_only_update_gate` / `sparse_invoke_penalty`.
- **Metis** (arXiv:2606.24151) — `text_experience_store` / `crystallize_plan_to_tool` / `dual_retrieve` / `representation_tradeoff` / `promote_kind_gate` / `metis_loop_plan`.
- **`memgen_metis_shaped_report`** harness.
- MCP tools → **520**; CLI: `mem-trigger`, `weave-latent`, `interweave`, `faculty`, `weaver-gate`, `sparse-invoke`, `text-experience`, `crystallize`, `dual-retrieve`, `rep-tradeoff`, `promote-kind`, `metis-loop`.
- Research frontiers §§160–161.

### Docs

- PRD / TECH_SPEC **v7.2.0** (UC-536–547). ROADMAP Phase 68.

### Tests

- `test_v720_features.py`

## [7.1.0] — 2026-08-20

### Added

- **Multi-Agent Evolve / MAE** (arXiv:2510.23595) — `mae_propose_question` / `mae_solve_attempt` / `mae_judge_score` / `mae_proposer_reward` / `mae_quality_filter` / `mae_triad_round_plan`.
- **SAGE** (arXiv:2603.15255) — `sage_challenge_task` / `sage_plan_steps` / `sage_solve_with_plan` / `sage_critic_filter` / `sage_drift_gate` / `sage_closed_loop_round`.
- **`mae_sagema_shaped_report`** harness.
- MCP tools → **508**; CLI: `mae-propose`, `mae-solve`, `mae-judge`, `mae-proposer-reward`, `mae-quality-filter`, `mae-triad`, `sage-challenge`, `sage-plan`, `sage-solve`, `sage-critic`, `sage-drift`, `sage-loop`.
- Research frontiers §§158–159.

### Docs

- PRD / TECH_SPEC **v7.1.0** (UC-524–535). ROADMAP Phase 67.

### Tests

- `test_v710_features.py`

## [7.0.0] — 2026-08-20

### Added

- **ECHO** (arXiv:2606.31650) — `write_turn_memory` / `select_turn_memories` / `reconstruct_policy_context` / `provenance_credit_mask` / `history_collapse_gate` / `budget_binding_check`.
- **Agent0** (arXiv:2511.16043) — `curriculum_propose_task` / `tool_use_reward` / `curriculum_reward` / `executor_frontier_filter` / `tool_aware_pressure` / `symbiotic_round_plan`.
- **`echomem_agent0_shaped_report`** harness.
- MCP tools → **496**; CLI: `write-turn-mem`, `select-turn-mem`, `reconstruct-ctx`, `credit-mask`, `collapse-gate`, `budget-binding`, `curriculum-task`, `tool-use-reward`, `curriculum-reward`, `executor-frontier`, `tool-pressure`, `symbiotic-round`.
- Research frontiers §§156–157.

### Docs

- PRD / TECH_SPEC **v7.0.0** (UC-512–523). ROADMAP Phase 66.

### Tests

- `test_v700_features.py`

## [6.9.0] — 2026-08-20

### Added

- **Absolute Zero / AZR** (arXiv:2505.03335) — `propose_reasoning_task` / `validate_task_structure` / `learnability_reward` / `solve_reward` / `abszero_joint_objective` / `executor_verify_gate`.
- **R-Zero** (arXiv:2508.05004) — `challenger_propose` / `uncertainty_reward` / `majority_vote_label` / `curriculum_band_filter` / `solver_binary_reward` / `coevolve_round_plan`.
- **`abszero_rzero_shaped_report`** harness.
- MCP tools → **484**; CLI: `propose-reason-task`, `validate-task-struct`, `learnability-reward`, `solve-reward`, `abszero-objective`, `executor-verify`, `challenger-propose`, `uncertainty-reward`, `majority-vote`, `curriculum-band`, `solver-reward`, `coevolve-round`.
- Research frontiers §§154–155.

### Docs

- PRD / TECH_SPEC **v6.9.0** (UC-500–511). ROADMAP Phase 65.

### Tests

- `test_v690_features.py`

## [6.8.0] — 2026-08-20

### Added

- **SkillWeaver** (arXiv:2504.07079) — `propose_skill` / `practice_skill_run` / `distill_skill_api` / `hone_skill_api` / `skill_library_register` / `transfer_skill_gate`.
- **SkillRoute / SAD** (arXiv:2606.18051) — `decompose_task_steps` / `retrieve_skills_for_steps` / `compose_skill_dag` / `sad_feedback_loop` / `granularity_match_check`.
- **`skillweaver_skillroute_shaped_report`** harness.
- MCP tools → **472**; CLI: `propose-skill`, `practice-skill`, `distill-skill-api`, `hone-skill-api`, `skill-library-reg`, `transfer-skill`, `decompose-task`, `retrieve-step-skills`, `compose-skill-dag`, `sad-loop`, `granularity-match`.
- Research frontiers §§152–153.

### Docs

- PRD / TECH_SPEC **v6.8.0** (UC-488–499). ROADMAP Phase 64.

### Tests

- `test_v680_features.py`

## [6.7.0] — 2026-08-20

### Added

- **EvolveR** (arXiv:2510.16079) — `distill_principle` / `principle_dedupe_plan` / `principle_metric_score` / `search_experience_action` / `lifecycle_phase_gate` / `prune_low_score_principles`.
- **AgentEvolver** (arXiv:2511.10395) — `self_question_task` / `experience_when_content` / `mixed_rollout_split` / `attribute_step_credit` / `curiosity_explore_plan`.
- **`evolver_agentevolver_shaped_report`** harness.
- MCP tools → **461**; CLI: `distill-principle`, `principle-dedupe`, `principle-score`, `search-exp-action`, `lifecycle-phase`, `prune-principles`, `self-question`, `exp-when-content`, `mixed-rollout`, `attribute-credit`, `curiosity-explore`.
- Research frontiers §§150–151.

### Docs

- PRD / TECH_SPEC **v6.7.0** (UC-476–487). ROADMAP Phase 63.

### Tests

- `test_v670_features.py`

## [6.6.0] — 2026-08-20

### Added

- **ProcMEM** (arXiv:2602.01869) — `define_skill_triplet` / `skill_select_gate` / `skill_terminate_check` / `semantic_gradient_candidate` / `ppo_gate_verify` / `skill_score_maintain`.
- **MemRL** (arXiv:2601.03192) — `ieu_record` / `two_phase_retrieve` / `utility_q_update` / `value_aware_select` / `semantic_vs_utility_warn`.
- **`procmem_memrl_shaped_report`** harness.
- MCP tools → **450**; CLI: `define-skill`, `skill-select`, `skill-terminate`, `semantic-gradient`, `ppo-gate`, `skill-maintain`, `ieu-record`, `two-phase-retrieve`, `utility-q-update`, `value-aware-select`, `sim-util-warn`.
- Research frontiers §§148–149.

### Docs

- PRD / TECH_SPEC **v6.6.0** (UC-464–475). ROADMAP Phase 62.

### Tests

- `test_v660_features.py`

## [6.5.0] — 2026-08-20

### Added

- **PreFlect** (arXiv:2602.07187) — `distill_planning_error` / `prospective_critique_plan` / `revise_plan_proposal` / `replan_on_deviation` / `preflect_before_execute_gate`.
- **SkillFlow** (arXiv:2605.14089) — `orchestration_action_select` / `ttb_residual` / `step_importance` / `skill_marginal_flow` / `skill_curation_decide` / `phase_evolve_gate`.
- **`preflect_skillflow_shaped_report`** harness.
- MCP tools → **439**; CLI: `distill-planning-error`, `prospective-critique`, `revise-plan`, `replan-deviation`, `preflect-gate`, `orch-action`, `ttb-residual`, `step-importance`, `skill-marginal-flow`, `skill-curation`, `phase-evolve`.
- Research frontiers §§146–147.

### Docs

- PRD / TECH_SPEC **v6.5.0** (UC-452–463). ROADMAP Phase 61.

### Tests

- `test_v650_features.py`

## [6.4.0] — 2026-08-20

### Added

- **Mem-α** (arXiv:2509.25911) — `classify_memory_slot` / `memory_write_op` / `process_chunk_plan` / `compression_ratio` / `memalpha_reward_bundle` / `length_generalization_gate`.
- **AgentHER** (arXiv:2603.21357) — `classify_failure` / `extract_replay_outcome` / `hindsight_relabel_plan` / `multi_judge_accept` / `package_training_pair`.
- **`memalpha_agenther_shaped_report`** harness.
- MCP tools → **428**; CLI: `classify-memory-slot`, `memory-write-op`, `process-chunk`, `compression-ratio`, `memalpha-reward`, `length-gen-gate`, `classify-failure`, `replay-outcome`, `hindsight-relabel`, `multi-judge`, `package-training-pair`.
- Research frontiers §§144–145.

### Docs

- PRD / TECH_SPEC **v6.4.0** (UC-440–451). ROADMAP Phase 60.

### Tests

- `test_v640_features.py`

## [6.3.0] — 2026-08-20

### Added

- **Trace2Skill** (arXiv:2603.25158) — `collect_trajectory_label` / `propose_trajectory_patch` / `parallel_patch_pool` / `hierarchical_merge_patches` / `skill_mode_gate` / `prefer_parallel_over_sequential`.
- **Evo-Memory** (arXiv:2511.20857) — `streaming_task_append` / `exprag_retrieve` / `search_predict_evolve_check` / `evomem_refine_plan` / `evolution_similarity_hint`.
- **`trace2skill_evomemory_shaped_report`** harness.
- MCP tools → **417**; CLI: `collect-trajectory`, `propose-patch`, `parallel-patch-pool`, `merge-patches`, `skill-mode-gate`, `prefer-parallel`, `streaming-task-append`, `exprag-retrieve`, `spe-check`, `evomem-refine`, `evolution-similarity`.
- Research frontiers §§142–143.

### Docs

- PRD / TECH_SPEC **v6.3.0** (UC-428–439). ROADMAP Phase 59.

### Tests

- `test_v630_features.py`

## [6.2.0] — 2026-08-20

### Added

- **ExpeL** (arXiv:2308.10144) — `experience_pool_add` / `insight_op` / `insight_importance_gate` / `retrieve_insights` / `retrieve_similar_successes`.
- **RMM dialogue** (arXiv:2503.08026) — `prospective_reflect` / `topic_memory_bank` / `retrieve_topic_memories` / `retrospective_cite_feedback` / `rerank_memories` / `retrieval_refine_plan`.
- **`expel_rmm_shaped_report`** harness.
- MCP tools → **406**; CLI: `experience-pool-add`, `insight-op`, `insight-importance-gate`, `retrieve-insights`, `retrieve-similar-successes`, `prospective-reflect`, `topic-memory-bank`, `retrieve-topic-memories`, `retrospective-cite`, `rerank-memories`, `retrieval-refine`.
- Research frontiers §§140–141.

### Docs

- PRD / TECH_SPEC **v6.2.0** (UC-416–427). ROADMAP Phase 58.

### Tests

- `test_v620_features.py`

## [6.1.0] — 2026-08-20

### Added

- **ReMe** (arXiv:2512.10696) — `multi_faceted_distill` / `scenario_retrieve` / `adaptive_rewrite_plan` / `utility_after_reuse` / `selective_add_plan` / `utility_prune_plan`.
- **Dynamic Cheatsheet** (arXiv:2504.07952) — `extract_cheatsheet_snippet` / `retrieve_cheatsheet` / `curator_decide` / `compact_memory_gate` / `dc_rs_order_check`.
- **`reme_cheatsheet_shaped_report`** harness.
- MCP tools → **395**; CLI: `multi-faceted-distill`, `scenario-retrieve`, `adaptive-rewrite`, `utility-after-reuse`, `selective-add`, `utility-prune`, `cheatsheet-snippet`, `retrieve-cheatsheet`, `curator-decide`, `compact-memory-gate`, `dc-rs-order`.
- Research frontiers §§138–139.

### Docs

- PRD / TECH_SPEC **v6.1.0** (UC-404–415). ROADMAP Phase 57.

### Tests

- `test_v610_features.py`

## [6.0.0] — 2026-08-20

### Added

- **Agent Workflow Memory (AWM)** (arXiv:2409.07429) — `induce_workflow` / `online_induce_gate` / `workflow_memory_add_plan` / `retrieve_workflows` / `workflow_step_budget`.
- **RRM** (arXiv:2607.28156) — `distill_retrieval_experience` / `anomaly_trigger` / `query_level_guidance` / `experience_lifecycle_score` / `prune_experience_plan` / `isolate_factual_from_procedural`.
- **`awm_rrm_shaped_report`** harness.
- MCP tools → **384**; CLI: `induce-workflow`, `online-induce-gate`, `workflow-add-plan`, `retrieve-workflows`, `workflow-step-budget`, `distill-retrieval-exp`, `anomaly-trigger`, `query-level-guidance`, `experience-lifecycle`, `prune-experience`, `isolate-factual`.
- Research frontiers §§136–137.

### Docs

- PRD / TECH_SPEC **v6.0.0** (UC-392–403). ROADMAP Phase 56.

### Tests

- `test_v600_features.py`

## [5.9.0] — 2026-08-20

### Added

- **G-Memory** (arXiv:2506.07398) — `classify_graph_tier` / `build_query_graph` / `upward_insight_traverse` / `downward_interaction_traverse` / `bidirectional_retrieve` / `hierarchy_update_plan`.
- **MemMA** (arXiv:2603.18718) — `meta_thinker_guidance` / `answerability_check` / `synthesize_probe_qa` / `verify_probes` / `repair_from_probes`.
- **`gmemory_memma_shaped_report`** harness.
- MCP tools → **373**; CLI: `graph-tier`, `query-graph`, `insight-up`, `interaction-down`, `bidir-retrieve`, `hierarchy-update`, `meta-thinker`, `answerability`, `probe-qa`, `verify-probes`, `repair-probes`.
- Research frontiers §§134–135.

### Docs

- PRD / TECH_SPEC **v5.9.0** (UC-380–391). ROADMAP Phase 55.

### Tests

- `test_v590_features.py`

## [5.8.0] — 2026-08-20

### Added

- **MemSkill** (arXiv:2602.02474) — `init_skill_bank` / `span_partition` / `select_skills` / `execute_skill_plan` / `record_hard_case` / `designer_evolve_plan`.
- **Memory-R1** (arXiv:2508.19828) — `classify_memory_op` / `noop_gate` / `memory_op_plan` / `conflict_update_plan` / `delete_stale_plan`.
- **`memskill_memoryr1_shaped_report`** harness.
- MCP tools → **362**; CLI: `skill-bank`, `span-partition`, `select-skills`, `execute-skills`, `hard-case`, `designer-evolve`, `memory-op`, `noop-gate`, `memory-op-plan`, `conflict-update`, `delete-stale`.
- Research frontiers §§132–133.

### Docs

- PRD / TECH_SPEC **v5.8.0** (UC-368–379). ROADMAP Phase 54.

### Tests

- `test_v580_features.py`

## [5.7.0] — 2026-08-20

### Added

- **Hindsight** (arXiv:2512.12818) — `classify_network` / `retain_plan` / `network_inventory` / `recall_multi_strategy` / `opinion_reinforce` / `reflect_plan`.
- **ReasoningBank** (arXiv:2509.25140) — `distill_strategy_item` / `failure_lesson_gate` / `retrieve_strategies` / `consolidate_strategy_plan` / `matts_contrastive_plan`.
- **`hindsight_reasoningbank_shaped_report`** harness.
- MCP tools → **351**; CLI: `classify-network`, `retain-plan`, `network-inventory`, `recall-multi`, `opinion-reinforce`, `reflect-plan`, `distill-strategy`, `failure-lesson-gate`, `matts-plan`.
- Research frontiers §§130–131.

### Docs

- PRD / TECH_SPEC **v5.7.0** (UC-357–367). ROADMAP Phase 53.

### Tests

- `test_v570_features.py`

## [5.6.0] — 2026-08-20

### Added

- **MemoryOS** (arXiv:2506.06326) — `classify_memory_tier` / `heat_score` / `segment_pages` / `stm_to_mtm_plan` / `mtm_evict_plan` / `promote_to_lpm_plan` / `hierarchical_retrieve`.
- **NEMORI** (ACL 2026) — `integrate_episodic_narrative` / `anticipatory_schema` / `prediction_error_distill` / `deserves_memory_gate` / `distill_batch_plan`.
- **`memoryos_nemori_shaped_report`** harness.
- MCP tools → **340**; CLI: `memory-tier`, `heat-score`, `segment-pages`, `stm-to-mtm`, `mtm-evict`, `promote-lpm`, `hier-retrieve`, `episodic-narrative`, `anticipatory-schema`, `prediction-error`, `deserves-memory`, `distill-batch`.
- Research frontiers §§128–129.

### Docs

- PRD / TECH_SPEC **v5.6.0** (UC-345–356). ROADMAP Phase 52.

### Tests

- `test_v560_features.py`

## [5.5.0] — 2026-08-20

### Added

- **REMem** (arXiv:2602.13530) — `extract_episodic_gist` / `extract_temporal_facts` / `situational_bind` / `build_hybrid_episodic_graph` / `agentic_retrieve_plan` / `ordinal_event_query`.
- **EverMemOS** (ACL 2026) — `form_memcell` / `consolidate_memscenes` / `foresight_filter` / `reconstructive_recollect` / `profile_evolve_plan` / `necessity_sufficiency_check`.
- **`remem_evermemos_shaped_report`** harness.
- MCP tools → **328**; CLI: `episodic-gist`, `temporal-facts`, `situational-bind`, `episodic-graph`, `agentic-retrieve`, `ordinal-event`, `memcell`, `memscenes`, `foresight-filter`, `recollect`, `profile-evolve`, `necessity-check`.
- Research frontiers §§126–127.

### Docs

- PRD / TECH_SPEC **v5.5.0** (UC-333–344). ROADMAP Phase 51.

### Tests

- `test_v550_features.py`

## [5.4.0] — 2026-08-20

### Added

- **PAMU** (arXiv:2510.09720) — `extract_preference_signal` / `fuse_preference` / `preference_change_detect` / `preference_update_plan` / `format_preference_prompt`.
- **BEAM-shaped eval** — `beam_category_inventory` / `classify_beam_query` / `knowledge_update_check` / `abstention_gate` / `contradiction_resolve_plan` / `event_order_check` / `beam_eval_pack`.
- **HaluMem stage localize** (arXiv:2511.03506) — `localize_hallucination_stage`.
- **`pamu_beam_shaped_report`** harness.
- MCP tools → **316**; CLI: `pref-signal`, `pref-update`, `pref-fuse`, `pref-change`, `pref-prompt`, `beam-categories`, `beam-classify`, `knowledge-update`, `abstention-gate`, `contradiction-plan`, `event-order`, `halu-stage`.
- Research frontiers §§123–125.

### Docs

- PRD / TECH_SPEC **v5.4.0** (UC-320–332). ROADMAP Phase 50.

### Tests

- `test_v540_features.py`

## [5.3.0] — 2026-08-20

### Added

- **MemEvolve / EvolveLab** (arXiv:2512.18746) — `list_design_space` / `architecture_profile` / `diagnose_architecture` / `propose_architecture_variants` / `rank_architecture_fitness` / `select_architecture_parents`.
- **MindMemOS** (arXiv:2608.12428) — `ept_classify` / `dreaming_consolidate_plan` / `feedback_revise_plan` / `skill_evolve_plan`.
- **MEMGUARD** (arXiv:2605.28009) — `functional_role_assign` / `contamination_scan` / `type_route_retrieve`.
- **`memevolve_mindmemos_shaped_report`** harness.
- MCP tools → **303**; CLI: `design-space`, `arch-profile`, `arch-diagnose`, `arch-variants`, `arch-rank`, `arch-parents`, `ept`, `functional-role`, `contamination-scan`, `type-route`, `dreaming-plan`, `feedback-revise`, `skill-evolve`.
- Research frontiers §§120–122.

### Docs

- PRD / TECH_SPEC **v5.3.0** (UC-307–319). ROADMAP Phase 49.

### Tests

- `test_v530_features.py`

## [5.2.0] — 2026-08-20

### Added

- **AgentDoG-shaped trajectory diagnostics** (arXiv:2601.18491) — `classify_risk_source` / `classify_failure_mode` / `classify_real_world_harm` / `diagnose_trajectory_step` / `diagnose_trajectory` / `safe_but_unreasonable_scan` / `taxonomy_inventory`.
- **MemWeaver-shaped hybrid weave** (arXiv:2601.18204) — `weave_layer_assign` / `build_hybrid_weave` / `dual_channel_retrieve` / `experience_abstract_plan` / `temporal_session_conflict_scan`.
- **MemHop-shaped hop depth** — `multi_hop_depth_score`.
- **`agentdog_memweaver_shaped_report`** harness.
- MCP tools → **290**; CLI: `risk-source`, `failure-mode`, `real-world-harm`, `diagnose-step`, `diagnose-trajectory`, `unreasonable-scan`, `taxonomy-inventory`, `weave-layer`, `hybrid-weave`, `dual-channel`, `experience-abstract`, `temporal-conflict`, `hop-depth`.
- Research frontiers §§117–119.

### Docs

- PRD / TECH_SPEC **v5.2.0** (UC-294–306). ROADMAP Phase 48.

### Tests

- `test_v520_features.py`

## [5.1.0] — 2026-08-20

### Added

- **PAM deepen** (arXiv:2605.11032) — `classify_memory_component` / `build_merkle_dag` / `verify_merkle_root` / `issue_capability_token` / `check_capability` / `selective_disclose` / `rehydrate_safe_plan`.
- **CapSeal-shaped action capabilities** (arXiv:2604.16762) — `issue_action_capability` / `capability_export_probe` / `check_action_capability` / `action_capability_inventory`.
- **`pam_capseal_shaped_report`** harness.
- MCP tools → **277**; CLI: `memory-component`, `merkle-dag`, `verify-merkle`, `issue-cap-token`, `check-cap-token`, `selective-disclose`, `rehydrate-safe`, `issue-action-cap`, `cap-export-probe`, `check-action-cap`.
- Research frontiers §§115–116.

### Docs

- PRD / TECH_SPEC **v5.1.0** (UC-282–293). ROADMAP Phase 47.

### Tests

- `test_v510_features.py`

## [5.0.0] — 2026-08-20

### Added

- **Knowledge-layer persistence semantics** (arXiv:2604.11364) — `classify_persistence_layer` / `persistence_policy` / `layer_inventory` / `knowledge_protect_scan` / `intelligence_reject_gate`.
- **Credential reject write gate** (MAPLE/PRISM-shaped) — `credential_scan` / `credential_reject_gate` / `credential_store_scan`.
- **Oblivion uncertainty retrieval** — `uncertainty_score` / `uncertainty_retrieve_gate` / `reasoning_reserve_plan`.
- **`knowledgelayer_cred_uncertainty_shaped_report`** harness.
- MCP tools → **266**; CLI: `persistence-layer`, `persistence-policy`, `layer-inventory`, `knowledge-protect`, `intelligence-reject`, `credential-scan`, `credential-reject`, `credential-store-scan`, `uncertainty-score`, `uncertainty-gate`, `reasoning-reserve`.
- Research frontiers §§112–114.

### Docs

- PRD / TECH_SPEC **v5.0.0** (UC-270–281). ROADMAP Phase 46.

### Tests

- `test_v500_features.py`

## [4.9.0] — 2026-08-20

### Added

- **MemPoison ladder** (arXiv:2607.14651) — `slot_coverage` / `threat_tier_classify` / `dormant_trigger_scan` / `mempoison_ladder_report`.
- **Salami / MemCollusion** (arXiv:2608.01637) — `compositional_coalition_scan` / `collusion_risk_gate` / `salami_pair_probe`.
- **`mempoison_salami_shaped_report`** harness.
- MCP tools → **255**; CLI: `slot-coverage`, `threat-tier`, `dormant-scan`, `coalition-scan`, `collusion-gate`, `mempoison-ladder`, `salami-pair`.
- Research frontiers §§110–111.

### Docs

- PRD / TECH_SPEC **v4.9.0** (UC-262–269). ROADMAP Phase 45.

### Tests

- `test_v490_features.py`

## [4.8.0] — 2026-08-20

### Added

- **Dependency-guided rollback repair** (arXiv:2608.10502) — `build_mem_action_graph` / `dependency_trace` / `preserve_independent` / `selective_replay_plan`.
- **MPBench write channels** (arXiv:2606.04329) — `classify_write_channel` / `source_isolation_gate` / `write_channel_inventory` / `channel_admit_batch`.
- **`deprepair_mpbench_shaped_report`** harness.
- MCP tools → **248**; CLI: `mem-action-graph`, `dependency-trace`, `preserve-independent`, `selective-replay`, `classify-write-channel`, `source-isolation`, `write-channel-inventory`, `channel-admit-batch`.
- Research frontiers §§108–109.

### Docs

- PRD / TECH_SPEC **v4.8.0** (UC-253–261). ROADMAP Phase 44.

### Tests

- `test_v480_features.py`

## [4.7.0] — 2026-08-20

### Added

- **MemSecBench** — `persistence_probe` / `execute_chain_probe` / `selective_repair_plan` / `lifecycle_report` (Write–Execute–Forget).
- **SleepGate** — `conflict_tag` / `forget_gate_plan` / `consolidate_survivors` / `pi_depth_scan` (proactive interference).
- **A-MemGuard** — `consensus_admit` (multi-channel retrieval admit).
- **`memsec_sleepgate_amemguard_shaped_report`** harness.
- MCP tools → **240**; CLI: `persistence-probe`, `execute-chain-probe`, `lifecycle-report`, `selective-repair`, `conflict-tag`, `forget-gate`, `consolidate-survivors`, `pi-depth`, `consensus-admit`.
- Research frontiers §§105–107.

### Docs

- PRD / TECH_SPEC **v4.7.0** (UC-244–252). ROADMAP Phase 43.

### Tests

- `test_v470_features.py`

## [4.6.0] — 2026-08-20

### Added

- **MemForest / MemTree** — `build_memtree` / `dirty_path_plan` / `coarse_to_fine` (hierarchical temporal index; localized dirty paths).
- **xMemory** — `build_themes` / `theme_attach` / `split_merge_plan` / `top_down_pack` (decouple→aggregate; expand under uncertainty).
- **`memforest_xmemory_shaped_report`** harness.
- MCP tools → **231**; CLI: `build-memtree`, `dirty-path`, `coarse-to-fine`, `build-themes`, `theme-attach`, `split-merge`, `top-down-pack`.
- Research frontiers §§102–104.

### Docs

- PRD / TECH_SPEC **v4.6.0** (UC-236–243). ROADMAP Phase 42.

### Tests

- `test_v460_features.py`

## [4.5.0] — 2026-08-20

### Added

- **TMA-NM** — `origin_bind` / `propagate_origin` / `launder_scan` / `act_authority_gate` (origin-bound authority; Sybil-resistant elevation).
- **AM-Sentry** — `save_policy` / `retrieval_screen` (GhostWriter two-stage defense).
- **`tmanm_amsentry_shaped_report`** harness.
- MCP tools → **224**; CLI: `origin-bind`, `propagate-origin`, `launder-scan`, `act-authority`, `save-policy`, `retrieval-screen`.
- Research frontiers §§99–101.

### Docs

- PRD / TECH_SPEC **v4.5.0** (UC-229–235). ROADMAP Phase 41.

### Tests

- `test_v450_features.py`

## [4.4.0] — 2026-08-20

### Added

- **TGMS** — `result_digest` / `operator_cost_estimate` / `plan_static_verify` / `claim_verify` / `summary_quarantine_scan`.
- **MemoryData** — `localized_maintenance_plan` / `maintenance_cost_compare` (O7 bound subset).
- **`tgms_memdata_shaped_report`** harness.
- MCP tools → **218**; CLI: `result-digest`, `operator-cost`, `plan-verify`, `claim-verify`, `summary-quarantine`, `local-maint`, `maint-cost`.
- Research frontiers §§96–98.

### Docs

- PRD / TECH_SPEC **v4.4.0** (UC-221–228). ROADMAP Phase 40.

### Tests

- `test_v440_features.py`

## [4.3.0] — 2026-08-20

### Added

- **SodaMem** — `density_fuse` / `evidence_plan` / `cited_pack` (density mass + mandatory citations).
- **MemRefine** — `compress_candidates` / `refine_plan` (storage-budget compress; no LLM judge).
- **AriadneMem / MemFuse** — `merge_link_add` / `bridge_discover` / `fuse_cluster`.
- **`sodamem_memrefine_ariadne_shaped_report`** harness.
- MCP tools → **211**; CLI: `density-fuse`, `evidence-plan`, `cited-pack`, `compress-candidates`, `refine-plan`, `merge-link-add`, `bridge-discover`, `fuse-cluster`.
- Research frontiers §§93–95.

### Docs

- PRD / TECH_SPEC **v4.3.0** (UC-212–220). ROADMAP Phase 39.

### Tests

- `test_v430_features.py`

## [4.2.0] — 2026-08-20

### Added

- **ConsistencyGate** — `support_score` / `consistency_admit` (lexical τ admission; no LLM votes).
- **MemGate** — `retrieval_admit` / `task_conditioned_pack` (query-conditioned hit admission).
- **Mnemonic sovereignty** — `sovereignty_checklist` / `post_delete_verify` / `rollback_plan`.
- **`consistency_memgate_sovereignty_shaped_report`** harness.
- MCP tools → **203**; CLI: `support-score`, `consistency-admit`, `retrieval-admit`, `task-pack`, `sovereignty-checklist`, `post-delete-verify`, `rollback-plan`.
- Research frontiers §§90–92.

### Docs

- PRD / TECH_SPEC **v4.2.0** (UC-203–211). ROADMAP Phase 38.

### Tests

- `test_v420_features.py`

## [4.1.0] — 2026-08-20

### Added

- **BudgetMem** — `query_complexity` / `budget_tier_route` / `budget_module_plan` (deterministic Low/Mid/High; no RL).
- **Skill library ranker** — `skill_rank` / `skill_prereq_expand` (lexical + LINK walk).
- **ERSkill** — `list_retrieval_primitives` / `list_retrieval_skills` / `compose_retrieval_skill` / `route_retrieval_skill` / `run_retrieval_skill`.
- **`budgetmem_erskill_shaped_report`** harness.
- MCP tools → **196**; CLI: `query-complexity`, `budget-tier-route`, `budget-module-plan`, `skill-rank`, `skill-prereq`, `retrieval-skills`, `route-retrieval-skill`, `run-retrieval-skill`.
- Research frontiers §§87–89.

### Docs

- PRD / TECH_SPEC **v4.1.0** (UC-193–202). ROADMAP Phase 37.

### Tests

- `test_v410_features.py`

## [4.0.0] — 2026-08-20

### Added

- **Deterministic freshness** — `extract_version_markers` / `freshness_resolve` / `assemble_current` / `hop_freshness` (arXiv:2606.01435 assembly thesis).
- **MemTxn deepen** — `patch_test` / `temporal_resolve` / `recover_active_map`.
- **Fleet propagation** — `fleet_scope_gate` / `propagate_plan` / `stale_propagation_scan`.
- **`freshness_memtxn_fleet_shaped_report`** harness.
- MCP tools → **186**; CLI: `version-markers`, `freshness-resolve`, `assemble-current`, `hop-freshness`, `patch-test`, `temporal-resolve`, `recover-active-map`, `fleet-scope-gate`, `propagate-plan`, `stale-propagation`.
- Research frontiers §§84–86.

### Docs

- PRD / TECH_SPEC **v4.0.0** (UC-183–192). ROADMAP Phase 36.

### Tests

- `test_v400_features.py`

## [3.9.0] — 2026-08-20

### Added

- **Governed Memory deepen** — `dual_project` / `governance_route` / `session_delta_*` / `entity_context` / `entity_leak_probe`.
- **HyMem** — `hymem_classify_slot` / `hymem_isolate_pack` (typed plan/execute/reason/memory isolation).
- **`govmem_hymem_shaped_report`** harness.
- MCP tools → **176**; CLI: `dual-project`, `governance-route`, `session-delta-*`, `entity-context`, `entity-leak-probe`, `hymem-slot`, `hymem-isolate`.
- Research frontiers §§81–83.

### Docs

- PRD / TECH_SPEC **v3.9.0** (UC-174–182). ROADMAP Phase 35.

### Tests

- `test_v390_features.py`

## [3.8.0] — 2026-08-20

### Added

- **ProGraph** — `extract_residuals` / `register_entities` / `profile_expand` / `residual_augment`.
- **EMG** — `match_correction` / `insight_inject` (report-only edit paths; never auto-rewrites SoT).
- **AgentIR** — `cascade_route` / `multi_channel_fuse` (lexical ± PPR ± residual RRF).
- **`prograph_emg_agentir_shaped_report`** harness.
- MCP tools → **167**; CLI: `residuals`, `entities`, `profile-expand`, `residual-augment`, `match-correction`, `insight-inject`, `cascade-route`, `multi-channel`.
- Research frontiers §§78–80.

### Docs

- PRD / TECH_SPEC **v3.8.0** (UC-166–173). ROADMAP Phase 34.

### Tests

- `test_v380_features.py`

## [3.7.0] — 2026-08-20

### Added

- **LightMem** — `sensory_filter` / `stage_inventory` / `topic_segments` / `stage_budget_plan`.
- **HippoRAG** — `ppr_scores` / `multi_hop_retrieve`.
- **Quipu + MAP-Graph risk** — `write_gate` / `action_risk_gate`.
- **`lightmem_hippo_quipu_shaped_report`** harness.
- MCP tools → **159**; CLI: `sensory-filter`, `stage-inventory`, `stage-budget`, `multi-hop`, `write-gate`, `action-risk-gate`.
- Research frontiers §§75–77.

### Docs

- PRD / TECH_SPEC **v3.7.0** (UC-159–165). ROADMAP Phase 33.

### Tests

- `test_v370_features.py`

## [3.6.0] — 2026-08-20

### Added

- **SCM** — `value_tag` / `wm_push` / `wm_list` / `wm_clear` / `sleep_trigger` / `sleep_plan` / `sleep_apply_nrem`.
- **GAM** — `episodic_buffer` / `semantic_boundary` / `consolidate_plan`.
- **ACM** — `anticipate` / `verify_compaction`.
- **`scm_gam_acm_shaped_report`** harness.
- MCP tools → **151**; CLI: `value-tag`, `wm-push`, `wm-list`, `sleep-plan`, `sleep-nrem`, `episodic-buffer`, `semantic-boundary`, `consolidate-plan`, `anticipate`, `verify-compaction`.
- Research frontiers §§72–74.

### Docs

- PRD / TECH_SPEC **v3.6.0** (UC-152–158). ROADMAP Phase 32.

### Tests

- `test_v360_features.py`

## [3.5.0] — 2026-08-20

### Added

- **Archive tier** — `archive_plan` / `archive_apply` / `unarchive` / `list_archived`; new state `archived` (out of Select; reversible).
- **SF-AMS CIS** — `composite_importance` / `cis_scan`.
- **MemCon control** — `control_suggest` (heuristic policy proxy).
- **`archive_sfams_memcon_shaped_report`** harness.
- MCP tools → **140**; CLI: `archive-plan`, `archive-apply`, `unarchive`, `cis`, `cis-scan`, `control-suggest`.
- Research frontiers §§69–71.

### Docs

- PRD / TECH_SPEC **v3.5.0** (UC-146–151). ROADMAP Phase 31.

### Tests

- `test_v350_features.py`

## [3.4.0] — 2026-08-20

### Added

- **FadeMem** — `fade_strength` / `fade_scan` / `fusion_candidates` (dual-layer decay; report-only fade; deterministic fusion plans).
- **SSGM Weibull** — `weibull_relevance` + Select `min_weibull` / `weibull_eta` / `weibull_kappa`.
- **MemR3** — `evidence_gap` / `reflective_retrieve` / `gap_tracker_update`.
- **`fademem_memr3_shaped_report`** harness.
- MCP tools → **133**; CLI: `fade-scan`, `fusion-candidates`, `weibull`, `evidence-gap`, `reflective-retrieve`.
- Research frontiers §§66–68.

### Docs

- PRD / TECH_SPEC **v3.4.0** (UC-140–145). ROADMAP Phase 30.

### Tests

- `test_v340_features.py`

## [3.3.0] — 2026-08-20

### Added

- **TierMem** — `put_raw_page` / `sufficiency_gate` / `escalate_raw` / `verified_writeback`.
- **MSCE** — `skill_eligibility` / `crystallize_skill` / `value_backfill` / `skill_catalog`.
- **`tiermem_msce_shaped_report`** harness.
- MCP tools → **127**; CLI: `put-raw`, `sufficiency`, `escalate-raw`, `writeback`, `crystallize-skill`, `skill-catalog`.
- Research frontiers §§64–65.

### Docs

- PRD / TECH_SPEC **v3.3.0** (UC-135–139). ROADMAP Phase 29.

### Tests

- `test_v330_features.py`

## [3.2.0] — 2026-08-20

### Added

- **Exact MemoRepair min-cut** — `repair_select_mincut` (Edmonds–Karp predecessor closure).
- **CUPMem adjudication** — `adjudicate_update` / `unknown_current_slots` / `authorize_retrieval`.
- **CMGL admit** — `admit_gate` / `list_admit_receipts` / `verify_admit_receipt`.
- **`memorepair_cupmem_cmgl_shaped_report`** harness.
- MCP tools → **120**; CLI: `repair-mincut`, `adjudicate`, `unknown-slots`, `authorize-retrieval`, `admit-gate`.
- Research frontiers §§61–63.

### Docs

- PRD / TECH_SPEC **v3.2.0** (UC-130–134). ROADMAP Phase 28.

### Tests

- `test_v320_features.py`

## [3.1.0] — 2026-08-20

### Added

- **StateFuse projection authority** — `project_resolve` / `pin_projection` / `clear_projection_pin` / `list_projection_pins` / `correction_handle`.
- **TOKI operator contract** — `toki_classify_operator` / `toki_anomaly_scan`.
- **MemArchitect triage & bid** — `context_bid`.
- **`statefuse_toki_shaped_report`** harness.
- MCP tools → **114**; CLI: `project-resolve`, `correction-handle`, `pin-projection`, `toki-classify`, `toki-anomalies`, `context-bid`.
- Research frontiers §§58–60.

### Docs

- PRD / TECH_SPEC **v3.1.0** (UC-125–129). ROADMAP Phase 27.

### Tests

- `test_v310_features.py`

## [3.0.0] — 2026-08-20

### Added

- **STALE-shaped probes** — `state_resolution` / `premise_resistance` / `ipa_gap_scan` / `related_slot_scan`.
- **VTA-shaped** `verify_transition` (provenance + chronology).
- **GEM-shaped** `gem_report` six-condition checklist.
- **`stale_gem_shaped_report`** harness.
- MCP tools → **106**; CLI: `state-resolution`, `premise-resistance`, `verify-transition`, `related-slots`, `gem-report`.
- Research frontiers §§56–57.

### Docs

- PRD / TECH_SPEC **v3.0.0** (UC-120–124). ROADMAP Phase 26.

### Tests

- `test_v300_features.py`

## [2.9.0] — 2026-08-20

### Added

- **LatticeMind-shaped** `symbolic_conflict_scan` / `classify_conflict` / `compact_render` (reader character budget).
- **Cordon-shaped effect outbox** — `stage_effect` / `release_effects` / `mark_effect_dispatched` / `cancel_effect` / `compensate_effect` / `list_effects`.
- **`lattice_cordon_shaped_report`** harness.
- MCP tools → **100**; CLI: `symbolic-conflicts`, `classify-conflict`, `compact-render`, `stage-effect`, `list-effects`.
- Research frontiers §§54–55.

### Docs

- PRD / TECH_SPEC **v2.9.0** (UC-115–119). ROADMAP Phase 25.

### Tests

- `test_v290_features.py`

## [2.8.0] — 2026-08-20

### Added

- **MemTX-shaped belief transactions** — `begin_transaction` / `stage_write` / `validate_transaction` / `commit_transaction` / `abort_transaction` / `in_flight_report`.
- **`action_safe_gate`** — irreversible tools require promoted (action_safe) beliefs; blocks in-flight conflict_key overlap.
- **`aoep_report`** — Always-On AOEP-v0 shaped obligation checklist.
- **`memtx_aoep_shaped_report`** harness.
- MCP tools → **94**; CLI: `begin-tx`, `commit-tx`, `abort-tx`, `action-safe`, `in-flight`.
- Research frontiers §§52–53.

### Docs

- PRD / TECH_SPEC **v2.8.0** (UC-110–114). ROADMAP Phase 24.

### Tests

- `test_v280_features.py`

## [2.7.0] — 2026-08-20

### Added

- **TARL-shaped five-action updates** — `propose_update` / `apply_update` (`append|noop|revise|reject_conflict|defer_verify`) + `ledger_view`.
- **Memory Worth** — `memory_worth` / `low_worth_scan` / Select `min_worth` (associational; from `usage` counters).
- **`tarl_mw_shaped_report`** harness.
- MCP tools → **88**; CLI: `propose-update`, `apply-update`, `ledger-view`, `memory-worth`, `low-worth`.
- Research frontiers §§50–51.

### Docs

- PRD / TECH_SPEC **v2.7.0** (UC-105–109). ROADMAP Phase 23.

### Tests

- `test_v270_features.py`

## [2.6.0] — 2026-08-20

### Added

- **ChronoMem-shaped global versions** — `pin_memory_version` / `activate_version` / `active_version` / `counterfactual_search` (`refs/read_head`; `_version_select` surfaces later-superseded pinned ids).
- **MemStrata-shaped current-fact Select** — `exclude_superseded` / `stale_fact_scan` / `supersession_winners`.
- **`chronomem_strata_shaped_report`** harness.
- MCP tools → **83**; CLI: `pin-version`, `activate-version`, `stale-facts`.
- Research frontiers §§48–49.

### Docs

- PRD / TECH_SPEC **v2.6.0** (UC-100–104). ROADMAP Phase 22.

### Tests

- `test_v260_features.py`

## [2.5.0] — 2026-08-20

### Added

- **GitOfThoughts-shaped commit log** (`commits.ndjson` + refs/tags) — `commit_view` / `checkout_view` / `diff_commits` / `merge_branches` / `verify_commit_chain` (stdlib; no git binary).
- **`copyability_gate`** — Jaccard near-duplicate threshold (τ≈0.8 paper proxy) before trusting memory for accuracy.
- **`gitofthoughts_shaped_report`** harness.
- MCP tools → **79**; CLI: `commit`, `checkout`, `diff-commits`, `copyability`.
- Research frontiers §§46–47.

### Docs

- PRD / TECH_SPEC **v2.5.0** (UC-95–99). ROADMAP Phase 21.

### Tests

- `test_v250_features.py`

## [2.4.0] — 2026-08-20

### Added

- **MemIR-shaped typed roles** — optional `memory_role` (`evidence`|`claim`|`decision`); layer defaults; JSON Schema.
- **`fact_interface`** / **`role_collapse_scan`** — separate authorize set (claims+decisions only).
- **`claims_only` / `memory_roles` Select filters**; `claim_closure(..., require_claim_role=True)`.
- **D-Mem-shaped `quality_gate` + `dual_channel_search`** (routine claims-only → deliberation escalate).
- **`memir_dmem_shaped_report`** harness.
- MCP tools → **75**; CLI: `fact-interface`, `role-scan`, `dual-search`.
- Research frontiers §§44–45.

### Docs

- PRD / TECH_SPEC **v2.4.0** (UC-90–94). ROADMAP Phase 20.

### Tests

- `test_v240_features.py`

## [2.3.0] — 2026-08-20

### Added

- **MemoRepair-shaped cascade repair** — `cascade_impact` / `cascade_exposure` / `withdraw_cascade` (barrier-first) / `repair_plan` (predecessor-closed greedy) / `non_revival_probe`.
- **`memorepair_shaped_report`** harness.
- MCP tools → **71**; CLI: `cascade`, `withdraw-cascade`, `repair-plan`.
- Research frontiers §§42–43 (MemoRepair cascade, non-revival).

### Docs

- PRD / TECH_SPEC **v2.3.0** (UC-85–89). ROADMAP Phase 19.

### Tests

- `test_v230_features.py`

## [2.2.0] — 2026-08-20

### Added

- **PoEM-shaped execution ledger** (`executions.ndjson`) — `record_execution` / `verify_execution` / `verify_execution_chain`; memory wording never authorizes safety skips.
- **PPMF-shaped `authority_gate`** — non-amplification: action risk vs provenance authority (pack-hydrate capped).
- **GPM-shaped `claim_closure`** — exact promoted-fact closure at journal head.
- **`poem_ppmf_shaped_report`** harness.
- MCP tools → **67**; CLI: `record-exec`, `verify-exec`, `authority-gate`, `claim-closure`.
- Research frontiers §§39–41 (PoEM, PPMF, claim closure).

### Docs

- PRD / TECH_SPEC **v2.2.0** (UC-80–84). ROADMAP Phase 18.

### Tests

- `test_v220_features.py`

## [2.1.0] — 2026-08-20

### Added

- **Decision receipts** — GPM-shaped local records on successful `release_gate(..., issue_receipt=True)`; optional abstain audit via `record_abstain`.
- **`verify_import`** — PAM-shaped fail-closed import gate (structure → injection → count → policy → seal); `hydrate(..., require_verify=True)`.
- **Policy manifest** — export stamps `policy` / `policy_digest` + `policy_manifest.json`.
- **`lineage_trust`** + `search(..., refuse_untrusted_lineage=True)` — MemLineage-shaped Trusted / Derived-Untrusted / Untrusted.
- **`pam_cava_shaped_report`** harness.
- MCP tools → **63**; CLI: `verify-import`, `decisions`, `lineage-trust`, release-gate receipt flags.
- Research frontiers §§36–38.

### Docs

- PRD / TECH_SPEC **v2.1.0** (UC-75–79). ROADMAP Phase 17.

### Tests

- `test_v210_features.py`

## [2.0.0] — 2026-08-20

### Added

- **`health_report`** — unified doctor + journal chain + injection + seal head.
- **`release_gate`** — GPM-shaped fail-closed release; `export(..., require_release=True)`.
- **`cue_tags`** on entries + `search(..., cue_tags=)` associative filter.
- **Derived SQLite FTS index** (`rebuild_sqlite_index` / `search_sqlite`) — stdlib only; files remain SoT.
- **`gpm_release_shaped_report`** harness.
- MCP tools → **59**; CLI: `health`, `release-gate`, `rebuild-index`, `search-sqlite`.
- Research frontiers §§34–35 (GPM release, storage≠memory / derived index).

### Docs

- PRD / TECH_SPEC **v2.0.0** (UC-70–74). ROADMAP Phase 16.

### Tests

- `test_v200_features.py`

## [1.9.0] — 2026-08-20

### Added

- **Journal hash chain** — `prev_hash`/`row_hash` on new journal rows; `verify_journal_chain` / `journal_chain_head` (GPM-shaped).
- **`spread_activate`** — SYNAPSE-shaped spreading activation along LINKs.
- **`connection_density`** + `search(..., prefer_dense=True)` — SodaMem-shaped density ranking.
- **`retention_score`** + `search(..., min_retention=)` — Oblivion-shaped decay/retention gate.
- **`soda_synapse_shaped_report`** harness; module `activation.py`.
- MCP tools → **55**; CLI: `journal-chain`, `spread`, `density`, `retention`.
- Research frontiers §§30–33 (GPM, SYNAPSE, SodaMem, Oblivion).

### Docs

- PRD / TECH_SPEC **v1.9.0** (UC-65–69).

### Tests

- `test_v190_features.py`

## [1.8.0] — 2026-08-20

### Added

- **`blast_radius`** — LINK neighborhood within N hops (RippleMem/MAP-Graph shaped).
- **`merge_classify`** — MELD-shaped five-outcome classifier (insert/merge/relate/conflict/reject); report-only.
- **`path_trust`** + `search(..., min_path_trust=)` — multiplicative provenance path trust.
- **`meld_map_shaped_report`** harness.
- New module `graph.py` (deterministic; no LLM/NLI).
- MCP tools → **50**; CLI: `blast`, `merge-classify`, `path-trust`.
- Research frontiers §§27–29 (MELD, MAP-Graph, RippleMem).

### Docs

- PRD / TECH_SPEC **v1.8.0** (UC-60–64).

### Tests

- `test_v180_features.py`

## [1.7.0] — 2026-08-20

### Added

- **`lifecycle_tier` / `lifecycle_inventory`** + `search(..., lifecycle_tiers=)` — AMV-L-shaped HOT/WARM/COLD eligibility.
- **`conflict_key` + `revoke_by_key` / `unrevoke`** — TEPA-shaped keyed revoke (new state `revoked`; history retained).
- **`pack_seal` / `verify_pack_seal`** — tamper-evident seals for exported packs.
- **`search_explain`** — SEARCH with channel `rank_detail` (lexical/RRF).
- **`tepa_amvl_shaped_report`** harness.
- MCP tools → **47**; CLI: `lifecycle`, `revoke-key`, `pack-seal`, `verify-pack-seal`, `explain`.
- Research frontiers §§24–26 (AMV-L, TEPA, pack attestation).

### Docs

- PRD / TECH_SPEC **v1.7.0** (UC-55–59).

### Tests

- `test_v170_features.py`

## [1.6.0] — 2026-08-20

### Added

- **`store_seal` / `verify_seal`** — tamper-evident content+journal seal (MemMark R3-adjacent).
- **`attribution_receipt`** — per-entry content digest + journal binding.
- **`replay_consistency`** — journal↔SoT soft check; PURGE retains `removed` ids.
- **`entry_content_digest`** helper in `integrity.py`.
- **`memmark_shaped_report`** — seal/receipt/tamper/replay proxies.
- MCP: `stele_store_seal`, `stele_verify_seal`, `stele_attribution_receipt`, `stele_replay_consistency` (**41 tools**).
- CLI: `seal`, `verify-seal`, `receipt`, `replay-check`.
- Research frontiers §§22–23 (MemMark, TRACE).

### Docs

- PRD / TECH_SPEC **v1.6.0** (UC-51–54).

### Tests

- `test_v160_features.py`

## [1.5.0] — 2026-08-20

### Added

- **`injection_scan`** + `risk.py` — deterministic injection-marker scan (MIND-inspired; no LLM).
- **`search(..., withhold_injection_suspects=)`** — MAPLE retrieval gate.
- **`promote(..., block_injection_suspects=)`** — MAPLE promote gate.
- **`select_budget_plan`** — Compress-plane fitted vs overflow.
- **`maple_shaped_report`** — write/retrieve/promote lifecycle gate proxies.
- MCP: `stele_injection_scan`, `stele_select_budget_plan` (**37 tools**).
- CLI: `stele injection-scan`, `stele budget-plan`.
- Research frontiers §§20–21 (MIND, MAPLE-Guard).

### Docs

- PRD / TECH_SPEC **v1.5.0** (UC-48–50).

### Tests

- `test_v150_features.py`

## [1.4.0] — 2026-08-20

### Added

- **`lineage`** — supersede chain + journal (TOKI audit-erasure defence).
- **`belief_at`** — bi-temporal point-in-time SEARCH or inventory.
- **`conflict_surface`** — contested pairs preserved (StateFuse; no auto-collapse).
- **`memoryagent_shaped_report`** — four-competency local CI proxies.
- MCP: `stele_lineage`, `stele_belief_at`, `stele_conflict_surface` (**35 tools**).
- CLI: `stele lineage`, `stele belief-at`, `stele conflicts`.
- Research frontiers §§17–19 (TOKI, StateFuse, MemoryAgentBench).

### Docs

- PRD / TECH_SPEC **v1.4.0** (UC-44–47).

### Tests

- `test_v140_features.py`

## [1.3.0] — 2026-08-20

### Added

- **`search(..., principal_scopes=)`** — GateMem-shaped access control (explicit scope allowlist; no implicit universal).
- **`forget_compliance`** — post-erasure active-forgetting probe (store clear + SEARCH leak check).
- **`gatemem_shaped_report`** — utility ∩ ACL ∩ forgetting local CI proxies.
- MCP: `stele_forget_compliance` (**32 tools**); search gains `principal_scopes_json`.
- CLI: `stele forget-check`.
- Research frontiers §§14–16 (GateMem, governed shared memory, agent-native study).

### Docs

- PRD / TECH_SPEC **v1.3.0** (UC-41–43).

### Tests

- `test_v130_features.py`

## [1.2.0] — 2026-08-20

### Added

- **`entangled_suspects`** — LINK-neighborhood human-review queue after provenance poison (report only).
- **`hygiene_candidates`** — zombie / net-harm / stale-promoted triage (MemArchitect-aligned; no auto-delete).
- **`search(..., prefer_fresh=True)`** — SSGM-style soft rank by `last_verified`.
- **`governance_shaped_report`** — Layer-4 governance proxies for local CI.
- MCP: `stele_entangled_suspects`, `stele_hygiene_candidates` (**31 tools**); search gains `prefer_fresh` + `trusted_sources_json`.
- CLI: `stele hygiene`, `stele entangled`.
- Research frontiers §§11–13 (MemArchitect, SSGM, governance metrics).

### Docs

- PRD / TECH_SPEC **v1.2.0** (UC-38–40).

### Tests

- `test_v120_features.py`

## [1.1.0] — 2026-08-20

### Added

- **`purge_by_provenance`** — PurgeBench-aligned recovery (dry-run default).
- **`add_batch`** — atomic multi-ADD under one lock.
- **`diff_stores`** — compare live SoT to a snapshot/other root by entry id.
- **`search(..., trusted_sources=)`** — Select filter by provenance.source.
- **`membench_shaped_report`** — MemBench-shaped capacity/efficiency/effectiveness proxies.
- MCP: `stele_purge_by_provenance`, `stele_diff_stores`, `stele_add_batch` (29 tools).
- CLI: `stele purge`, `stele diff`.
- Research frontiers §§9–10 (MemBench, provenance recovery).

### Docs

- PRD / TECH_SPEC **v1.1.0** (UC-33–37).

### Tests

- `test_v110_features.py`

## [1.0.0] — 2026-08-20

### Added — v1.0 product bar

- **`stele` CLI** — `init · schema · verify · doctor · stats · snapshot · search · attach`.
- **`entry_json_schema()`** + `docs/schemas/entry.schema.json` (JSON Schema 2020-12).
- **`snapshot(dest)`** — cold-copy SoT (manifest, journal, entries, attachments).
- **`doctor()`** — verify + stats + contested + stale in one report.
- **memorywire projection** — `to_memorywire_remember` / `from_memorywire_recall_hits` (no dep).
- MCP: `stele_attach`, `stele_snapshot`, `stele_doctor`, `stele_entry_schema` (26 tools total).
- Research: `docs/research/GOVERNED_EXPERIENTIAL_MEMORY_FRONTIERS_2026.md`.
- Docs: PRD/TECH_SPEC **v1.0.0**, `docs/ARCHITECTURE.md`, patterns **v1.3**.

### Changed

- Package versions **1.0.0**; classifier Production/Stable.
- Intent status → **IMPLEMENTED — v1.0**.

### Tests

- `test_v100_features.py`; MCP tool AST gate; `proof_run.py` v1 gates.

## [0.1.7] — 2026-08-20

### Added

- **`stats()`** — store health dashboard (state/layer/scope counts).
- **`timeline(entry_id)`** — journal history per entry.
- **`attach(bytes)`** — content-addressed attachments + optional LINK.
- **`verify_pack()`** — offline C3 pack integrity.
- **`follow_link_depth` 1–3** — multi-hop LINK expansion on SEARCH.
- MCP: `stele_stats`, `stele_timeline`, `stele_verify_pack`.

### Docs

- **PRD v0.2.0** — expanded use cases UC-13–27, pains P13–P15, capability map vs alpha.
- **TECH_SPEC v0.2.0** — MCP §7 full tool table; retrieval/governance/hydrate aligned to alpha; UC index.

### Tests

- `test_v017_features.py`

## [0.1.6] — 2026-08-20

### Added — living ledger

- **`record_outcome(helpful|harmful|ignored)`** — reinforce on use; helpful refreshes `last_verified`.
- **`pin()`** — SEARCH prefers pinned + high-helpful lessons.
- **`match_reasons` + `body_max_chars`** — explainability + OP-9 compress on slices.
- **`stale_report()` / `reverify()`** — batch FF-8 freshness ops.
- **`related()`** — inbound/outbound LINK neighborhood.
- MCP tools for all of the above.

### Tests

- `test_v016_features.py`

## [0.1.5] — 2026-08-20

### Added

- **`judgment_entry()`** — wire-shape codified judgment → ADD (no foreign-framework import).
- **`memory_arena_smoke()`** — multi-family task-outcome suite (success_oracle shape).
- **`measure_search_overhead()`** — TECH_SPEC §10 cost/latency harness.
- MCP **`stele_export`**.
- **`examples/proof_run.py`** — end-to-end PASS/FAIL proof.

### Tests

- `test_v015_features.py`

## [0.1.4] — 2026-08-20

### Added

- **`consumer_model_id` / `model_policy`** on SEARCH — flag or withhold when lesson `provenance.model_id` differs (TECH_SPEC re-verify).
- **`follow_links=True`** — one-hop `kind=entry` expansion within budget (`via_link`, `linked_from`).
- Tests lock **REFLECT `dangling_links`** for missing entry refs.

### Tests

- `test_v014_features.py`

## [0.1.3] — 2026-08-20

### Added

- **`stale_policy`** on SEARCH — `flag` (default) or `withhold` (FF-8 abstention).
- **`reviewer_corrections(limit=)`** — bounded contested-first slice (C8 reviewer role).
- **`verify()`** — store integrity (dual-location, schema, journal parse).
- **`hydrate()` + `foreign_pack_transfer_eval()`** — scoped OP-12 pack → recipient lift.
- MCP: `stale_policy` on search; `stele_verify`, `stele_reviewer_corrections`, `stele_hydrate`.

### Tests

- `test_v013_features.py`

## [0.1.2] — 2026-08-20

### Added

- **`list_contested` / `resolve_contested`** — evidenced supersede for REFLECT conflicts (TECH_SPEC Q5 / R2); peer links via `contested_with`; authors cannot self-resolve.
- **Workflow env-gate harness family** — `workflow_env_gate_suite()` + `require_env_ok` on `LessonTask` (FF-4).
- MCP tools: `stele_list_contested`, `stele_resolve_contested`; search accepts `consumer_env_json`.

### Tests

- `test_contested_and_env_gate.py`

## [0.1.1] — 2026-08-20

### Added (research-driven)

- **Distill gate on ADD** (OP-2 / FF-2 / FF-3) — rejects transcripts, tool trajectories, equipment-heavy insight bodies.
- **Search `consumer_env`** (FF-4) — slices carry `env_assumptions`, `env_mismatch`, `missing_env_assumptions`.
- **Export subject allowlist + adaptation operators** (FF-7 / FF-9 / FF-13) — equipment lines → `re_derive`; `may_be_outdated` on manifest.
- **`migration_entry()` producer** (TECH_SPEC §8.3).
- **Task-outcome harness** (`LessonTask`, `compare_with_without`) — OP-12 / success_oracle shape (not recall QA).
- Empty SEARCH query returns ∅ (C2 / OP-9 Compress).

### Tests

- `test_research_features.py` covers distill, env mismatch, export allowlist, migration, harness lift.

## [0.1.0] — 2026-08-20

### Added

- **`stele-core`** — file-backed governed ledger (schema, store, governance, retrieval, export, receipt adapter). Zero runtime dependencies.
- **`stele-mcp`** — stdio MCP server with eight named tools.
- Constraint test suite (C1–C8 + joint lifecycle) and `examples/lifecycle_demo.py`.
- CI workflow, Makefile, workspace `pyproject.toml`.

### Fixed (intent validation pass)

- Writer cannot promote its own claim (C8).
- Domain scope via `consumer_domain` (C2 / TECH_SPEC §4.3).
- Staleness flags, as_of historical supersede, REFLECT provenance-preserving merge.
- Semantic index includes superseded for point-in-time search; embedder stays off write path.

## [0.1.6] — 2026-07-17

### Changed

Full cross-check of TECH_SPEC against PRD; PRD → v0.1.2, TECH_SPEC → v0.1.1.

- **Reconciled API signatures.** `search()` gained its resolved `consumer_scope`/`as_of` params in PRD (UC-3/UC-4, matching TECH_SPEC §6.1); `delete()` broadened in both docs to `subject_id | entry_id` — UC-5 now covers wrong-lesson single-entry erasure, not only subject erasure (intent OP-3/FF-9); `reflect()`'s report fields renamed to match TECH_SPEC's `conflicts[]`/`dangling_links[]`.
- **Reconciled the scope taxonomy.** PRD's UC-7 and FR table still described the intent's illustrative two-value enum (`universal_insight | project_scoped`) after TECH_SPEC had already resolved Q4 to three rungs (`universal` / `domain:<name>` / `project:<name>`). PRD now states the resolved taxonomy with a footnote explaining it refines the intent.
- **Closed the point-in-time flagging gap.** Neither doc previously guaranteed that entries served via `as_of` point-in-time queries carry an explicit historical marker — without it, PRD's "zero expired/superseded entries served unflagged" metric didn't hold outside the default retrieval path. Both docs now specify the `historical=true` flag.
- **Surfaced two silent risks as explicit non-decisions.** R4 ("never add LLM extraction to core, even for lazy producers") and the Phase-5 cost/latency measurement harness (required by PRD's "Cost" success metric) had no anchor in TECH_SPEC; both now have one (§2, §10).
- **Added the audit-trail and promote() traceability notes.** The journal now explicitly named as what makes PRD's "auditable" claim checkable; `promote()`'s convenience-wrapper-over-UPDATE relationship stated in both docs so the six-op/eight-tool count never reads as a contradiction.
- **UC-9 / P9 broadened** to name physical write-corruption risk under concurrency (TECH_SPEC §3.3's locking mechanism), not only the logical-conflict framing that was there before.

## [0.1.5] — 2026-07-17

### Added

- `docs/TECH_SPEC.md` — technical design derived from the intent and PRD.
  Resolves all six PRD open questions (file-based SoT + append-only journal;
  typed oracle-evidence records where self-assertions are unrepresentable;
  eight named MCP tools compiling to the six contract ops; three-rung scope
  taxonomy; surface-only conflict handling; migration producer). Specifies
  the monorepo package layout, byte-stable storage and content-derived ids,
  the governance state machine, the retrieval pipeline with staleness
  abstention and budgeting, the pack format with a blocking redaction
  pipeline, producer adapters, and the test strategy pinned to the intent's
  planned test paths.

## [0.1.4] — 2026-07-17

### Changed

- PRD → v0.1.1 after a full cross-check against the system intent: restored
  the two dropped non-goals (not-a-replacement-for-siblings; not generic
  document RAG), added the joint-satisfaction lifecycle test as the explicit
  completion gate and the injection-cost measurement condition to success
  metrics, surfaced the constraint priority ordering and the four
  context-operator coverage map in the requirements section, and added the
  wrong-lesson liability hedge to the pack-export use case.

## [0.1.3] — 2026-07-17

### Added

- `docs/PRD.md` — product requirements derived from the system intent:
  12 research-grounded pain points, 12 use cases (each generating a
  requirement), functional requirements by plane mapped to constraints
  C1–C7, when-not-to-use-Stele guidance, measurable success metrics, and
  the 6 open questions that block the tech spec.

## [0.1.2] — 2026-07-17

### Added

- OSS scaffolding parity with sibling projects: `CONTRIBUTING.md` (design-phase
  contribution model — research corrections, pattern challenges, intent review),
  `SECURITY.md` (private reporting; design-phase security commitments),
  `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1), `.gitignore`.

### Changed

- Scope hygiene: product questions are now stated as plainly out of scope
  across the intent, roadmap, patterns, and research docs. This repository
  defines infrastructure.

## [0.1.1] — 2026-07-17

### Changed

- Full cross-check of the system intent against `docs/patterns/` closed the
  gaps it found: restored the true `DELETE` operation alongside `SUPERSEDE`
  (erasure vs. belief update — they are not the same op); C2 gained staleness
  abstention and budgeted injection; C3 gained audience tiers, adaptation
  operators, and the recipe-vs-equipment rule; C6 gained subject-id erasure
  indexing, source pointers, rejected-options content, and environment
  assumptions for workflow entries; added the four-operator coverage map
  (write/select/compress/isolate) and a full failure-mode coverage register
  with explicit mitigations or written acceptances; joint lifecycle test now
  exercises erasure cascade. README/ROADMAP aligned. Intent → v0.1.1.

## [0.1.0] — 2026-07-17

### Added

- Repository created (design phase — no implementation yet).
- `stele_system_intent.yaml`: system intent locking the architecture — five
  planes (contract / tool surface / governance / retrieval / export), seven
  constraints with planned test paths, satisfiability analysis, ecosystem
  boundaries (judgment producer, retrieval router, promotion oracle — protocol linkage only),
  known risks.
- `docs/research/AGENT_SESSION_LEDGER_INFERENCE_TIME_MEMORY_RESEARCH_2026.md`
  (v1.4): source-audited research on inference-time agent ledgers — relocated
  from the authors' private research corpus; host references genericized.
- `docs/research/AGENT_MEMORY_STORAGE_SYSTEMS_RESEARCH_2026.md` (v1.2):
  source-audited memory-storage landscape — relocated likewise.
- `docs/patterns/patterns_session_ledger_memory.yaml` (v1.2): distilled
  pattern file — 13 foundational findings, 12 operational patterns,
  contested findings, research-does-not-support register, quantitative
  reference.
- `README.md`, `ROADMAP.md`, MIT `LICENSE`.
