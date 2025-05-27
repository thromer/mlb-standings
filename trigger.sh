#!/bin/bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: bearer $(gcloud --project=mlb-standings-001 auth print-identity-token)" \
     https://mlb-standings-001-repro-432241755017.us-west1.run.app -d '{}'
