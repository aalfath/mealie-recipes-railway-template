# Mealie on Railway: the official image, pinned by version and digest,
# plus a small start script (see railway-start.sh).
FROM ghcr.io/mealie-recipes/mealie:v3.31.0@sha256:97e21ac96e9a8d1ee15aaf558ba3f14998936b9d6f334e40ebb4c6c2127dc12f

COPY railway-start.sh /railway/railway-start.sh
COPY bootstrap_admin.py /railway/bootstrap_admin.py
RUN chmod +x /railway/railway-start.sh

# Upstream's /app/run.sh starts as root, chowns /app (where the volume is
# mounted) and then drops to its own user with gosu, so stay root here.
USER root
ENTRYPOINT ["/railway/railway-start.sh"]
