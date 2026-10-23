#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

SOURCE_GTFS_URL="https://www.data.gouv.fr/api/1/datasets/r/e6e71df3-0163-42ed-9c1f-927c4026ab1b"
WEB_DIR="/var/www/gtfs"
SOURCE_GTFS="cache/gtfs-src.zip"
SOURCE_LAST_MODIFIED="cache/gtfs-src.last-modified"

# --- Vérification de mise à jour ---
lastModified=$(curl -sIL "$SOURCE_GTFS_URL" | grep -i '^last-modified' | tail -n 1 | tr -d '\r' || true)
savedLastModified=$(cat last-modified.txt 2>/dev/null || true)

if [[ -n "$lastModified" && "$lastModified" == "$savedLastModified" ]]; then
    echo "Mise à jour non nécessaire."
    exit 0
fi

# --- Téléchargement : la source déjà téléchargée est réutilisée tant qu'elle n'a pas changé, pour ne pas la
# retélécharger à chaque exécution lorsque c'est le traitement qui échoue ---
sourceLastModified=$(cat "$SOURCE_LAST_MODIFIED" 2>/dev/null || true)

if [[ -n "$lastModified" && "$lastModified" == "$sourceLastModified" && -f "$SOURCE_GTFS" ]]; then
    echo "GTFS source inchangé, utilisation du cache."
else
    echo "Téléchargement du GTFS..."
    mkdir -p "$(dirname "$SOURCE_GTFS")"
    wget -q -O "$SOURCE_GTFS.tmp" "$SOURCE_GTFS_URL"
    mv "$SOURCE_GTFS.tmp" "$SOURCE_GTFS"
    echo "$lastModified" > "$SOURCE_LAST_MODIFIED"
fi

echo "Traitement..."
.venv/bin/python -m vitre "$SOURCE_GTFS" gtfs-processed.zip

echo "Déploiement..."
mv gtfs-processed.zip "$WEB_DIR/vitre.zip"

# On ne met à jour la date de référence que si tout a réussi
echo "$lastModified" > last-modified.txt
echo "Terminé avec succès."
