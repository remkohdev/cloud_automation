#!/usr/bin/env python

import json
import argparse
import requests
import pandas as pd

with open("../config.local") as jsonfile:
    config = json.load(jsonfile)

    IBM_CLOUD_APIKEY=config['credentials']['ibm_cloud_apikey']

#################################
#           Functions           #
#################################

def init():
    """parse arguments, validate input, set variables"""

    # commandline arguments
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(prog='python3 report_cost_per_resource-group.py')

    list_of_output_formats=["csv", "json"]
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output format",
        default="csv",
        choices=list_of_output_formats
    )

    parser.add_argument(
        "-f", "--file",
        required=False,
        help="Output file name"
    )

    parser.add_argument(
        "-a", "--account_id",
        required=True,
        help="IBM Cloud account id"
    )

    parser.add_argument(
        "-d", "--billing_date",
        required=True,
        help="Billing date in format yyyy-MM"
    )

    # Parse arguments
    args = parser.parse_args()
    global OUTPUT_FORMAT
    OUTPUT_FORMAT=args.output
    global ACCOUNT_ID
    ACCOUNT_ID=args.account_id
    global BILLING_DATE
    BILLING_DATE=args.billing_date
    global OUTPUT_FILE_NAME
    OUTPUT_FILE_NAME="cost-report_{}.{}".format(BILLING_DATE, OUTPUT_FORMAT) #args.file

    print(
        "Running Cost Report with Output format: {}, Output file: {}, Account id: {}, Billing date: {}"
        .format(
            OUTPUT_FORMAT,
            OUTPUT_FILE_NAME,
            ACCOUNT_ID,
            BILLING_DATE
        )
    )

def get_access_token():
    """GET /access_token"""

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


def get_resources_for_resourcegroup(rg_id):
    """Get resource instance usage in a resource group"""

    # See: https://cloud.ibm.com/apidocs/metering-reporting#get-resource-usage-resource-group

    access_token = get_access_token()

    RESOURCE_GROUP_ID = rg_id
    url1 = "https://billing.cloud.ibm.com/v4/accounts/%s/resource_groups/%s/resource_instances/usage/%s"
    url2 = url1 % (ACCOUNT_ID, RESOURCE_GROUP_ID, BILLING_DATE)

    headers1 = {
        'Authorization': access_token,
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'apikey' : 'iam_apikey'
    }

    response = requests.get(url=url2, headers=headers1, data=payload)

    resources = response.json()['resources']
    return resources


def get_resourcegroups():
    """GET /resourcegroups"""

    access_token = get_access_token()
    authorization_header = "Bearer %s" % (access_token)

    url1 = "https://resource-controller.cloud.ibm.com/v2/resource_groups/"

    headers1 = {
        'Authorization': authorization_header,
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'apikey' : 'iam_apikey'
    }

    response = requests.get(url=url1, headers=headers1, data=payload)

    resource_groups = response.json()['resources']
    return resource_groups


def summarize_costs_for_resources(rg_id, rg_name, resources):
    """summarize costs"""
    total_cost = float(0)
    for resource in resources:
        for use in resource["usage"]:
            cost = float(use["cost"])
            total_cost += cost

    return total_cost

#################################
#              Main             #
#################################

print("----->Begin")

init()

# Step 1: Create Report "Cost per ResourceGroup"
print("----->1 - create report")
report_lines = []
report_header = "rg_id, rg_name, nr_of_resources, total_cost"
report_lines.append(report_header)
resourcegroups = get_resourcegroups()
for resourcegroup in resourcegroups:
    rg_name = resourcegroup["name"]
    rg_id = resourcegroup["id"]
    resources = get_resources_for_resourcegroup(rg_id)
    nr_of_resources = len(resources)
    total_cost = summarize_costs_for_resources(rg_id, rg_name, resources)
    cost_line_item = "{}, {}, {}, {}".format(rg_id, rg_name, nr_of_resources, total_cost)
    report_lines.append(cost_line_item)

# Step 2: Write to File
print("----->2 - write to file")
if OUTPUT_FORMAT == "json":
    with open(OUTPUT_FILE_NAME, 'w') as fp:
        json.dump(report_lines, fp)
elif OUTPUT_FORMAT == "csv":
    df = pd.read_json(json.dumps(report_lines))
    df.to_csv(OUTPUT_FILE_NAME)
else:
    with open(OUTPUT_FILE_NAME, 'w') as fp:
        json.dump(report_lines, fp)

print("----->The End")
