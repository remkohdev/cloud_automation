#!/usr/bin/env python

"""
## Run

```bash
pip3 install -r requirements.txt

BILLING_DATE=2021-08
ACCOUNT_ID=1234567890
GROUP_BY=[resource,resourcegroup]

python3 report.py --output_format csv --billing_date $BILLING_DATE --account_id $ACCOUNT_ID --report_type monthly --group_by $GROUP_BY
python3 report.py -o csv -d $BILLING_DATE -a $ACCOUNT_ID -t monthly -g $GROUP_BY
```

## Fixes

Currently, fix report:

* remove first line `,0`
* remove all `"`

## Report

```
0,rg_id, rg_name, nr_of_resources, total_cost
3,057a526703fb42c39f40a8b817073127, user1-rg,30,2184.594507
22,5626cab685a049e58933bad6db310675, project1-rg,25,2055.599
```

"""

import json
import argparse
import requests
import pandas as pd
import os.path
from datetime import datetime

with open("config.local") as jsonfile:
    config = json.load(jsonfile)

    IBM_CLOUD_APIKEY=config['credentials']['ibm_cloud_apikey']

#################################
#           Functions           #
#################################

def init():
    """parse arguments, validate input, set variables"""

    # commandline arguments
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(prog='python3 report.py')

    list_of_output_formats=["csv", "json"]
    parser.add_argument(
        "-o", "--output_format",
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

    parser.add_argument(
        "-t", "--report_type",
        required=True,
        help="Billing date in format yyyy-MM"
    )

    parser.add_argument(
        "-g", "--group_by",
        required=True,
        help="Billing date in format yyyy-MM"
    )

    # Parse arguments
    args = parser.parse_args()
    global OUTPUT_FORMAT
    OUTPUT_FORMAT=args.output_format
    global ACCOUNT_ID
    ACCOUNT_ID=args.account_id
    global BILLING_DATE
    BILLING_DATE=args.billing_date
    global REPORT_TYPE
    REPORT_TYPE=args.report_type
    global GROUP_BY
    GROUP_BY=args.group_by
    
    global OUTPUT_FILE_NAME
    now = datetime.now()
    date_time = now.strftime("%Y%m%dT%H%M%S%f")
    OUTPUT_FILE_NAME="cost-report_{}_by-{}-{}.{}".format(BILLING_DATE, GROUP_BY, date_time, OUTPUT_FORMAT)
  
    print(
        "Running Cost Report with Output format: {}, Output file: {}, Account id: {}, Billing date: {}, Report type: {}, Group by: {}"
        .format(
            OUTPUT_FORMAT,
            OUTPUT_FILE_NAME,
            ACCOUNT_ID,
            BILLING_DATE,
            REPORT_TYPE,
            GROUP_BY
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

def create_report_resources():
    """Cost per Resource"""
    report_lines = []
    report_header = ["resource_id", "resource_name", "resource_billable_cost"]
    report_lines.append(report_header)
    # get resource groups
    resources = get_resources()
    nr_of_resources = len(resources)
    
    for resource in resources:
        r_id = resource["resource_id"]
        r_name = resource["resource_name"]
        r_billable_cost = resource["billable_cost"]
        cost_line_item = [r_id, r_name, r_billable_cost]
        report_lines.append(cost_line_item)

    return report_lines


def create_report_groupby_resourcegroup():
    """Cost per ResourceGroup"""
    report_lines = []
    report_header = ["rg_id", "rg_name", "nr_of_resources", "total_cost"]
    report_lines.append(report_header)
    # get resource groups
    resourcegroups = get_resourcegroups()
    for resourcegroup in resourcegroups:
        rg_name = resourcegroup["name"]
        rg_id = resourcegroup["id"]
        # get resources
        resources = get_resources_for_resourcegroup(rg_id)
        nr_of_resources = len(resources)
        total_cost = summarize_costs_for_resources(rg_id, rg_name, resources)
        cost_line_item = [rg_id, rg_name, nr_of_resources, total_cost]
        report_lines.append(cost_line_item)

    return report_lines

def get_resources():
    """Get usage for all the resources and plans in an account for a given month"""

    # See: https://cloud.ibm.com/apidocs/metering-reporting#get-account-usage

    access_token = get_access_token()

    # include resource _names
    url1 = "https://billing.cloud.ibm.com/v4/accounts/%s/usage/%s?_names=1"
    url2 = url1 % (ACCOUNT_ID, BILLING_DATE)

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


def get_resources_for_resourcegroup(rg_id):
    """Get resource instance usage in a resource group"""

    # See: https://cloud.ibm.com/apidocs/metering-reporting#get-resource-usage-resource-group

    access_token = get_access_token()

    RESOURCE_GROUP_ID = rg_id
    # include resource _names
    url1 = "https://billing.cloud.ibm.com/v4/accounts/%s/resource_groups/%s/resource_instances/usage/%s?_names=1"
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


#################################
#              Main             #
#################################

print("----->Begin")
init()

# Create JSON Report
if GROUP_BY == "reourcegroup":
    report_lines = create_report_groupby_resourcegroup()
elif GROUP_BY == "resource":
    # note: grouping should be done in d3js rendering layer
    report_lines = create_report_resources()
else:
    report_lines = create_report_groupby_resourcegroup()

print(json.dumps(report_lines))

# Write to File
write_to_file(report_lines)

print("----->The End")
