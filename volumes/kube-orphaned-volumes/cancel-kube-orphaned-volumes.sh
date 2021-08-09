#!/bin/sh

counter=0
for volume in $(jq -c '.[]' output/clusterVolumes.json)
do
  volume_id=$(echo $volume | jq -r '.volume_id')
  volume_type=$(echo $volume | jq -r '.volume_type')
  cluster_id=$(echo $volume | jq -r '.cluster_id')
  cluster_exists=$(echo $volume | jq -r '.cluster_exists')
  last_row=$(echo $volume | jq -r '.last_row')
  if [ ! -z "$last_row" ] && [ "$last_row" != "null" ] && [ "$last_row"==true ]; then
    echo "INFO: deleted $counter volumes"
    echo "=====>done"
    exit 1
  fi

  if [ "$cluster_exists" == false ]; then
    echo "WARN: cancel $volume_type volume $volume_id"
    ibmcloud sl $volume_type volume-cancel $volume_id --immediate -f
    if [ "$?" = "1" ]; then
      echo "ERROR: ibmcloud sl $volume_type volume-cancel $volume_id failed"
      exit 1
    fi
    counter=$((counter+1))
  fi
done

echo "INFO: deleted $counter volumes"
