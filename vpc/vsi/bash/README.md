# Create Virtual Server Instances (VSIs) on VPC Gen2

## Get Source Code

```bash
git clone https://github.com/remkohdev/cloud_automation.git
cd ibmcloud/vpc/vsi/bash
chmod +x vsi-for-vpc-gen2.sh
```

## Pre-requirements

* [IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cli-getting-started),
* [jq function](https://stedolan.github.io/jq/manual/),

## Configuration

Create and edit a new file "config.local",

```bash
cp config config.local
```

Configuration options:

* naming_prefix, instances are named using a naming template: "<naming_prefix>-<instance_nr>",
* ibmcloud_apikey=<your-ibmcloud-apikey>
* ibmcloud_resource_group, "default"
* ibmcloud_region, use "ibmcloud is regions" to list all available 
* ibmcloud_zone, use "ibmcloud is zones <region>" to list all available zones in a target region
* instances_per_subnet=1
* instances_per_subnet_offset=1
* ssh_key_file_path=./<naming-prefix>_id_rsa.pub, use an existing SSH Key File to create an IBM Cloud Key using "ibmcloud is key-create <key-name> @<key-file-path>",
* ssh_key_name=name of an existing IBM Cloud Key
* instance_image_id=image id of image, use "ibmcloud is images" to list all available images, e.g. image name "ibm-windows-server-2019-full-standard-amd64-1" has an image id "r014-6e732c5c-673b-42bd-911e-5a05e1c9b9b2",
* instance_profile=Use "ibmcloud is instance-profiles" to list all available instance profiles, e.g. "cx2-4x8"
* vpc_name=Using an existing VPC,
* subnet_name=Using an existing subnet,
* public_gateway_name=using an existing public gateway.

# Run

```bash
./vsi-for-vpc-gen2.sh
```
