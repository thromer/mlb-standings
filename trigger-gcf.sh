#!/bin/bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: bearer $(gcloud --project=mlb-standings-001 auth print-identity-token)" https://us-west1-mlb-standings-001.cloudfunctions.net/mlb-standings-001-update -d '{}'
