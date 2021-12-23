# Users

## Usage

Remove lint errors:

```bash
yamllint -d relaxed mailmap-hcbt-v1.yaml
```

Create a config.local file:

```bash
cp config config.local
```

Run users report:

```bash
cd account-management/users
python3 report_users.py -c ../../config.local -u valid-users-myteam.yaml -o json
```

The file `valid-users-myteam.yaml` is a manually edited list of valid users in the organization. This list can be organized by association or by manager.

Report type `by_manager` creates the following users list organized by manager:

```json
[
    {
        "manager": {
            "email": "j.jones@company.com",
            "name": "Janet Jones",
            "association": "Development Team"
        },
        "users": [
            {
                "email": "john.doe@company.com",
                "name": "John Doe",
                "title": "Cloud Solutions Architect",
                "identities": [
                    "joe.doe", "doe"
                ],
                "resourceGroups": [
                    "project1-rg"
                ],
                "manager": "j.jones@company.com",
                "association": "Development Team"
            },
            {
                "email": "alis.smith@company.com",
                "name": "Alisson Smith",
                "identities": [
                    "as", "smithy", "ally", "all"
                ],
                "resourceGroups": [
                    "project1-rg"
                ],
                "manager": "j.jones@company.com",
                "association": "Development Team"
            }
        ]
    }
]
```

The users report is then cross checked against the users in your IBM Cloud account.

```bash
ibmcloud account org-users $ORG_NAME -r $ORG_REGION --output json > build/org_users.json
```

Use cases:

1. user is valid and an account member,
1. user is valid and not an account member,
1. user is not valid (not in valid users) and an account member,
1. user is not valid (not in valid users) and not an account member,
1. user is temporary valid (in valid users for limited period) and an account member,
1. user is temporary valid (in valid users for limited period) and not an account member,
1. unknown

This results in a file `{}/report_users_{}_{}.{}` which add status fields to the users in the report:

* valid (keep)
* valid (add)
* invalid (remove, keep resources)
* invalid (remove, purge resources)
* unknown
