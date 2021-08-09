# Htdocs - D3JS Rendering

```bash
cp output/clusterVolume.json htdocs/clusterVolume.json

docker run -d --name orphaned-volumes-web -p 8080:80 -v $(pwd)/htdocs:/usr/local/apache2/htdocs/ httpd:2.4
```

TODO grep status!=normal clusters, and follow up for removal
example:

cluster check? false!=false
cluster c0pt217d015nbij4sjjg exists
cluster check? false!=true
ERROR: cluster_exists_check failed for cluster c0pt217d015nbij4sjjg: false!=true
ibmcloud ks cluster get --cluster c0pt217d015nbij4sjjg --output json

TODO last_row causes null cluster error in test

```bash
...
WARN: cancel file volume 231034024
OK
File volume 231034024 has been marked for immediate cancellation.
INFO: deleted 346 orphaned volumes
=====>done
❯ ibmcloud sl file volume-limits
Datacenter   MaximumAvailableCount   ProvisionedCount   
global       700                     463   
dal10        741                     320
```
