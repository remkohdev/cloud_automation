# Users

## Usage

Remove lint errors:

```bash
yamllint -d relaxed valid-users-myteam.yaml
```

Create a config.local file:

```bash
cp config config.local
```

Run users report:

```bash
$ cd account-management/users
$ python3 report_users.py -c ../../config.local -u valid-users-myteam.yaml -o json

Running Users Report using Config File: ../../config.local, Ordered By: manager, Output format: json, Valid Users File: valid-users-myteam.yaml, Valid Users Output File: build/20211223T153812101564/valid_users_myteam_20211223T153812101564.json, IBM Cloud Account Output file: build/20211223T153812101564/ibmcloud_users_e65910fa61ce9072d64902d03f3d4774_20211223T153812101564.json, Ordered Users Report Output File: build/20211223T153812101564/users_report_orderedby_manager_20211223T153812101564.json, Unordered Users Report Output File: build/20211223T153812101564/users_report_20211223T153812101564.json

$ python3 report_users.py -c ../../config.local -u valid-users-myteam.yaml -o json -ob association

Running Users Report using Config File: ../../config.local, Ordered By: association, Output format: json, Valid Users File: valid-users-myteam.yaml, Valid Users Output File: build/20211223T153549420561/valid_users_myteam_20211223T153549420561.json, IBM Cloud Account Output file: build/20211223T153549420561/ibmcloud_users_e65910fa61ce9072d64902d03f3d4774_20211223T153549420561.json, Ordered Users Report Output File: build/20211223T153549420561/users_report_orderedby_association_20211223T153549420561.json, Unordered Users Report Output File: build/20211223T153549420561/users_report_20211223T153549420561.json
```

The file `valid-users-myteam.yaml` is a manually edited list of valid users in the organization. This list can be organized by association or by manager.

The users report ordered by manager creates a file `users_report_orderedby_manager_<datetime>`,  cross-checked users list organized by manager:

```json
[
    {
        "valid_users_by_manager": [
            {
                "email": "j.jones@company.com",
                "name": "Janet Jones",
                "association": "Development Team",
                "valid_users": [
                    {
                        "id": "1a2b3c4d5e6f7g8h9i0",
                        "iam_id": "IBMid-654321A0YZ",
                        "realm": "IBMid",
                        "user_id": "alis.smith@company.com",
                        "firstname": "Alisson",
                        "lastname": "Smith",
                        "state": "ACTIVE",
                        "sub_state": "",
                        "email": "alis.smith@company.com",
                        "phonenumber": "9728044604",
                        "altphonenumber": " ",
                        "photo": "https://cloud.ibm.com/avatar/v1/avatar/migrate-bluemix-photos-production/ ",
                        "account_id": "12345678901234567890",
                        "name": "Alisson Smith",
                        "identities": null,
                        "resourceGroups": [
                            "project1-rg"
                        ],
                        "manager": "j.jones@company.com",
                        "association": "Development Team"
                    },
```

The users report is then cross checked against the users in your IBM Cloud account.

```bash
ibmcloud account org-users $ORG_NAME -r $ORG_REGION --output json
```
