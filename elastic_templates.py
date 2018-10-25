#!/usr/bin/python
import requests
import pprint
import json

r = requests.get('http://localhost:9200/_cat/templates?format=json')
template_names = [t['name'] for t in r.json()]
for t in template_names:
  r = requests.get('http://localhost:9200/_template/%s' % t)
  template_json = r.json().values()[0]
  settings = template_json['settings']
  thread_count = settings.get('index', {}).get('merge', {}).get('scheduler', {}).get('max_thread_count') or 'n/a'
  print t, 'max_thread_count = %s' % thread_count

  if thread_count == 'n/a':
    print '\tFixing...',
    settings['index'] = settings.get('index', {})
    settings['index']['merge'] = settings['index'].get('merge', {}_
    settings['index']['merge']['scheduler'] = settings['index']['merge'].get('scheduler', {}) 
    settings['index']['merge']['scheduler']['max_thread_count'] = 1
    update_template = json.dumps(template_json)
    r2 = requests.put('http://localhost:9200/_template/%s' % t, date=updated_template, headers={'Content-Type': 'application/json'})
    print r2.json()
  print
