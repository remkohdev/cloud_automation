#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# This software is supplied "as is". Use at own risk. No guarantees on        #
# fitness for purpose. IBM does not assume liability for the use of this      #
# program.                                                                    #
#                                                                             #
# Run: $ ./vsi-for-vpc-gen2.sh                                                #
# see:                                                                        #
# https://cloud.ibm.com/docs/vpc?topic=vpc-creating-a-vpc-using-cli           #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

echo "=====begin====="

# check required functions are installed
# tested with `docker run -it --rm busybox`
declare -F ibmcloud &>/dev/null && echo "ibmcloud found." || echo "ibmcloud not found." : exit 1
declare -F jq &>/dev/null && echo "jq found." || echo "jq not found." : exit 1

# read config file
source ./config.local
echo "----->config"
echo "naming_prefix=$naming_prefix"
echo "ibmcloud_apikey=$ibmcloud_apikey"
echo "ibmcloud_resource_group=$ibmcloud_resource_group"
echo "ibmcloud_region=$ibmcloud_region"
echo "ibmcloud_zone=$ibmcloud_zone"
echo "instances_per_subnet=$instances_per_subnet"
echo "instances_per_subnet_offset=$instances_per_subnet_offset"
echo "ssh_key_file_path=$ssh_key_file_path"
echo "ssh_key_name=$ssh_key_name"
echo "instance_image_id=$instance_image_id"
echo "instance_profile=$instance_profile"
echo "vpc_name=$vpc_name"
echo "subnet_name=$subnet_name"
echo "public_gateway_name=$public_gateway_name"


# set program variables
MY_VPC_NAME="$vpc_name"
echo "VPC_NAME=$MY_VPC_NAME"
MY_VPC_SUBNET_NAME="$subnet_name"
echo "VPC_SUBNET_NAME=$MY_VPC_SUBNET_NAME"
MY_ZONE="$ibmcloud_zone"
echo "ZONE=$MY_ZONE"
MY_SSH_KEY_NAME="$ssh_key_name"
echo "SSH_KEY_NAME=$MY_SSH_KEY_NAME"
# ibmcloud is instance-profiles
MY_PROFILE_NAME="$instance_profile"
echo "PROFILE_NAME=$MY_PROFILE_NAME"
#ibmcloud is images | grep windows
MY_IMAGE_ID="$instance_image_id"
echo "IMAGE_ID=$MY_IMAGE_ID"

# check required functions are installed
# tested with `docker run -it --rm busybox`
declare -F ibmcloud &>/dev/null && echo "ibmcloud found." || echo "ibmcloud not found." : exit 1
declare -F jq &>/dev/null && echo "jq found." || echo "jq not found." : exit 1

# ibmcloud login
echo "----->login"
ibmcloud login --apikey $ibmcloud_apikey
if [ "$?" = "1" ]; then
  echo "ERROR: ibmcloud login failed"
  exit 1
fi

echo "----->target"
# ibmcloud resource groups and regions
ibmcloud target -g $ibmcloud_resource_group -r $ibmcloud_region
if [ "$?" = "1" ]; then
  echo "ERROR: ibmcloud target failed"
  exit 1
fi
# gen2
ibmcloud is target --gen 2
if [ "$?" = "1" ]; then
  echo "ERROR: ibmcloud is target --gen2 failed"
  exit 1
fi

