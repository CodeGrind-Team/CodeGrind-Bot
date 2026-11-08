# Backup runner: MongoDB tools (same version as the database) + age + rclone.
FROM mongo:8.0.34-noble

ARG RCLONE_VERSION=v1.75.2
ARG TARGETARCH

RUN apt-get update && \
    apt-get install -y --no-install-recommends age ca-certificates curl unzip && \
    rm -rf /var/lib/apt/lists/* && \
    arch="${TARGETARCH:-$(dpkg --print-architecture)}" && \
    zip="rclone-${RCLONE_VERSION}-linux-${arch}.zip" && \
    cd /tmp && \
    curl -fsSLO "https://downloads.rclone.org/${RCLONE_VERSION}/${zip}" && \
    curl -fsSL "https://downloads.rclone.org/${RCLONE_VERSION}/SHA256SUMS" | grep " ${zip}\$" | sha256sum -c - && \
    unzip -q "${zip}" && \
    install -m 0755 "rclone-${RCLONE_VERSION}-linux-${arch}/rclone" /usr/local/bin/rclone && \
    rm -rf /tmp/rclone-* && \
    rclone version | head -1 && age --version

COPY lib.sh backup.sh restore.sh entrypoint.sh /opt/backup/
RUN chmod 0755 /opt/backup/*.sh

ENTRYPOINT ["/opt/backup/entrypoint.sh"]
CMD ["schedule"]
