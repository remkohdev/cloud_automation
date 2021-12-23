#!/usr/bin/env python3

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import os
import json
import argparse
import pandas as pd
from datetime import datetime
import requests

###############################################################################
# FUNCTIONS
###############################################################################

def init():
    """parse arguments, validate input, set variables"""

    # commandline arguments
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(prog='python3 users_report.py -c ../../config.lcoal -u users.yaml -o json')

    parser.add_argument(
        "-c", "--config_file",
        required=True,
        help="Path to config file"
    )

    parser.add_argument(
        "-u", "--users_file",
        required=True,
        help="Path to users file"
    )

    list_of_output_formats=["csv", "json"]
    parser.add_argument(
        "-o", "--output_format",
        required=False,
        help="Output format",
        default="csv",
        choices=list_of_output_formats
    )

    list_of_order_by=["association", "manager"]
    parser.add_argument(
        "-ob", "--order_by",
        required=False,
        help="Order By",
        default="manager",
        choices=list_of_order_by
    )

    # Parse input arguments
    args = parser.parse_args()
    global CONFIG_FILE
    CONFIG_FILE=args.config_file

    global USERS_FILE
    USERS_FILE=args.users_file

    global OUTPUT_FORMAT
    OUTPUT_FORMAT=args.output_format

    global ORDER_BY
    ORDER_BY=args.order_by

    # Config values
    with open(CONFIG_FILE) as jsonfile:
        config = json.load(jsonfile)

        global IBM_CLOUD_APIKEY
        IBM_CLOUD_APIKEY=config['credentials']['ibm_cloud_apikey']
        global IBMCLOUD_ORG_ACCOUNTID
        IBMCLOUD_ORG_ACCOUNTID=config['account']['accountid']
    
    # Generate variable values
    now = datetime.now()
    date_time = now.strftime("%Y%m%dT%H%M%S%f")
    
    # Build directory
    global OUTPUT_DIR
    OUTPUT_DIR_ROOT='build'
    if(not os.path.exists(OUTPUT_DIR_ROOT)):
        os.makedirs(OUTPUT_DIR_ROOT)
    OUTPUT_DIR=("{}/{}").format(OUTPUT_DIR_ROOT, date_time)
    if(not os.path.exists(OUTPUT_DIR)):
        os.makedirs(OUTPUT_DIR)

    global USERS_REPORT_ORDERED_OUTPUT_FILENAME
    USERS_REPORT_ORDERED_OUTPUT_FILENAME=('{}/users_report_orderedby_{}_{}.{}').format(OUTPUT_DIR, ORDER_BY, date_time, OUTPUT_FORMAT)
    global USERS_REPORT_UNORDERED_OUTPUT_FILENAME
    USERS_REPORT_UNORDERED_OUTPUT_FILENAME=('{}/users_report_{}.{}').format(OUTPUT_DIR, date_time, OUTPUT_FORMAT)
    
    global VALID_USERS_OUTPUT_FILENAME
    VALID_USERS_OUTPUT_FILENAME = ('{}/valid_users_hcbt_{}.{}').format(OUTPUT_DIR, date_time, OUTPUT_FORMAT)

    global IBMCLOUD_ACCOUNT_USERS_OUTPUT_FILENAME
    IBMCLOUD_ACCOUNT_USERS_OUTPUT_FILENAME = ('{}/ibmcloud_users_{}_{}.{}').format(OUTPUT_DIR, IBMCLOUD_ORG_ACCOUNTID, date_time, OUTPUT_FORMAT)

    print(
        ("Running Users Report using Config File: {}, Report Type: {}, Output format: {}, " +
         "Valid Users File: {}, Valid Users Output File: {}, IBM Cloud Account Output file: {} " +
         "Users Report Output File: {}")
        .format(
            CONFIG_FILE,
            ORDER_BY,
            OUTPUT_FORMAT,
            USERS_FILE,
            VALID_USERS_OUTPUT_FILENAME,
            IBMCLOUD_ACCOUNT_USERS_OUTPUT_FILENAME,
            USERS_REPORT_ORDERED_OUTPUT_FILENAME
        )
    )

def get_managers_from_users(users):
    """get_managers_from_users(users)"""

    managers=[]
    manager_emails=[]

    for user in users:
        user_manager_email=user["manager"]

        if (user_manager_email not in manager_emails):
            user_manager = { "email": user_manager_email }
            # add email to manager_emails array for user cross check below
            manager_emails.append(user_manager_email)
            # add full manager user to managers array
            for user in users:
                if(user["email"] == user_manager_email):
                    user_manager["email"] = user["email"]
                    user_manager["name"] = user["name"]
                    user_manager["association"] = user["association"]
            managers.append(user_manager)
    
    return managers

def get_users_for_manager(manager, valid_users):
    """get_users_for_manager(manager, valid_users)"""

    users_for_manager=[]

    for user in valid_users:
        
        user_manager_email=user["manager"]
        
        if (user_manager_email == manager["email"]):
            users_for_manager.append(user)
    
    return users_for_manager

def get_associations_from_users(users):
    """get_users_for_association(association, users)"""

    associations=[]

    for user in users:
        user_association=user["association"]

        if (user_association not in associations):
            associations.append(user_association)
    
    return associations

