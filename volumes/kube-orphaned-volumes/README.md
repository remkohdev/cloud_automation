# Cancel Orphaned Volumes

Login to IBM Cloud account,

```bash
ibmcloud login -sso
```

Optional, check your regions,

```bash
❯ ibmcloud regions
Listing regions...

Name            Display name   
au-syd          Sydney   
in-che          Chennai   
jp-osa          Osaka   
jp-tok          Tokyo   
kr-seo          Seoul   
eu-de           Frankfurt   
eu-gb           London   
ca-tor          Toronto   
us-south        Dallas   
us-south-test   Dallas Test   
us-east         Washington DC   
br-sao          Sao Paulo

```

## Run

Prepare,

```bash
cd volumes/kube-orphaned-volumes
ibmcloud login [-sso]
./get-kube-orphaned-volumes.sh
```

Check volume-limits,

```bash
$ ibmcloud sl file volume-limits
Datacenter   MaximumAvailableCount   ProvisionedCount   
global       700                     673   
dal10        741                     462
```

Cancel orphaned volumes,

```bash
$ ./cancel-kube-orphaned-volumes.sh
INFO: deleted 179 volumes

$ ibmcloud sl file volume-limits
Datacenter   MaximumAvailableCount   ProvisionedCount   
global       700                     524   
dal10        741                     318 

```

## Output

The file `output/clusterVolumes.json` will contain entries like,

```json
{ "volume_id": "165114506", "volume_type": "block", "cluster_id": "bt1vufgd0tk62gnhc17g", "cluster_exists": false },
```

```bash
ibmcloud ks cluster get --cluster $cluster_id
```

The cluster_exists boolean is used to test and remove volumes without cluster,

```bash
  if [ "$cluster_exists" == false ]; then
    echo "WARN: cancel $volume_type volume $volume_id"
    ibmcloud sl $volume_type volume-cancel $volume_id --immediate -f
```

```bash
volume_id=183766864
ibmcloud sl $volume_type volume-cancel $volume_id --immediate -f

ibmcloud sl block volume-detail $volume_id
```

## D3JS Rendering

```bash
cd ../../../..

cp output/clusterVolumes.json htdocs/clusterVolumes.json

docker run -d --name orphaned-volumes-web -p 8080:80 -v $(pwd)/htdocs:/usr/local/apache2/htdocs/ httpd:2.4

open http://localhost:8080
```
