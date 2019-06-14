from organise import *
import glob, os
import sys
import PIL.Image
import PIL.ExifTags
from datetime import datetime
import dlib
import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.patches as patches
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage,
                                  AnnotationBbox)
import PIL
import imghdr
import pickle

class MePhoto(object):
    '''MePhoto Class

    uses dlib to recognise and tag faces in images
    saves a json library.
    
    You can download a trained facial shape predictor and recognition model from:
         http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2
         http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2
    '''
    def __init__(self, **kwargs):
        predictor_path = kwargs.get('predictor_path', 'shape_predictor_5_face_landmarks.dat')
        face_rec_model_path = kwargs.get('face_rec_model_path', 'dlib_face_recognition_resnet_model_v1.dat')
        self.detector = dlib.get_frontal_face_detector()
        self.sp = dlib.shape_predictor(os.path.abspath(predictor_path))
        self.facerec = dlib.face_recognition_model_v1(
            os.path.abspath(face_rec_model_path))

        self.faces_file = kwargs.get('faces_file', 'mephoto_tags.pkl')
        if os.path.exists(os.path.abspath(self.faces_file)):
            with open(os.path.abspath(self.faces_file), 'rb') as f:
                self.known_faces = pickle.load(f)
        else:
            self.known_faces = []
    
    def face_detect(self, image, filename):
        print ("Running face detection")
            
        img = image.convert('L')
        # print (img, img.size)
        # TODO resize image to something reasonable
        size = list(img.size)
        try:
            orientation = image._getexif()[274]
        except KeyError as ke:
            print (ke)
            orientation = 1
        except TypeError as te:
            print (te)
            orientation = 1
        print ("orientation ", orientation)

        
        if orientation in [5,6,7,8]:
            tsize = (768,1024)
        else:
            tsize = (1024,768)
        ds = 0
        while size[0] > tsize[0] or size[1] > tsize[1]:
            size[0] = int(size[0]/2)
            size[1] = int(size[1]/2)
            ds += 1
            # print ("current resize", ds, size)
        zoom = 2**ds
        # size = [2 * i for i in size]
        # print ("current resize", ds, size)
            
        img = img.resize(size)
            
        data = np.array( img, dtype='uint8' )
        
        # The 1 in the second argument indicates that we should upsample the image
        # 1 time.  This will make everything bigger and allow us to detect more
        # faces.
        dets = self.detector(data, 1)
        print("Number of faces detected: {}".format(len(dets)))
        #ax.imshow(data, cmap='gray')
        if len(dets) == 0:
            return []
        faces = []
        for i, d in enumerate(dets):
            print("d",type(d))
            print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                i, d.left(), d.top(), d.right(), d.bottom()))
            
            # Get the landmarks/parts for the face in box d.
            shape = self.sp(data, d)
            # Compute the 128D vector that describes the face in img identified by
            # shape.  In general, if two face descriptor vectors have a Euclidean
            # distance between them less than 0.6 then they are from the same
            # person, otherwise they are from different people. Here we just print
            # the vector to the screen.
            rgb = np.array(image)
            face_descriptor = self.facerec.compute_face_descriptor(rgb, shape)
            name = self.get_name_from_descriptor(face_descriptor)
            ldescr = [ vec for vec in face_descriptor ]
            faces.append(
                {'name': name,
            'left': d.left() * zoom, 'top': d.top() * zoom, 
            'right': d.right() * zoom, 'bottom': d.bottom() * zoom,
            'descriptor': ldescr})

        return faces

    def add_entry(self, filename):
        img = PIL.Image.open(filename)
        exif_data = img._getexif()
        
        exif = {
            PIL.ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in PIL.ExifTags.TAGS
        }
        exif = {}
        for k, v in img._getexif().items():
            if k in PIL.ExifTags.TAGS:
                # print (PIL.ExifTags.TAGS[k])
                if isinstance(v, bytes):
                    exif[PIL.ExifTags.TAGS[k]] = str(v)
                else:
                    exif[PIL.ExifTags.TAGS[k]] = v
        dt = datetime.strptime(exif['DateTimeDigitized'],
                                    '%Y:%m:%d %H:%M:%S') 
        
        entry = {}
        entry['file'] = filename
        #entry['exif'] = exif
        entry['year'] = dt.year
        entry['month'] = dt.month
        entry['day'] = dt.day
        entry['time'] = '{}:{}:{}'.format(dt.hour, dt.minute, dt.second)
        # find faces in there
        
        entry['faces'] = self.face_detect(img, filename)
        # create a dlib rectangle as 
        # for face in entry['faces']:
        #     d = dlib.rectangle(face['left'], face['top'], face['right'],
        #                        face['bottom'] )3
        return entry

    def display_picture(self, entry):
        #canvas = FigureCanvas(Figure(figsize=(5, 3)))
        #self.image_canvas = canvas
        #self.vl.addWidget(canvas)
        #self.addToolBar(NavigationToolbar(canvas, self))

        #self._static_ax = canvas.figure.subplots()
        image = PIL.Image.open(entry['file'])
        plt.ion()
        fig, ax = plt.subplots()

        ax.imshow(image)
        rect = entry['faces']
        for i,el in enumerate(rect):
            d = (el['left'], el['top'], el['right'], el['bottom'])
            print (d)
            #rect = patches.Rectangle((d.left(),d.bottom()),xsize,ysize,linewidth=1,edgecolor='r',facecolor='none')
            face = patches.Rectangle((d[0],d[1]),d[3]-d[1],d[2]-d[0],
                   linewidth=1,edgecolor='r',facecolor='none')
            ax.add_patch(face)
            # annotation
            # Annotate the face position with a text box ('1')
            offsetbox = TextArea("{}".format(i), minimumdescent=False)

            ab = AnnotationBbox(offsetbox, (d[2],d[3]),
                            xybox=(0,0),
                            xycoords='data',
                            boxcoords="offset points",
                            arrowprops=dict(arrowstyle="->"))
            ax.add_artist(ab)
        plt.show()
        return plt
    def tag_entry(self, entry):
        for i,el in enumerate(entry['faces']):
            name = el['name'] 
            if el['name'] is not None:
                tag = input('Please confirm that the face {} is from {}: '.format(i,el['name']))
                if tag is not '':
                    print ("recording face as ", tag)
                    el['name'] = tag
                else:
                    print ("face confirmed ", el['name'])
            else:
                tag = input('Please insert name of face {}: '.format(i))
                if tag == '':
                    tag = None
                else:
                    print ("adding", tag, "to known faces")
                    face = {}
                    face['name'] = tag
                    face['descriptor'] = el['descriptor']
                    el.pop('descriptor')
                    self.known_faces.append(face)

                print ("recording face as ", tag)
                el['name'] = tag
                print ("el" , el['name'])
        return entry

    def get_name_from_descriptor(self, descriptor):
        print ("get_name_from_descriptor")
        dists = []
        for face in self.known_faces:
            v = face['descriptor']
            vdist = np.array(descriptor) - np.array(v)
            #dist = np.sqrt(vdist.dot(vdist))
            #dist = np.sqrt((vdist**2).sum())
            dist = np.linalg.norm(vdist)
            print ('Name ', face['name'], 'distance', dist)
            dists.append(dist)
        
        if len(dists) > 0:
            a = np.asarray(dists)
            i = np.argmin(a)

            if a[i] < 0.6:
                return self.known_faces[i]['name']
        return None

if __name__ == "__main__":
    start_dir = sys.argv[1]
    #pics = glob.glob(os.path.join(start_dir, '**/*'),recursive=True)
    #filenames = ['IMG_20190504_200610.jpg']
    filenames = glob.glob(os.path.join(start_dir, '**/*'),recursive=True)
    entries = []
    mp = MePhoto()
    for i,fname in enumerate(filenames):
        print ("Checking file ", fname)
        if imghdr.what(os.path.abspath(fname)) == 'jpeg':
            print ("Looking for faces in file ", fname)
            entry = mp.add_entry(os.path.abspath(fname))
            if len(entry['faces']) > 0:    
                plt = mp.display_picture(entry)
                entry = mp.tag_entry(entry)
                print (entry)
                plt.close()
            entries.append(entry)
    
    # print (json.dumps(entry))
    # save library to file
    with open('mephoto.json', 'w') as f:
        json.dump(entries, f)
    
    with open(os.path.abspath(mp.faces_file), 'wb') as f:
        pickle.dump(mp.known_faces, f)

        
    
    