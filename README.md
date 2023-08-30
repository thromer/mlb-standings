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

# for playing (main.py:cf_test)
gcloud --project=mlb-standings-001 functions deploy mlb-standings-001-fun --gen2 --runtime=python311 --region=us-west1 --source=src --entry-point=cf_test --trigger-http --allow-unauthenticated --timeout=3600 --service-account=mlb-standings-001-update@mlb-standings-001.iam.gserviceaccount.com

