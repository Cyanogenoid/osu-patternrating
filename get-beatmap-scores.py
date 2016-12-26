import json
import sys

import requests
from tqdm import tqdm

import api


with open('beatmaps.csv') as fd:
    beatmaps = fd.read().split(',')

beatmap_scores = {}

session = requests.Session()
url = "https://osu.ppy.sh/api/get_scores"
for i, beatmap in enumerate(tqdm(beatmaps)):
    payload = {
        'k': api.key,
        'b': beatmap,
    }
    success = False
    while not success:
        try:
            r = session.get(url, params=payload)
            r.raise_for_status()
            results = json.loads(r.text)
            success = True
        except Exception as e:
            print('ERROR ({}): {}'.format(beatmap, e), file=sys.stderr)

    for entry in results:
        beatmap_scores.setdefault(beatmap, {})[entry['user_id']] = entry['enabled_mods']
         
with open('beatmap-scores.json', 'w') as fd:
    fd.write(json.dumps(beatmap_scores))
