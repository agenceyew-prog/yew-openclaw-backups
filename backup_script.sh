#!/bin/bash
set -euo pipefail

LOCK_FILE="/tmp/openclaw_backup.lock"
SOURCE_DIR="/data/.openclaw"
BACKUP_DIR="/data/openclaw_backups"
RETENTION_DAYS=7

log() { echo "[$(date -Is)] $*"; }

(
 flock -xn 10 || { log "Backup already running (lock busy). Exiting."; exit 0; }

 umask 077

 mkdir -p "$BACKUP_DIR"
 chmod 700 "$BACKUP_DIR"

 TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
 BACKUP_FILE="$BACKUP_DIR/openclaw_backup_${TIMESTAMP}.tar.gz"

 log "Starting backup -> $BACKUP_FILE"

 # Create archive (stores .openclaw/ at archive root)
 tar -czf "$BACKUP_FILE" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")"

 # Basic integrity check (can we list the archive?)
 tar -tzf "$BACKUP_FILE" >/dev/null

 chmod 600 "$BACKUP_FILE"
 log "Backup created + verified."

 # Retention
 find "$BACKUP_DIR" -type f -name "openclaw_backup_*.tar.gz" -mtime "+$RETENTION_DAYS" -delete

 log "Retention done (kept <= ${RETENTION_DAYS} days)."
 ls -lh "$BACKUP_DIR" | tail -n 50

 log "Backup finished."
) 10>"$LOCK_FILE"