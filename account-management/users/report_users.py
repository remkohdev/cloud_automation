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

# 1. read mailmap
# 2. create array of arrays, consisting of users per manager, include empty (unknown)

def init():
    """parse arguments, validate input, set variables"""

    # commandline arguments
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(prog='python3 report_users.py -c ../../config.lcoal -u users.yaml -o json')

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

    list_of_report_types=["by_association", "by_manager"]
    parser.add_argument(
        "-t", "--report_type",
        required=False,
        help="Report Type",
        default="by_manager",
        choices=list_of_report_types
    )

    # Parse input arguments
    args = parser.parse_args()
    global CONFIG_FILE
    CONFIG_FILE=args.config_file

    global USERS_FILE
    USERS_FILE=args.users_file

    global OUTPUT_FORMAT
    OUTPUT_FORMAT=args.output_format

    global REPORT_TYPE
    REPORT_TYPE=args.report_type
    
    # Generate variable values
    global OUTPUT_FILE_NAME
    now = datetime.now()
    date_time = now.strftime("%Y%m%dT%H%M%S%f")
    # check build directory
    OUTPUT_DIR='build'
    if(not os.path.exists(OUTPUT_DIR)):
        os.makedirs(OUTPUT_DIR)
    OUTPUT_FILE_NAME=('{}/report_users_{}_{}.{}').format(OUTPUT_DIR, REPORT_TYPE, date_time, OUTPUT_FORMAT)
    print(
        "Running Users Report using Config File: {}, Users File: {}, Report Type: {}, Output format: {}, Output file: {}"
        .format(
            CONFIG_FILE,
            USERS_FILE,
            REPORT_TYPE,
            OUTPUT_FORMAT,
            OUTPUT_FILE_NAME
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

def get_users_for_manager(manager, users):
    """get_users_for_manager(manager, users)"""

    users_for_manager=[]

    for user in users:
        user_manager=user["manager"]

        if (user_manager == manager):
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

def write_to_file(report_lines):
    """write to file"""

    print("----->write to file")
    if OUTPUT_FORMAT == "json":
        with open(OUTPUT_FILE_NAME, 'w') as fp:
            json.dump(report_lines, fp)
    elif OUTPUT_FORMAT == "csv":
        df = pd.read_json(json.dumps(report_lines))
        df.to_csv(OUTPUT_FILE_NAME)
    else:
        with open(OUTPUT_FILE_NAME, 'w') as fp:
            json.dump(report_lines, fp)


init()

with open(CONFIG_FILE) as jsonfile:
    config = json.load(jsonfile)

    IBM_CLOUD_APIKEY=config['credentials']['ibm_cloud_apikey']

with open(USERS_FILE, 'r') as stream:
    data_json = yaml.load(stream, Loader=Loader)
    report=[]
    valid_users = []

    users = data_json["users"]

    if(REPORT_TYPE=="by_association"):
        associations=get_associations_from_users(users)
        for association in associations:
            users_for_association=get_users_for_association(association, users)
            valid_users.append({ "association": association, "users": users_for_association})
    else:
        managers=get_managers_from_users(users)
        for manager in managers:
            users_for_manager=get_users_for_manager(manager["email"], users)
            valid_users.append({ "manager": manager, "users": users_for_manager})

    write_to_file(valid_users)

    
    
    #print as yaml
    #print(yaml.dump(data_json, Dumper=Dumper))
