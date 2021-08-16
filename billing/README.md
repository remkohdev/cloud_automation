# Billing and Usage

## Run

```bash
pip3 install -r requirements.txt
python3 report.py -o csv -d $BILLING_DATE -a $ACCOUNT_ID -t monthly -g $GROUP_BY
python3 report_cost_per_resource-group.py -o csv -d $BILLING_DATE -a $ACCOUNT_ID
```

## Fixes

Currently, fix report:

* remove first line `,0`
* remove all `"`

## Report

### Cost per Resource-Group

```bash
0,rg_id, rg_name, nr_of_resources, total_cost
3,057a526703fb42c39f40a8b817073127, user1-rg,30,1234.594507
22,5626cab685a049e58933bad6db310675, project1-rg,25,456.599
```

### Cost per Resource

```bash
,0,1,2
0,resource_id,resource_name,resource_billable_cost
1,76b7bf22-b443-47db-b3db-066ba2988f47,Watson Discovery,2600
2,983ea9a2-0fec-4021-8b70-8da5373394e5,Knowledge Studio,292.5
```

## Rendering Report in D3js

Copy the generated report `cost-report_2021-07_by-resource-20210815T195034611017.csv` to the `htdocs` folder.

To run the d3js report, start a web server and mount the htdocs volume as the web folder.

```bash
docker run -dit --name my-httpd -p 80:80 -v "$PWD/htdocs":/usr/local/apache2/htdocs/ httpd:2.4
```

In a browser, open

```bash
http://localhost/report.html?report_name=cost-report_2021-07_by-resource-20210815T195034611017.csv
```
