#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# This software is supplied "as is". Use at own risk. No guarantees on        #
# fitness for purpose. IBM does not assume liability for the use of this      #
# program.                                                                    #
#                                                                             #                                                                         #
# see:                                                                        #
# https://cloud.ibm.com/docs/vpc?topic=vpc-creating-a-vpc-using-cli           #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# read config file
source ./config.local
echo "=====config====="
echo "naming_prefix=$naming_prefix"
echo "ibmcloud_apikey=$ibmcloud_apikey"
echo "ibmcloud_resource_group=$ibmcloud_resource_group"
echo "ibmcloud_region=$ibmcloud_region"
echo "ibmcloud_zone=$ibmcloud_zone"
echo "instances_per_subnet=$instances_per_subnet"
echo "instances_per_subnet_offset=$instances_per_subnet_offset"
echo "ssh_key_file_path=$ssh_key_file_path"
echo "instance_image_id=$instance_image_id"
echo "instance_profile=$instance_profile"
echo "vpc_name=$vpc_name"
echo "subnet_name=$subnet_name"
echo "public_gateway_name=$public_gateway_name"
echo "-----------------"

# set program variables
MY_VPC_NAME="$vpc_name"
echo "MY_VPC_NAME=$MY_VPC_NAME"
MY_VPC_SUBNET_NAME="$subnet_name"
echo "MY_VPC_SUBNET_NAME=$MY_VPC_SUBNET_NAME"
MY_ZONE="$ibmcloud_zone"
echo "$MY_ZONE"
MY_SSH_KEY_NAME="$MY_INSTANCE_NAME-sshkey"
echo "MY_SSH_KEY_NAME=$MY_SSH_KEY_NAME"
# ibmcloud is instance-profiles
MY_PROFILE_NAME="$instance_profile"
echo "MY_PROFILE_NAME=$MY_PROFILE_NAME"
#ibmcloud is images | grep windows
MY_IMAGE_ID="$instance_image_id"
echo "MY_IMAGE_ID=$MY_IMAGE_ID"

# ibmcloud login
echo "----->login"
ibmcloud login --apikey $ibmcloud_apikey
echo "----->target"
# ibmcloud resource groups
ibmcloud target -g $ibmcloud_resource_group
# ibmcloud regions
ibmcloud target -r $ibmcloud_region
# gen2
#ibmcloud is target --gen 2

#ibmcloud is vpcs
MY_VPC_ID=$(ibmcloud is vpcs --output json | jq -r '.[] | select( .name=='\"$MY_VPC_NAME\"') | .id ')
echo "MY_VPC_ID=$MY_VPC_ID"
MY_VPC_STATUS=$(ibmcloud is vpc $MY_VPC_ID --output json | jq -r '.status')
echo $MY_VPC_STATUS
# status check
if [ "$MY_VPC_STATUS" != "available" ]; then
    echo "Error: vpc status: $MY_VPC_STATUS"
    exit 1
fi

# ibmcloud is zones  
MY_VPC_SUBNET_ID=$(ibmcloud is subnets --output json | jq -r '.[] | select( .name=='\"$MY_VPC_SUBNET_NAME\"') | .id ')
echo "MY_VPC_SUBNET_ID=$MY_VPC_SUBNET_ID"

lowerlimit=$instances_per_subnet_offset
upperlimit=$((instances_per_subnet_offset + instances_per_subnet))
for instance_nr in $(seq -f "%03g" $upperlimit $lowerlimit);
  do

    echo "instance_nr=$instance_nr"
    # instance naming: ibm03radprodxxx  
    # 001-150 in subnet1  
    # 151-300 in subnet2

    MY_INSTANCE_NAME="$naming_prefix-$instance_nr"
    echo "MY_INSTANCE_NAME=$MY_INSTANCE_NAME"
    MY_INSTANCE_ID=$(ibmcloud is instances --output json | jq -r '.[] | select( .name=='\"$MY_INSTANCE_NAME\"') | .id ')
    if [ "$?" = "1" ]; then
      echo "ERROR: ibmcloud is instances failed"
      exit 1
    fi
    if [ -z "$MY_INSTANCE_ID" ]; then
      echo "ERROR: instance id not found for instance $MY_INSTANCE_NAME"
      exit 1
    fi
    echo "MY_INSTANCE_ID=$MY_INSTANCE_ID"

    NIC_ID=$(ibmcloud is instance-network-interfaces $MY_INSTANCE_ID --output json | jq -r '.[0].id')
    if [ "$?" = "1" ]; then
      echo "ERROR: ibmcloud is instance-network-interfaces failed"
      exit 1
    fi
    if [ -z "$NIC_ID" ]; then
      echo "ERROR: nic id not found for instance $MY_INSTANCE_ID"
      exit 1
    fi
    echo "NIC_ID=$NIC_ID"

    # for all
    NIC_FLOATING_IP=$(ibmcloud is instance-network-interface-floating-ips $MY_INSTANCE_ID $NIC_ID --output json | jq -r '.[0].id')
    if [ "$?" = "1" ]; then
      echo "ERROR: ibmcloud is instance-network-interface-floating-ips failed"
      exit 1
    fi
    echo "NIC_FLOATING_IP=$NIC_FLOATING_IP"
    #ibmcloud is instance-network-interface-floating-ip-remove $MY_INSTANCE_ID $NIC_ID $NIC_FLOATING_IP --force

    ibmcloud is floating-ip-release $NIC_FLOATING_IP --force
    if [ "$?" = "1" ]; then
      echo "ERROR: ibmcloud is floating-ip-release failed"
      exit 1
    fi

    echo "----->instance-delete"
    ibmcloud is instance-delete $MY_INSTANCE_ID --force
    if [ "$?" = "1" ]; then
      echo "ERROR: ibmcloud is instance-delete failed"
      exit 1
    fi

  done

echo "=====>cleanup finished"
echo "----->VPCS"
ibmcloud is vpcs
echo "----->SUBNETS"
ibmcloud is subnets
echo "----->PUBLIC-GATEWAYS"
ibmcloud is public-gateways
echo "----->INSTANCES"
ibmcloud is instances
