export APIKEY=
ibmcloud login --apikey $APIKEY

ORG_NAME=""   
ORG_REGION=us-south
ORG_ACCOUNTID=

ibmcloud account org-users $ORG_NAME -r $ORG_REGION --output json > build/org_users.json