FROM python:3.12-slim
WORKDIR /app
COPY packages/stele-core packages/stele-core
COPY packages/stele-mcp packages/stele-mcp
COPY deploy deploy
RUN pip install --no-cache-dir -e packages/stele-core -e 'packages/stele-mcp[hosted]'
ENV STELE_STORE=/data/store STELE_AUTH_DISABLED=false
VOLUME /data
EXPOSE 8080
CMD ["python", "deploy/wsgi.py", "--port", "8080"]
