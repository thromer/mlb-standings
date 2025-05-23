Future work
=
* Get notified when new season starts, maybe.
* Maybe handle first day of season gracefully, when https://www.baseball-reference.com/leagues/majors/2024-schedule.shtml starts off with "Today's Games" instead of a date. Or at least don't error out so painfully.
* Stop using baseball-reference.com, or was there a reason not to switch to statsapi.mlb.com (other than having started with baseball-reference)?

# mlb-standings

# local exec using default creds (pick a project, will need some services enabled I guess, at the very least 'Service Usage API'

First get gcloud e.g. e.g. https://cloud.google.com/sdk/docs/install#deb
```bash
# Get cloud e.g. https://cloud.google.com/sdk/docs/install#deb
gcloud init
```

See RUNNING-LOCALLY for application default credentials

And in cloud console 
1. add self to Service Usage Consumer for PROJECT
2. Enable APIs for PROJECT: Service Usage, Sheets, Drive


For cloud function created mlb-standings-001-update@mlb-standings-001.iam.gserviceaccount.com service account and granted permission to relevant Drive folder

For real ... timeout is 1800 so that we can run hourly.

gcloud --project=mlb-standings-001 functions deploy mlb-standings-001-update --gen2 --runtime=python311 --region=us-west1 --source=src --entry-point=update --trigger-http --allow-unauthenticated --timeout=1800 --service-account=mlb-standings-001-update@mlb-standings-001.iam.gserviceaccount.com

To run directly:

``` bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://us-west1-mlb-standings-001.cloudfunctions.net/mlb-standings-001-update
```


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

THIS ONE

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

Stuff

https://googleapis.github.io/google-api-python-client/docs/dyn/sheets_v4.html

https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/drive_v3.files.html

By the way to delete a file created by service account: oddly can drag
and drop to trash from Drive UI, but cannot use snowman menu in Drive
or File menu in the file to move to trash.

For secrets to work in cloud: in permissions tab, grant relevant service account the role Secret Manager Secret Accessor. To find the service account, look at details for the cloud function.

This is super helpful for understanding statsapi.mlb.com
https://github.com/toddrob99/MLB-StatsAPI/wiki
