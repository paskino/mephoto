import numpy
import tensorflow
from tensorflow import keras
from tensorflow.keras.applications.mobilenet import MobileNet, \
        preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import Input, Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import SGD, Adam


import os, sys
# https://www.pyimagesearch.com/2019/06/24/change-input-shape-dimensions-for-fine-tuning-with-keras/

model = MobileNet(weights='imagenet')

img = image.load_img('data/P1090019.JPG', target_size=(224,224))
x = image.img_to_array(img)
x = numpy.expand_dims(x, axis=0)
x = preprocess_input(x)

print( x.shape )

# preds = model.predict(x)

# print('Predicted:', decode_predictions(preds, top=3)[0])

N,N,ch = 224,224,3
cnn = MobileNet(weights='imagenet', input_shape=(N,N,3), include_top=False)
#cnn.compile()
y = cnn.predict(x)
print (y.shape)


top = Sequential()
iseq = Input(shape = y.shape)
top.add( GlobalAveragePooling2D() )
top.add( Dense(1024,activation='relu'))
#top.add( Dense(256, activation='softmax'))
top.add( Dense(20, activation='softmax'))
#top(iseq)


# y = numpy.expand_dims(y, axis=0)
# print (y.shape)

# compile the model (should be done *after* setting layers to non-trainable)
# top.compile(optimizer='rmsprop', loss='categorical_crossentropy')

print (y.shape)
print (y[0].shape)
print (top.predict(y))



# add a global spatial average pooling layer
xin = cnn.output
xin = GlobalAveragePooling2D()(xin)
# let's add a fully-connected layer
xin = Dense(1024, activation='relu')(xin)
# and a logistic layer -- let's say we have 200 classes
predictions = Dense(20, activation='softmax')(xin)


# this is the model we will train
model = Model(inputs=cnn.input, outputs=predictions)

# first: train only the top layers (which were randomly initialized)
# i.e. freeze all convolutional InceptionV3 layers
for layer in cnn.layers:
    layer.trainable = False

# compile the model (should be done *after* setting layers to non-trainable)
model.compile(optimizer='rmsprop', loss='categorical_crossentropy')
print (model.predict(x))