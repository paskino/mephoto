#!/usr/bin/python
# The contents of this file are in the public domain. See LICENSE_FOR_EXAMPLE_PROGRAMS.txt
# http://creativecommons.org/licenses/publicdomain/ 
#   This example program shows how to find frontal human faces in an image.  In
#   particular, it shows how you can take a list of images from the command
#   line and display each on the screen with red boxes overlaid on each human
#   face.
#
#   The examples/faces folder contains some jpg images of people.  You can run
#   this program on them and see the detections by executing the
#   following command:
#       ./face_detector.py ../examples/faces/*.jpg
#
#   This face detector is made using the now classic Histogram of Oriented
#   Gradients (HOG) feature combined with a linear classifier, an image
#   pyramid, and sliding window detection scheme.  This type of object detector
#   is fairly general and capable of detecting many types of semi-rigid objects
#   in addition to human faces.  Therefore, if you are interested in making
#   your own object detectors then read the train_object_detector.py example
#   program.  
#
#
# COMPILING/INSTALLING THE DLIB PYTHON INTERFACE
#   You can install dlib using the command:
#       pip install dlib
#
#   Alternatively, if you want to compile dlib yourself then go into the dlib
#   root folder and run:
#       python setup.py install
#
#   Compiling dlib should work on any operating system so long as you have
#   CMake installed.  On Ubuntu, this can be done easily by running the
#   command:
#       sudo apt-get install cmake
#
#   Also note that this example requires Numpy which can be installed
#   via the command:
#       pip install numpy

import sys

import dlib
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import h5py


detector = dlib.get_frontal_face_detector()
#win = dlib.image_window()
#lfw = np.load("../../raleigh/raleigh/examples/complete_lfw.npy")
lfwh5 = h5py.File("../../raleigh/raleigh/examples/complete_lfw.h5", "r")
lfw = lfwh5['lfw']
#im2 = im.point(table,'L')
facesize = []
maxx = 0
maxy = 0
for f in range(len(lfw)):
    print("Processing image: {}".format(f))
    fig,ax = plt.subplots(1)
    #img = Image.open(f).convert('L')
    img = lfw[f]
    data = np.asarray( img, dtype='uint8' )
    #print (img)
    # The 1 in the second argument indicates that we should upsample the image
    # 1 time.  This will make everything bigger and allow us to detect more
    # faces.
    #dets = detector(data, 1)
    dets, scores, idx = detector.run(data, 1, 0)
    print("Number of faces detected: {}".format(len(dets)))
    if len(dets) > 0:
        d = dets[0]
        xsize = d.right() - d.left()
        ysize = d.top() - d.bottom()
        if maxx < xsize:
            maxx = xsize
        if maxy < ysize:
            maxy = ysize
    if False:
        ax.imshow(data, cmap='gray')
        
        for i, d in enumerate(dets):
            print("Detection {} score {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                i, scores[i], d.left(), d.top(), d.right(), d.bottom()))
            # Create a Rectangle patch
            
            edgecolor = 'r'
            if i == 0:
                edgecolor = 'g'
            rect = patches.Rectangle((d.left(),d.bottom()),xsize,ysize,linewidth=1,
            edgecolor=edgecolor,facecolor='none')
            ax.add_patch(rect)
    #    win.clear_overlay()
    #    win.set_image(img)
    #    win.add_overlay(dets)
        plt.show()
        dlib.hit_enter_to_continue()

print ("Max box: ",maxx, maxy)
# Finally, if you really want to you can ask the detector to tell you the score
# for each detection.  The score is bigger for more confident detections.
# The third argument to run is an optional adjustment to the detection threshold,
# where a negative value will return more detections and a positive value fewer.
# Also, the idx tells you which of the face sub-detectors matched.  This can be
# used to broadly identify faces in different orientations.

#if (len(sys.argv[1:]) > 0):
#    #img = dlib.load_rgb_image(sys.argv[1])
#    img = Image.open(f).convert('L')
#    data = np.array( img, dtype='uint8' )
#    
#    dets, scores, idx = detector.run(data, 1, -1)
#    for i, d in enumerate(dets):
#        print("Detection {}, score: {}, face_type:{}".format(
#            d, scores[i], idx[i]))