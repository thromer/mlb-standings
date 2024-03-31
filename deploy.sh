#!/usr/bin/env bash
PROJECT_ID=mlb-standings-001
SERVICE_ACCOUNT=mlb-standings-001-update
gcloud --project=mlb-standings-001 functions deploy mlb-standings-001-update --gen2 --runtime=python311 --region=us-west1 --source=src --entry-point=update --trigger-http --no-allow-unauthenticated --timeout=1800 --service-account=${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com
