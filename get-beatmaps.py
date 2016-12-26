import json
import sys

import requests

import api


dates = ['2016-09-21', '2015-09-21']


beatmaps = []

url = "https://osu.ppy.sh/api/get_beatmaps"
for i, date in enumerate(dates):
    print('Requesting beatmaps since {}'.format(date))
    payload = {
        'k': api.key,
        'm': 0,  # osu! standard
        'since': date,
        'limit': 500,
    }
    success = False
    while not success:
        try:
            r = requests.get(url, params=payload)
            r.raise_for_status()
            results = json.loads(r.text)
            success = True
        except Exception as e:
            print('ERROR ({}): {}'.format(date, e), file=sys.stderr)

    for entry in results:
        beatmaps.append(entry['beatmap_id'])


beatmaps = sorted(set(beatmaps))
with open('beatmaps.csv', 'w') as fd:
    s = ','.join(beatmaps)
    fd.write(s)
