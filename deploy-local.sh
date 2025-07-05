#!/usr/bin/bash

PROJECT=mlb-standings-001
LOCATION=us-west1
SERVICE=mlb-standings-001-update
cd "$(realpath "$(dirname "${BASH_SOURCE[0]}")")" &&
    uv --color never sync --all-packages &&
    docker build --progress=plain -t ${LOCATION}-docker.pkg.dev/${PROJECT}/artifacts/${SERVICE}:latest . &&
    docker build --progress=plain -t ${SERVICE}-merged:latest -f Dockerfile.merged . &&
    docker run -p 8080:8080 -e PORT=8080 --rm ${SERVICE}-merged:latest
