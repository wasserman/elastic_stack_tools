#!/bin/bash
for pipeline in `curl -s localhost:9200/_clsuter/state|jq .metadata.ingest.pipeline[].id -r`; do
  echo $pipeline
  curl -s localhost:9200/_cluster/state|jq ".metadata.ingest.pipeline[] | select(.id==\"$pipeline\") | .config" > $pipeline.pipeline.json
done
