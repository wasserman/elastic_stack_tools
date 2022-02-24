#!/bin/bash

###############
#
# Iterate through pipelines, saving off each to a file via API
# - https://www.elastic.co/guide/en/kibana/current/logstash-configuration-management-api.html
# 
# Assuming Python json library is present to pretty format, but that part can be removed if unavailable or replaced with jq.
# Worked with Elastic/Kibana 7.13
#
# Uses ~/.netrc to keep the passwords out of this file.
# 
# Sample .netrc format:
# 
# machine your_host_goes_here
# login elastic_user_with_kibana_access
# password password_goes_here
#
###############

SERVER=https://your_server_goes_here

echo Saving logstash_pipeline_list.json because it contains last_modified timestamp.
curl -s -n $SERVER/api/logstash/pipelines | python -mjson.tool > logstash_pipeline_list.json

PIPELINES=`cat logstash_pipeline_list.json | grep '"id":' | tr -d '\n' | tr -d '  ' | sed 's/\"id\"://g' | tr -d '"' | tr ',' ' '`

for pipeline_id in $PIPELINES; do
    echo Saving $pipeline_id to $pipeline_id.logstash_pipeline.json
    curl -s -n $SERVER/api/logstash/pipeline/$pipeline_id | python -mjson.tool > $pipeline_id.logstash_pipeline.json
    # Parse json in Python 2.x (maybe 3.x works too) and pull out pipeline blob and dump it to a text file for easier review.
    # Ensure UTF-8 is enabled so funny characters don't break things.  Clean up cr/lf to use the OS specific one instead of assuming always non-Windows.
    PYTHONIOENCODING=UTF-8 python > $pipeline_id.logstash_pipeline.txt <<HEREDOC
import json, os, re
# Redact passwords that aren't referenced via variables like \${...}
# Include escaped backslashes since the raw pipeline content in the json double escapes out quotes.
redact = re.compile(r'password\s+=>\s+(\\\\){0,1}\"(?!\${[^"]+}).*?\"')

d = open('$pipeline_id.logstash_pipeline.json','r').read()

# Rewrite file, leaving REDACTED passwords without quotes to not silently fail credentials until you put a password or variable back in.
open('$pipeline_id.logstash_pipeline.json','w').write(redact.sub('password => REDACTED', d))

# Output to stdout redacted pipeline content in pretty form.  Again, no quotes around REDACTED to force you to fix the passwords.
txt = redact.sub('password => REDACTED', json.loads(d)['pipeline'] )

print(txt.replace('\r\n', os.linesep))
HEREDOC
done
