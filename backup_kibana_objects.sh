#!/bin/bash
SERVER=https://your_host_goes_here:5601
declare -a types=("config" "url" "query" "index-pattern" "visualization" "canvas-element" "canvas-workpad" "graph-workspace" "timelion-sheet" "dashboard" "search" "tag" "lens" "map" "infrastructure-ui-source" "metrics-explorer-view" "inventory-view" "apm-indices")

# updated for ES 7.x
# Using -n option of curl for .netrc
for type in "${types[@]}"; do
    echo $type
    curl -s -n "$SERVER/api/kibana/management/saved_objects/_find?perPage=999&page=1&fields=id&type=$type" > $type.json
done
