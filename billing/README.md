# Billing and Usage

## Run

```bash
pip3 install -r requirements.txt
python3 report_cost_per_resource-group.py -o csv -d 2021-08 -a 1234567890
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
