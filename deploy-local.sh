#!/usr/bin/bash

PROJECT=mlb-standings-001
LOCATION=us-west1
SERVICE=mlb-standings-001-update
cd "$(realpath "$(dirname "${BASH_SOURCE[0]}")")" &&
    uv sync --all-packages &&
    docker build --progress=plain -t ${LOCATION}-docker.pkg.dev/${PROJECT}/artifacts/${SERVICE}:latest . &&
    docker build -t ${SERVICE}-merged:latest -f Dockerfile.merged . &&
    docker run --rm ${SERVICE}-merged:latest
