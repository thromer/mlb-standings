#!/usr/bin/bash

set -o pipefail

PROJECT=mlb-standings-001
LOCATION=us-west1
LOGS_BUCKET=gs://${PROJECT}_build-logs

ensure_logs_bucket() {
    if gcloud --project=${PROJECT} storage buckets describe ${LOGS_BUCKET} >& /dev/null; then
	return 0
    fi
    gcloud --project=mlb-standings-001 storage buckets create --location=us-west1 --soft-delete-duration=0 ${LOGS_BUCKET}
    return $?
}

TIMESTAMP="$(date -u +'%Y-%m-%dT%H:%M:%S.%NZ')"
BUILD_LOG="/tmp/mlb-standings-001-build-${TIMESTAMP}.log"
DEPLOY_LOG="/tmp/mlb-standings-001-deploy-${TIMESTAMP}.log"
cd $(realpath "$(dirname "${BASH_SOURCE[0]}")")/src &&
    docker build --progress=plain -t ${LOCATION}-docker.pkg.dev/${PROJECT}/artifacts/mlb-standings-001-update:latest . |& ts |& tee "${BUILD_LOG}" &&
    ensure_logs_bucket &&
    gcloud --project=${PROJECT} storage cp --gzip-local-all "${BUILD_LOG}" ${LOGS_BUCKET}/ &&
    docker push ${LOCATION}-docker.pkg.dev/${PROJECT}/artifacts/mlb-standings-001-update:latest &&
    gcloud run deploy \
	   --project=${PROJECT} \
	   --image ${LOCATION}-docker.pkg.dev/${PROJECT}/artifacts/mlb-standings-001-update \
	   --base-image ${LOCATION}-docker.pkg.dev/serverless-runtimes/google-22/runtimes/python312 \
	   --region ${LOCATION} \
	   --no-allow-unauthenticated \
	   --concurrency 1 \
	   --max-instances 1 \
	   --timeout 1800 \
	   --cpu=0.2 \
	   --memory=256Mi \
	   --cpu-boost \
	   mlb-standings-001-update |& ts |& tee "${DEPLOY_LOG}" &&
    gcloud --project=${PROJECT} storage cp --gzip-local-all "${DEPLOY_LOG}" ${LOGS_BUCKET}/ &&
    docker image ls -f "reference=${LOCATION}-docker.pkg.dev/${PROJECT}/artifacts/mlb-standings-001-update*" |
    	tail -n +2 | awk '$2 != "latest" {print $3}' | xargs -r docker image rm
