import tensorflow as tf
import numpy as np
import boto3
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.optimizers import SGD

train_path = '/data/Resize/Training/' # directory containing subsets of data with labels
valid_path = '/data/Resize/Validation/'
test_path = '/data/Resize/Test/'

TEST_NUM = 164542 # number of original test images

EPOCH_NUM = 30 # number of epochs to run
LEARN_RATE = 0.01 # how much the guesses adjust for loss each time to find the minimum
BATCH_SIZE = 64 # how many to process at once (greatest power of 2 that can ft in RAM)

train_datagen = keras.preprocessing.image.ImageDataGenerator()
valid_datagen = keras.preprocessing.image.ImageDataGenerator()
test_datagen = keras.preprocessing.image.ImageDataGenerator()

# Use the ImageDataGenerators to load the training data
train_gen = train_datagen.flow_from_directory(directory=train_path,
                                    target_size=(224,224), # size to resize images to
                                    color_mode='rgb', # color mode of the images
                                    batch_size=BATCH_SIZE, # how many images to process at once
                                    class_mode='categorical', # classify into categorical classes
                                    shuffle=True # shuffle order of images
)
valid_gen = valid_datagen.flow_from_directory(directory=valid_path,
                                    target_size=(224,224),
                                    color_mode='rgb',
                                    batch_size=BATCH_SIZE,
                                    class_mode='categorical',
                                    shuffle=True
)
test_gen = test_datagen.flow_from_directory(directory=test_path,
                                    target_size=(224,224),
                                    color_mode='rgb',
                                    batch_size=1,
                                    class_mode='categorical',
                                    shuffle=False
)

# Calculate the different step sizes based on the number of photos in the
# generator and the batch size
STEP_SIZE_TRAIN=train_gen.n//train_gen.batch_size
STEP_SIZE_VALID=valid_gen.n//valid_gen.batch_size

# set up model
# Sequential model. One layer feeds directly into another
model = keras.models.Sequential()
# basic layer for image processing
# extracts high level features (like edges) by applying a convolution
model.add(keras.layers.Conv2D(16, (3, 3), input_shape=(224, 224, 3)))
# rectified linear unit activation function, simplest way to add non-linearity to a categorical problem
model.add(keras.layers.Activation('relu'))
# Reduces the spatial size of convolved figure, descreasing computational requirements
# This is also useful for extracting rotational and positional invariant features
model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))

# the next two duplicates are to extract more features. each application should
#   extract a different feature from the spatially reduced output of the other layer
model.add(keras.layers.Conv2D(32, (3, 3)))
model.add(keras.layers.Activation('relu'))
model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))

model.add(keras.layers.Conv2D(64, (3, 3)))
model.add(keras.layers.Activation('relu'))
model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))

# this chunk is meant to prevent overfitting
# this converts our 3D feature maps to 1D feature vectors
model.add(keras.layers.Flatten())
# this densely connects all of the outputs from the previous layer
#   with a dimensionality equal to the parameter. Makes output from flatten more manageable
#   as it could be a ridiculously long array
model.add(keras.layers.Dense(64))
# another nonlinear activation
model.add(keras.layers.Activation('relu'))
# drops half of the input values randomly to prevent overfitting
model.add(keras.layers.Dropout(0.5))
# densely connects all inputs to prevent overfitting
# combines all outputs into one neuron
model.add(keras.layers.Dense(1))

# this chunk regularizes everything for output
# flatten back to a one dimenstional tensor
model.add(keras.layers.Flatten())
# densely connects with an output dimensionality of 64
# we do this first to reduce the number of neurons presented by flatten before inputting them into the output layer
model.add(keras.layers.Dense(64, activation='relu'))
# outputs with softmax, which is preferred for categorical applications
model.add(keras.layers.Dense(28, activation='softmax'))

model.summary() # print structure of the model

opt = keras.optimizers.SGD(lr=LEARN_RATE) # custom SGD optimizer

# compile the model with a loss function, optimizer, and the metric on which to judge it
model.compile(loss='categorical_crossentropy', # used when you have a categorical problem
            optimizer=opt, # custom defined above because the default adam optimizer kept crashing
            metrics=['accuracy'] # evaluate on accuracy
)

# train the neural net
with tf.device('/GPU:0'):
    model.fit_generator(generator=train_gen,
                        steps_per_epoch=STEP_SIZE_TRAIN, # number of steps in each epoch
                        validation_data=valid_gen,
                        validation_steps=STEP_SIZE_VALID,
                        epochs=EPOCH_NUM
    )

# evaluate the function using the test set
test_loss, test_acc = model.evaluate_generator(test_gen,
                                            TEST_NUM)

# print test accuracy
print('Accuracy: {}'.format(test_acc))
