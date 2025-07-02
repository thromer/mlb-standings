#!/bin/bash

PROJECT=mlb-standings-001
PROJECT_NUMBER=$(gcloud projects describe $PROJECT --format="value(projectNumber)")
LOCATION=us-west1
SERVICE=mlb-standings-001-update
APP=
URL="https://${SERVICE}-${PROJECT_NUMBER}.${LOCATION}.run.app/${APP}"
TOKEN="$(gcloud --project=${PROJECT} auth print-identity-token)"

curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer ${TOKEN}" \
     "${URL}" -d '{}'
