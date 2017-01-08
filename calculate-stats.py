import os
from collections import defaultdict

import numpy as np
import h5py


def parse_beatmap(s):
    beatmap = list(map(float, s[:-1]))
    beatmap = np.array(beatmap).reshape(len(beatmap) // 3, 3)
    return beatmap


def parse_replay(s):
    replay = [float(x) if x else np.nan for x in s]
    replay = np.array(replay).reshape(len(replay) // 2, 2)
    return replay


def process_beatmap(path):
    with open(path) as fd:
        cs, *beatmap = next(fd).split(',')
        cs = float(cs)
        beatmap = parse_beatmap(beatmap)
        lines = fd.read().splitlines()

    mod = defaultdict(list)
    for i, line in enumerate(lines):
        hr, dt, *replay = line.split(',')
        hr, dt = int(hr), int(dt)
        mod[hr, dt].append(parse_replay(replay))

    for mod_combination in list(mod.keys()):
        mod[mod_combination] = np.array(mod[mod_combination])

    # beatmap info
    movement = np.diff(beatmap, axis=0)
    times_delta = movement[:, 0]
    movement_lengths = np.linalg.norm(movement[:, 1:], axis=1)
    movement_angles = np.arctan2(movement[:, 2], movement[:, 1])

    for mod_combination, replays in mod.items():
        if replays.shape[0] < 10:
            # too few replays to get anything useful out of it
            continue
        # replay info
        mean = np.nanmean(replays, axis=0)
        delta = beatmap[:, 1:] - mean
        stdev = np.mean(np.nanstd(replays, axis=0), axis=1)

        rate_multiplier = 1.5 if dt > 0 else 0.75 if dt < 0 else 1.0
        diff_multiplier = 1.4 if hr > 0 else 0.5 if hr < 0 else 1.0
        actual_radius = 109 - 9 * min(cs * diff_multiplier, 10)
        # first hitobject doesn't have any movement towards it, so it's ignored
        # data thus has to start with the second hitobject
        data = np.zeros([movement.shape[0], movement.shape[1] + 2])
        data[:, 0] = times_delta / rate_multiplier
        data[:, 1] = movement_lengths
        data[:, 2] = movement_angles
        data[:, 3] = stdev[1:] / actual_radius
        data[:, 4] = actual_radius
        # TODO mean difference if it seems useful
        # TODO correlation/covariance instead of mean of variance
        # TODO more beatmap difficulty metadata
        yield data


hdf5_path = 'data.hdf5'
if os.path.isfile(hdf5_path):
    os.remove(hdf5_path)
file = h5py.File(hdf5_path)
for beatmap in os.listdir('data'):
    if beatmap.endswith('.csv'):
        path = os.path.join('data', beatmap)
        for i, modded_beatmap in enumerate(process_beatmap(path)):
            file['{}-{}'.format(beatmap[:-4], i)] = modded_beatmap
