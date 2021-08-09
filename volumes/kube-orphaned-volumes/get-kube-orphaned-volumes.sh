#!/bin/sh

parse_volumes () {
  volume_type=${1}
  echo "volume_type=$volume_type"
  ## get all volumes
  ## --column mount_addr not supported for block
  ## --column created_by 
  ## --column id --column username --column datacenter --column storage_type 
  ## --column capacity_gb --column bytes_used --column ip_addr --column active_transactions
  for volume in $(ibmcloud sl $volume_type volume-list --column id --column notes --output JSON | jq -c '.[]')
  do
    echo "$volume";
    volume_id=$(echo $volume | jq -r '.id');
    # cluster of attached volume;
    cluster_id=$(echo $volume | jq -r '.notes' | jq -r '.cluster');
    if [ "$?" = "1" ]; then
      echo "ERROR: getting cluster_id from notes failed"
      exit 1
    fi
    if [ -z "$cluster_id" ] || [ "$cluster_id" == "null" ]; then
      echo "ERROR: cluster_id not found"
      # TODO: only mark clusters with a cluster_id
      # echo "{ \"volume_id\": \"$volume_id\", \"volume_type\": \"$volume_type\", \"cluster_id\": null, \"cluster_exists\": null }," >> output/clusterVolumes.json;
    else

      grep $cluster_id output/clusters.lst > /dev/null; 
      # if volume's cluster is not in cluster list
      if [ $? -eq 1 ]; then
          echo "$volume_id, $cluster_id, false"
          echo "{ \"volume_id\": \"$volume_id\", \"volume_type\": \"$volume_type\", \"cluster_id\": \"$cluster_id\", \"cluster_exists\": false }," >> output/clusterVolumes.json;
      else
          echo "$volume_id, $cluster_id, true"
          echo "{ \"volume_id\": \"$volume_id\", \"volume_type\": \"$volume_type\", \"cluster_id\": \"$cluster_id\", \"cluster_exists\": true }," >> output/clusterVolumes.json;
      fi;
    fi
  done
}

echo "=====>begin";

if [ ! -d "output" ]; then
  mkdir output
fi

echo "=====>1";

# list of clusters;
# ibmcloud ks clusters | grep normal | awk '{ print $ 2}' > output/clusters.lst;
ibmcloud ks clusters | awk '{ print $ 2}' > output/clusters.lst;

echo "=====>2";

# process volumes, check against existing clusters
echo "[" >> output/clusterVolumes.json;
volume_type_block="block"
volume_type_file="file"
echo "=====>3";
parse_volumes $volume_type_block
echo "=====>4";
parse_volumes $volume_type_file
echo "=====>5";
# dummy row
echo "{ \"last_row\": true }" >> output/clusterVolumes.json;
echo "]" >> output/clusterVolumes.json;

echo "=====>done";
