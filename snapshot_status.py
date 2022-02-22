"""
  Summarize snapshot sizes for a repository.

  Good for understanding space used on an object store when 
  you may not have direct access to the appliance or hosting account.
"""

import requests
import math
import sys
import argparse

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

parser = argparse.ArgumentParser()
parser.add_argument('--api-key', help='Elastic API key', required=True)
parser.add_argument('--repo-status', help='Snapshot repository')

args = parser.parse_args()
url = '_snapshot/_status'
headers = {'Authorization': 'ApiKey %s' % args.access_token}
r = requests.get('https://elk1:9200/' + url, headers=headers, verify=False)

if args.repo_status:
  url = '_snapshot/%s/_all' % args.repo_status
  r = requests.get('https://elk1:9200/' + url, headers=headers, verify=False)
  data = r.json()
  total_size_in_gb = 0
  print('%-55s\t%-24s\t%s\t%s' % ('SNAPSHOT', 'END_TIME', 'STATE', 'SIZE'))
  for snapshot in data['snapshots']:
    url = '_snapshot/%s/%s/_status' % (args.repo_status, snapshot['snapshot'])
    r = requests.get('https://elk1:9200/' + url, headers=headers, verify=False)
    data2 = r.json()
    stats_incremental = data2['snapshots'][0]['stats']['incremental']
    files = stats_incremental['file_count']
    size_in_gb = int(stats_incremental['size_in_bytes'] / (1024 * 1024 * 1024))
    total_size_in_gb += size_in_gb
    print('%s\t%s\t%s\t%s GB' % (snapshot['snapshot'], snapshot['end_time'], snapshot['state'], size_in_gb))
  print('\nTOTAL = %s GB' % total_size_in_gb)
  sys.exit(0)



data = r.json()
if r.status_code != 200:
  print('Access denied')
  sys.exit(r.status_code)

incremental = data['snapshots'][0]['stats']['incremental']
processed = data['snapshots'][0]['stats']['processed']
stats = data['snapshots'][0]['stats']
stats['start_time_in_millis']

files_progress = processed['file_count'] / incremental['file_count']
bytes_progress = processed['size_in_bytes'] / incremental['size_in_bytes']
bytes_remaining = incremental['size_in_bytes'] - processed['size_in_bytes']
byte_rate = processed['size_in_bytes'] / (stats['time_in_millis']/1000)

print('Snapshot: %s\n' % data['snapshots'][0]['snapshot'])

print('Files processed: %3.2f%% (%d/%d)' %  (100*files_progress, processed['file_count'], incremental['file_count']))
print('Bytes processed: %3.2f%% (%d GB/%d GB)' %  (100*bytes_progress, processed['size_in_bytes']/(1024*1024*1024), incremental['size_in_bytes']/(1024*1024*1024)))

print('Byte rate: %d MB/s' % (byte_rate / (1024*1024 )))
print('Elapsed: %d minutes' % ( stats['time_in_millis']/60000))
print('ETA %3.1f minutes' % ( (bytes_remaining / byte_rate) / 60))
