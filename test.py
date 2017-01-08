import numpy as np
from keras.models import load_model


model = load_model('test.model')
model.summary()


with open('.train-stats') as fd:
    m0, m1, m4, std0, std1, std4 = map(float, fd.read().split(','))

bpm = 180
rhythm = 1/2
cs = 4

tdelta = np.array([60 * 1000 / bpm * rhythm for _ in range(2)])
tdelta = (tdelta - m0) / std0
circle_radius  = ((109 - 9 * cs) - m4) / std4

def evaluate(first_length, angle_between, second_length):
    '''
    first_length: distance of first movement in pixels
    angle_between: angle between the two movements,
                   between -0.5 (0 degrees) and 0.5 (180 degrees)
    second_length: distance of second movement in pixels
    '''
    lengths = (np.array([first_length, second_length]) - m1) / std1
    data = np.concatenate([tdelta, lengths, [angle_between, circle_radius]])
    data = data.reshape(1, data.shape[0])
    prediction = model.predict(data)
    print('difficulty score:', prediction)


print('\n### pattern difficulty ###')

print('back and forth')
evaluate(200, 0.5, 200)
print('very acute triangle')
evaluate(200, 0.375, 200)
print('acute triangle')
evaluate(200, 0.25, 200)
print('slightly acute triangle')
evaluate(200, 0.125, 200)
print('square')
evaluate(200, 0, 200)
print('slightly obtuse triangle')
evaluate(200, -0.125, 200)
print('obtuse triangle')
evaluate(200, -0.25, 200)
print('very obtuse triangle')
evaluate(200, -0.375, 200)
print('straight line')
evaluate(200, -0.5, 200)
