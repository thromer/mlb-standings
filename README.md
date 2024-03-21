New season
=
* copy previous season to a new spreadsheet
* add row to [table of contents](https://docs.google.com/spreadsheets/d/14h3hTCvXNzUqTtbegIzSE6JwetMgvtWB6xP9gv87gZs) spreadsheet
* in new spreadsheet clear data in data, al_uploaded, nl_uploaded, playoff_upload tabs

Future work
=
* Auto-create spreadsheet each year.
  * Get notified when that happens, maybe.
* Get notified when the cloud function fails, or just when cloud scheduler fails.
* Maybe handle first day of season gracefully, when https://www.baseball-reference.com/leagues/majors/2024-schedule.shtml starts off with "Today's Games" instead of a date. Or at least don't error out so painfully.

# mlb-standings

# local exec using default creds (pick a project, will need some services enabled I guess, at the very least 'Service Usage API'

gcloud init
gcloud auth login
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/sqlservice.admin,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive.metadata.readonly
gcloud auth application-default set-quota-project PROJECT

And in cloud console 
1. add self to Service Usage Consumer for PROJECT
2. Enable APIs for PROJECT: Service Usage, Sheets, Drive


For cloud function created mlb-standings-001-update@mlb-standings-001.iam.gserviceaccount.com service account and granted permission to relevant Drive folder

For real ... timeout is 1800 so that we can run hourly.

gcloud --project=mlb-standings-001 functions deploy mlb-standings-001-update --gen2 --runtime=python311 --region=us-west1 --source=src --entry-point=update --trigger-http --allow-unauthenticated --timeout=1800 --service-account=mlb-standings-001-update@mlb-standings-001.iam.gserviceaccount.com

Trigger URL is https://us-west1-mlb-standings-001.cloudfunctions.net/mlb-standings-001-update


Logs are here

https://console.cloud.google.com/logs/query;query=resource.type%3D%22cloud_run_revision%22%0Aresource.labels.service_name%3D%22mlb-standings-001-update%22;cursorTimestamp=2023-08-30T22:30:40.888073Z;duration=PT1H?project=mlb-standings-001

# for playing (main.py:cf_test)
gcloud --project=mlb-standings-001 functions deploy mlb-standings-001-fun --gen2 --runtime=python311 --region=us-west1 --source=src --entry-point=cf_test --trigger-http --allow-unauthenticated --timeout=3600 --service-account=mlb-standings-001-update@mlb-standings-001.iam.gserviceaccount.com

Now to invoke it via cloud scheduler, following

https://github.com/GoogleCloudPlatform/community/blob/master/archived/using-scheduler-invoke-private-functions-oidc/index.md

Have to deploy --no-allow-unauthenticated

PROJECT_ID=mlb-standings-001
SERVICE_ACCOUNT=mlb-standings-001-update
URI=https://us-west1-mlb-standings-001.cloudfunctions.net/mlb-standings-001-update

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
  --role roles/cloudfunctions.invoker

gcloud --project=mlb-standings-001 functions deploy mlb-standings-001-update --gen2 --runtime=python311 --region=us-west1 --source=src --entry-point=update --trigger-http --no-allow-unauthenticated --timeout=1800 --service-account=${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com

curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" ${URI}

# Not 100% sure if this was needed

gcloud --project=${PROJECT_ID} iam service-accounts add-iam-policy-binding ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com --member user:tromer@gmail.com --role roles/iam.serviceAccountUser

gcloud scheduler jobs create http mlb-standings-update \
  --location us-west1 \
  --schedule "2 * * * *" \
  --time-zone "America/Los_Angeles" \
  --uri "${URI}" \
  --oidc-service-account-email ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com

Newer is https://cloud.google.com/scheduler/docs/http-target-auth

First try apparently I missed the following. With effort I can grant this permission, and it works!

gcloud --project=${PROJECT_ID} functions add-iam-policy-binding mlb-standings-001-update --member=serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com --role=roles/run.invoker --gen2