def get_users_for_association(association, users):
    """get_users_for_association(association, users)"""

    users_for_association=[]

    for user in users:
        user_association=user["association"]

        if (user_association == association):
            users_for_association.append(user)
    
    return users_for_association

def get_ibmcloud_access_token():
    """get_ibmcloud_access_token()"""

    url = "https://iam.cloud.ibm.com/identity/token"

    payload= {
        "apikey" : IBM_CLOUD_APIKEY,
        "response_type" : "cloud_iam",
        "grant_type" : "urn:ibm:params:oauth:grant-type:apikey" 
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    access_token=response.json()['access_token']
    return access_token

def get_ibmcloud_users():
    """get_ibm_cloud_users()"""

    # doc: https://cloud.ibm.com/apidocs/user-management#list-users

    IBMCLOUD_ACCOUNT_USERS_URL = "https://user-management.cloud.ibm.com/v2/accounts/{}/users".format(IBMCLOUD_ORG_ACCOUNTID)
    access_token = get_ibmcloud_access_token()

    #ORG_NAME=""   
    #ORG_REGION=us-south
    #ORG_ACCOUNTID=
    # ibmcloud account org-users $ORG_NAME -r $ORG_REGION --output json > build/org_users.json

    headers1 = {
        'Authorization': access_token,
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'apikey' : 'iam_apikey'
    }

    response = requests.get(url=IBMCLOUD_ACCOUNT_USERS_URL, headers=headers1, data=payload)

    ibmcloud_users = response.json()['resources']
    return ibmcloud_users

def get_users_report(valid_users, ibmcloud_account_users):
    """get_users_report()"""

    users_report = []
    valid_account_users = []
    invalid_account_users = []

    # use case 1: find users in account not in valid_users
    for account_user in ibmcloud_account_users:

        # check if account user is in valid_users
        is_valid_user=False
        for valid_user in valid_users:
            if ( account_user["email"] == valid_user["email"] ):
                account_user["name"] = valid_user["name"]
                account_user["identities"] = valid_user["identities"]
                if "resourceGroups" in valid_user:
                    account_user["resourceGroups"] = valid_user["resourceGroups"]
                account_user["manager"] = valid_user["manager"]
                account_user["association"] = valid_user["association"]

                is_valid_user=True
    
        if is_valid_user:
            valid_account_users.append(account_user)
        else:
            invalid_account_users.append(account_user)
        
    users_report = {
        "valid_account_users" : valid_account_users,
        "invalid_account_users" : invalid_account_users
    }
    return users_report

def write_to_file(report_lines, output_filename):
    """write to file"""

    if OUTPUT_FORMAT == "json":
        with open(output_filename, 'w') as fp:
            json.dump(report_lines, fp)
    elif OUTPUT_FORMAT == "csv":
        df = pd.read_json(json.dumps(report_lines))
        df.to_csv(output_filename)
    else:
        with open(output_filename, 'w') as fp:
            json.dump(report_lines, fp)

###############################################################################
# MAIN
###############################################################################

init()

# get valid users
valid_users = []
with open(USERS_FILE, 'r') as stream:
    data_json = yaml.load(stream, Loader=Loader)
    report=[]
    valid_users = data_json["users"]

write_to_file(valid_users, VALID_USERS_OUTPUT_FILENAME)

# get ibmcloud account users
ibmcloud_account_users=get_ibmcloud_users()
write_to_file(ibmcloud_account_users, IBMCLOUD_ACCOUNT_USERS_OUTPUT_FILENAME)

# cross-validate valid_users and ibmcloud_account_users
# users_report = {
#        "valid_account_users" : valid_account_users,
#        "invalid_account_users" : invalid_account_users
users_report_users = get_users_report(valid_users, ibmcloud_account_users)

write_to_file(users_report_users, USERS_REPORT_UNORDERED_OUTPUT_FILENAME)

# order users_report_users by order_by
ordered_users_report_users = []
if(ORDER_BY=="association"):
    associations=get_associations_from_users(valid_users)
    valid_users_by_association = []
    invalid_users_by_association = []
    for association in associations:
        valid_users_for_association=get_users_for_association(association, users_report_users["valid_account_users"])
        invalid_users_for_association=get_users_for_association(association, users_report_users["invalid_account_users"])
        valid_users_by_association.append(valid_users_for_association)
        invalid_users_by_association.append(invalid_users_for_association)
    users_report_users.append({
        "valid_users_by_association" : valid_users_by_association,
        "invalid_users_by_association" : invalid_users_by_association,
    })
else:
    managers=get_managers_from_users(valid_users)
    valid_users_by_manager = []
    invalid_users_by_manager = []
    for manager in managers:
        valid_users_for_manager=get_users_for_manager(manager, users_report_users["valid_account_users"])
        manager["valid_users"] = valid_users_for_manager
        valid_users_by_manager.append(manager)
    users_report_users = [{
        "valid_users_by_manager" : valid_users_by_manager,
        "invalid_users" : users_report_users["invalid_account_users"],
    }]

write_to_file(users_report_users, USERS_REPORT_ORDERED_OUTPUT_FILENAME)
