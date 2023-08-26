# mlb-standings

# local exec using default creds (pick a project, will need some services enabled I guess, at the very least 'Service Usage API'

gcloud init
gcloud auth login
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/sqlservice.admin,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive.metadata.readonly
gcloud auth application-default set-quota-project PROJECT

And in cloud console 
1. add self to Service Usage Consumer for PROJECT
2. Enable APIs for PROJECT: Service Usage, Sheets, Drive

