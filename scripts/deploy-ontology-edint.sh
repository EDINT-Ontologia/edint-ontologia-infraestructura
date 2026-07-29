#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:-}"
DEF_PATH="${2:-}"
SLUG="${3:-}"

if [ -z "$SOURCE_DIR" ] || [ -z "$DEF_PATH" ] || [ -z "$SLUG" ]; then
  echo "Uso: $0 SOURCE_DIR DEF_PATH SLUG" >&2
  exit 2
fi

case "$SLUG" in
  ''|*[!a-z0-9-]*)
    echo "Slug invalido: $SLUG" >&2
    exit 2
    ;;
esac

if [ ! -d "$SOURCE_DIR" ]; then
  echo "No existe SOURCE_DIR: $SOURCE_DIR" >&2
  exit 2
fi

for file in index-es.html index-en.html ontology.rdf ontology.ttl ontology.jsonld ontology.nt; do
  if [ ! -s "$SOURCE_DIR/$file" ]; then
    echo "Falta $file en SOURCE_DIR" >&2
    exit 2
  fi
done

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync no esta disponible" >&2
  exit 2
fi

HTTPDOCS="$(dirname "$DEF_PATH")"
VHOST_ROOT="$(dirname "$HTTPDOCS")"
BACKUP_ROOT="$VHOST_ROOT/edint-backups"
STORAGE_ROOT="$DEF_PATH/_ontologias"
DEST="$STORAGE_ROOT/$SLUG"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$BACKUP_ROOT/${TIMESTAMP}-def-${SLUG}"
RELEASE="${DEST}.release-${TIMESTAMP}"

mkdir -p "$BACKUP_ROOT" "$BACKUP" "$STORAGE_ROOT"

if [ -d "$DEST" ]; then
  cp -a "$DEST" "$BACKUP/$SLUG"
fi

mkdir -p "$RELEASE"
rsync -a --delete --exclude ".git" --exclude ".github" "$SOURCE_DIR/" "$RELEASE/"

for file in index-es.html index-en.html ontology.rdf ontology.ttl ontology.jsonld ontology.nt; do
  test -s "$RELEASE/$file"
done

if [ -d "$DEST" ]; then
  rm -rf "$DEST"
fi
mv "$RELEASE" "$DEST"
find "$DEST" -type d -exec chmod 755 {} +
find "$DEST" -type f -exec chmod 644 {} +

echo "Publicado $SLUG en $DEST"
echo "Backup: $BACKUP"
