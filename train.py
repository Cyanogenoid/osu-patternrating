import itertools

import numpy as np
np.random.seed(11037)
import h5py
from keras.models import Model
from keras.layers import Activation, Dense, Input, Dropout


PATTERN_LENGTH = 2


file = h5py.File('data.hdf5')
data = [file[k][()] for k in file]


def nwise(iterable, n):
    ''' s -> (s0, s1, ... sn), (s1, s2, ... sn+1), ... '''
    iters = itertools.tee(iterable, n)
    for i, it in enumerate(iters):
        for _ in range(i):
            next(it, None)
    return zip(*iters)


def normalize_angle_into_half_circle(angle):
    angle %= 2 * np.pi
    angle -= 2 * np.pi * (angle > np.pi)
    return np.abs(angle)


def process_pattern(pattern):
    time_and_magnitudes = pattern[:, :2].T.flatten()
    delta_angles = normalize_angle_into_half_circle(np.diff(pattern[:, 2])) - 0.5
    #previous_std = pattern[0, 3].flatten()
    circle_radius = pattern[0, 4].flatten()
    feature_vector = [time_and_magnitudes, delta_angles, circle_radius]
    feature_vector = np.concatenate(feature_vector)
    return feature_vector


def data_gen(data_src):
    for beatmap in data_src:
        for pattern in nwise(beatmap, PATTERN_LENGTH):
            pattern_data = np.array(pattern)
            x = process_pattern(pattern_data)
            y = pattern[-1][3]
            yield x, y


# time delta, movement magnitude, movement angle, stdev, circle size
all_objects = np.vstack(data)
mean = np.mean(all_objects, axis=0)
std = np.std(all_objects, axis=0)
with open('.train-stats', 'w') as fd:
    fd.write(','.join(map(str, [mean[0], mean[1], mean[4], std[0], std[1], std[4]])))


mean_of_angle_only = np.array([0, 0, 1, 0, 0]) * mean
data = [(beatmap - mean) / std + mean_of_angle_only for beatmap in data]
X = []
Y = []
for x, y in data_gen(data):
    X.append(x)
    Y.append(y)
X = np.array(X)
Y = np.array(Y)
rng = np.random.get_state()
np.random.shuffle(X)
np.random.set_state(rng)
np.random.shuffle(Y)


input = Input(shape=[X.shape[1]])
x = input
for i in range(8):
    x = Dense(128)(x)
    x = Activation('relu')(x)
    x = Dropout(i / 7 * 0.5)(x)
x = Dense(1)(x)

model = Model(input=input, output=x)
model.compile(loss='mse', optimizer='adam')

model.fit(X, Y, validation_split=0.2, batch_size=4096, nb_epoch=50)
model.save('test.model')
