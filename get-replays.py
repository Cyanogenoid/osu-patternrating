import json
import sys
import os

import requests
from tqdm import tqdm

import api


with open('beatmap-scores.json') as fd:
    scores = json.loads(fd.read())

session = requests.Session()
url = "https://osu.ppy.sh/api/get_replay"
for beatmap in tqdm(sorted(scores.keys())):
    beatmap_path = os.path.join('data', beatmap)
    if not os.path.exists(beatmap_path):
        os.makedirs(beatmap_path)
    outdated = set(f[:-4] for f in os.listdir(beatmap_path) if f.endswith('.b64')) - set(scores[beatmap].keys())
    for user in outdated:
        os.remove(os.path.join(beatmap_path, '{}.b64'.format(user)))
    for user in tqdm(sorted(scores[beatmap])):
        path = os.path.join(beatmap_path, '{}.b64'.format(user))
        if os.path.exists(path):
            continue
        payload = {
            'k': api.key,
            'u': user,
            'b': beatmap,
        }
        success = False
        while not success:
            try:
                r = session.get(url, params=payload)
                r.raise_for_status()
                results = json.loads(r.text)
                replay = results['content']
                success = True
            except Exception as e:
                print('ERROR ({} on {}): {}'.format(user, beatmap, e), file=sys.stderr)

        with open(path, 'w') as fd:
            fd.write(replay)
