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

class MePhoto(object):
    def __init__(self, **kwargs):
        self.detector = dlib.get_frontal_face_detector()
    
    def face_detect(self, image):
        print ("Running face detection")
            
        img = image.convert('L')
        print (img, img.size)
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
            print ("current resize", ds, size)
        zoom = 2**ds
        # size = [2 * i for i in size]
        print ("current resize", ds, size)
            
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
            faces.append(
                {'name': None,
            'left': d.left() * zoom, 'top': d.top() * zoom, 
            'right': d.right() * zoom, 'bottom': d.bottom() * zoom})
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
                print (PIL.ExifTags.TAGS[k])
                if isinstance(v, bytes):
                    exif[PIL.ExifTags.TAGS[k]] = str(v)
                else:
                    exif[PIL.ExifTags.TAGS[k]] = v
        dt = datetime.strptime(exif['DateTimeDigitized'],
                                    '%Y:%m:%d %H:%M:%S') 
        
        entry = {}
        entry['file'] = filename
        entry['exif'] = exif
        # find faces in there
        
        entry['faces'] = self.face_detect(img)
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
    def tag_entry(self, entry):
        for i,el in enumerate(entry['faces']):
            tag = input('Please insert name of face {}: '.format(i))
            if tag == '':
                tag = None
            print ("recording face as ", tag)
            el['name'] = tag
            print ("el" , el['name'])
        return entry

if __name__ == "__main__":
    #start_dir = sys.argv[1]
    #pics = glob.glob(os.path.join(start_dir, '**/*'),recursive=True)

    mp = MePhoto()
    entry= mp.add_entry('IMG_20190504_200610.jpg')
    mp.display_picture(entry)
    entry = mp.tag_entry(entry)
    

    print (entry)
    # print (json.dumps(entry))
    
    