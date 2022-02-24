#!/root/venv/bin/python

"""
  Script will check the Filebeat registry file to determine progress.
  
  Useful in determining Filebeat lags, especially when a module or input is slow.
  Output goes to stdout and also sent as metrics to Elastic for visualization and monitoring.
  Good to use as a cron for measuring flow.
  
  Config in filebeat_registry_check.yml in same directory as this script.
  
    username: user
    password: password
    hosts:
    - https://elk1:9200
    - https://elk2:9200
    - https://elk3:9200

"""
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime
import time
from elasticsearch import Elasticsearch
import yaml
import pprint

import json
import os

script_path = os.path.dirname(__file__)
print('\n\nRunning: %s\n\n' % str(datetime.utcnow()))


config = yaml.load(open(script_path + '/filebeat_registry_check.yml'))

es = Elasticsearch(config['hosts'], verify_certs=False, timeout=300,
                   http_auth=(config['username'], config['password']))


# use system registry file, but sometimes using local one if testing with filebeat in user space

log = open('/var/lib/filebeat/registry/filebeat/log.json', 'r')
#log = open('data/registry/filebeat/log.json', 'r')
lines = log.readlines()

files = {}

for line in lines:
  data = json.loads(line)
  if data.get('v'):
    filename = data.get('v').get('source')
    offset = data.get('v').get('offset')
    size = os.path.getsize(filename)
    meta = filename.replace('_tcp', '').split('/')[-1:][0].split('_')
    log_date_tmp_array = meta[-1].split('.',3)
    log_date_tmp = '.'.join(log_date_tmp_array[0:3])
    try:
      log_date = datetime.strptime(log_date_tmp, '%Y.%m.%d')
    except Exception as e:
      # print("Skipping %s because no date like Y.m.d found in the name." % filename)
      continue

    label = meta[0] + '_' + meta[-1].replace('.log','')

    #print(label, filename)
        
    pct = (offset*100)/size

    files[filename] = {'offset': offset, 'size': size, 'source': meta[0], 'host': meta[1], 'log_date': log_date, 'filename': filename, 'percent_complete': pct, 'label': label}


timestamp = datetime.utcnow()

for k in sorted(files.keys()):
  v = files[k]
  if v['size'] == 0:
    continue
  if v['offset'] == v['size']:
    #print ('%s: up to date' % k)
    continue
  pct = (v['offset']*100) / v['size']
  print ("%s: offset=%s of %s MB  (%s%%)" % (k,v['offset']/pow(1024,2), v['size']/pow(1024,2), pct))
  v['timestamp'] = timestamp
  
  # Using index name outside of standard filebeat/metricbeat namespaces.  
  # My projects use metrics-* for other things so using metrx instead.
  d = es.index(index='metrx-fbeat-registry', body=v)
