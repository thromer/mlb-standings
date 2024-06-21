#!/usr/bin/env bash
PROJECT_ID=mlb-standings-001
SERVICE_ACCOUNT=mlb-standings-001-update
cd $(realpath "$(dirname "${BASH_SOURCE[0]}")") && gcloud --project=mlb-standings-001 functions deploy mlb-standings-001-update --gen2 --runtime=python312 --region=us-west1 --source=src --entry-point=update --trigger-http --no-allow-unauthenticated --timeout=1800 --service-account=${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com
