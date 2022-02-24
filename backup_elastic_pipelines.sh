#!/bin/bash
SERVER=https://localhost:9200

# Assume .netrc is used for creds, so use curl "-n" option

# Dump all pipelines into json via curl so we don't need requests.
curl -nks $SERVER/_cluster/state?filter_path=metadata.ingest.pipeline > pipelines.json

# Avoid use of jq since it isn't ubiquitous.  
# Inline Python because I hope the json module is there and I don't know any other way.
python <<HEREDOC
import json, os
pipelines = json.loads(open('pipelines.json','r').read())['metadata']['ingest']['pipeline']
for pipeline in pipelines:
  filename = '%s.pipeline.json' % pipeline['id']
  print('Saving %s' % filename)
  open(filename, 'w').write(json.dumps(pipeline['config'], indent=4, sort_keys=True))
HEREDOC
