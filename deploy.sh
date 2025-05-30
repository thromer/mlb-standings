#!/usr/bin/bash

cd $(realpath "$(dirname "${BASH_SOURCE[0]}")")/src &&
    docker build -t us-west1-docker.pkg.dev/mlb-standings-001/artifacts/mlb-standings-001-update:latest . &&
    docker push us-west1-docker.pkg.dev/mlb-standings-001/artifacts/mlb-standings-001-update:latest &&
    gcloud run deploy \
	   --image us-west1-docker.pkg.dev/mlb-standings-001/artifacts/mlb-standings-001-update \
	   --base-image us-west1-docker.pkg.dev/serverless-runtimes/google-22/runtimes/python312 \
	   --region us-west1 mlb-standings-001-update \
	   --concurrency 1 \
	   --max-instances 1 \
	   --timeout 1800 \
	   --cpu=0.1 \
	   --memory=256Mi &&
    docker images ls -f 'reference=us-west1-docker.pkg.dev/mlb-standings-001/artifacts/mlb-standings-001-update*' |
	tail -n +2 | awk '{print $3}' | xargs docker image rm