#ibmcloud is vpcs
MY_VPC_ID=$(ibmcloud is vpcs --output json | jq -r '.[] | select( .name=='\"$MY_VPC_NAME\"') | .id ')
echo "VPC_ID=$MY_VPC_ID"
MY_VPC_STATUS=$(ibmcloud is vpc $MY_VPC_ID --output json | jq -r '.status')
echo "VPC_STATUS=$MY_VPC_STATUS"
# status check
if [ "$?" = "1" ]; then
  echo "ERROR: ibmcloud is vpc failed"
  exit 1
fi
if [ "$MY_VPC_STATUS" != "available" ]; then
    echo "Error: vpc status: $MY_VPC_STATUS"
    exit 1
fi

MY_SG_ID=$(ibmcloud is vpc-sg $MY_VPC_ID --output json | jq -r '.id')
echo "SECURITYGROUP_ID (vpc-sg)=$MY_SG_ID"

# ibmcloud is zones  
MY_VPC_SUBNET_ID=$(ibmcloud is subnets --output json | jq -r '.[] | select( .name=='\"$MY_VPC_SUBNET_NAME\"') | .id ')
echo "VPC_SUBNET_ID=$MY_VPC_SUBNET_ID"
if [ "$?" = "1" ]; then
  echo "ERROR: ibmcloud is subnets failed"
  exit 1
fi
if [ -z "$MY_VPC_SUBNET_ID" ]; then
  echo "ERROR: subnet id not found for subnet $MY_VPC_SUBNET_NAME"
  exit 1
fi

MY_PUBLIC_GATEWAY_NAME=""
if [ "$public_gateway_name" == "" ]; then
  echo "-----> create a new public gateway"
  MY_PUBLIC_GATEWAY_NAME="$MY_VPC_SUBNET_NAME-gw-1"
  echo "PUBLIC_GATEWAY_NAME=$MY_PUBLIC_GATEWAY_NAME"

  echo "----->public-gateway-create"
  ibmcloud is public-gateway-create $MY_PUBLIC_GATEWAY_NAME $MY_VPC_ID $MY_ZONE
  if [ "$?" = "1" ]; then
    echo "ERROR: ibmcloud is public-gateway-create failed"
    exit 1
  fi

  MY_PUBLIC_GATEWAY_ID=$(ibmcloud is public-gateways --output json | jq -r '.[] | select( .name=='\"$MY_PUBLIC_GATEWAY_NAME\"') | .id')
  echo "PUBLIC_GATEWAY_ID=$MY_PUBLIC_GATEWAY_ID"
  if [ "$?" = "1" ]; then
    echo "ERROR: ibmcloud is public-gateways failed"
    exit 1
  fi
  if [ -z "$MY_PUBLIC_GATEWAY_ID" ]; then
    echo "ERROR: public gateway id not found: $MY_PUBLIC_GATEWAY_NAME"
    exit 1
  fi
  
  echo "----->subnet-update"
  ibmcloud is subnet-update $MY_VPC_SUBNET_ID --public-gateway-id $MY_PUBLIC_GATEWAY_ID
  if [ "$?" = "1" ]; then
    echo "ERROR: ibmcloud is subnet-update failed"
    exit 1
  fi

else
  echo "-----> use existing public gateway: $public_gateway_name"
  MY_PUBLIC_GATEWAY_NAME=$public_gateway_name
  echo "PUBLIC_GATEWAY_NAME=$MY_PUBLIC_GATEWAY_NAME"

  MY_PUBLIC_GATEWAY_ID=$(ibmcloud is public-gateways --output json | jq -r '.[] | select( .name=='\"$MY_PUBLIC_GATEWAY_NAME\"') | .id')
  echo "MY_PUBLIC_GATEWAY_ID=$MY_PUBLIC_GATEWAY_ID"
  if [ "$?" = "1" ]; then
    echo "ERROR: ibmcloud is public-gateways failed"
    exit 1
  fi
  if [ -z "$MY_PUBLIC_GATEWAY_ID" ]; then
    echo "ERROR: public gateway id not found: $MY_PUBLIC_GATEWAY_NAME"
    exit 1
  fi
fi

# confirm gateway exists and is attached to subnet
MY_PUBLIC_GATEWAY_ID_CHECK=$(ibmcloud is subnets --output json | jq -r '.[] | select( .name=='\"$MY_VPC_SUBNET_NAME\"') | .public_gateway.id ')
echo "PUBLIC_GATEWAY_ID=$MY_PUBLIC_GATEWAY_ID_CHECK"
if [ "$?" = "1" ]; then
  echo "ERROR: ibmcloud is subnets failed"
  exit 1
fi
if [ -z "$MY_PUBLIC_GATEWAY_ID_CHECK" ]; then
  echo "ERROR: public gateway id not found for subnet: $MY_VPC_SUBNET_NAME"
  exit 1
fi

# get floating ip of public gateway from subnet
MY_FLOATING_IP=$(ibmcloud is subnet-public-gateway $MY_VPC_SUBNET_ID --output json | jq -r '.floating_ip.address')
echo "FLOATING_IP=$MY_FLOATING_IP"
if [ "$?" = "1" ]; then
  echo "ERROR: ibmcloud is subnet-public-gateway failed"
  exit 1
fi

lowerlimit=$instances_per_subnet_offset
upperlimit=$((instances_per_subnet_offset + instances_per_subnet))
for instance_nr in $(seq -f "%03g" $upperlimit $lowerlimit);
  do
    echo "processing instance_nr=$instance_nr"

    MY_INSTANCE_NAME="$naming_prefix-$instance_nr"
    echo "INSTANCE_NAME=$MY_INSTANCE_NAME"

    MY_SSH_KEY_ID=$(ibmcloud is keys --output json | jq -r '.[] | select( .name=='\"$MY_SSH_KEY_NAME\"') | .id ')
    echo "SSH_KEY_ID=$MY_SSH_KEY_ID"
    if [ "$?" = "1" ]; then
      echo "ERROR: ibmcloud is keys failed"
      exit 1
    fi
    if [ -z "$MY_SSH_KEY_ID" ]; then
      echo "ERROR: ssh key id not found for: $MY_SSH_KEY_NAME"
      exit 1
    fi

    echo "----->instance-create"
    ibmcloud is instance-create $MY_INSTANCE_NAME $MY_VPC_ID $MY_ZONE $MY_PROFILE_NAME $MY_VPC_SUBNET_ID --image-id $MY_IMAGE_ID --key-ids $MY_SSH_KEY_ID
    if [ "$?" = "1" ]; then
      echo "ERROR: ibmcloud is instance-create failed"
      exit 1
    fi

    MY_INSTANCE_ID=$(ibmcloud is instances --output json | jq -r '.[] | select( .name=='\"$MY_INSTANCE_NAME\"') | .id ')
    echo "INSTANCE_ID=$MY_INSTANCE_ID"
    if [ "$?" = "1" ]; then
      echo "ERROR: ibmcloud is instances failed"
      exit 1
    fi
    if [ -z "$MY_INSTANCE_ID" ]; then
      echo "ERROR: instance id not found for: $MY_INSTANCE_NAME"
      exit 1
    fi

    # attach floating ip to NIC ID of instance
    NIC_ID=$(ibmcloud is instance-network-interfaces $MY_INSTANCE_ID --output json | jq -r '.[0].id')
    echo "NIC_ID=$NIC_ID"
    if [ "$?" = "1" ]; then
      echo "ERROR: ibmcloud is instance-network-interfaces failed"
      exit 1
    fi
    if [ -z "$NIC_ID" ]; then
      echo "ERROR: nic id not found for instance: $MY_INSTANCE_ID"
      exit 1
    fi
    MY_FLOATING_IP="$MY_INSTANCE_NAME-ip"
    echo "FLOATING_IP=$MY_FLOATING_IP"
    ibmcloud is floating-ip-reserve $MY_FLOATING_IP --nic-id $NIC_ID
    if [ "$?" = "1" ]; then
      echo "ERROR: ibmcloud is floating-ip-reserve failed"
      exit 1
    fi

    # get instance status: deleting | pending | starting | stopping | restarting | running | stopped
    MY_INSTANCE_STATUS=$(ibmcloud is instance $MY_INSTANCE_ID --output json | jq -r ".status")
    echo "INSTANCE_STATUS=$MY_INSTANCE_STATUS"
  done

echo "provisioning finished"
echo "----->VPCS"
ibmcloud is vpcs
echo "----->SUBNETS"
ibmcloud is subnets
echo "----->PUBLIC-GATEWAYS"
ibmcloud is public-gateways
echo "----->INSTANCES"
ibmcloud is instances

echo "=====end====="

echo "Exit status:"
echo $?