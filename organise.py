'''
organise.py copies pictures from a directory and stores them in another based
picture date


'''
import PIL.Image
import PIL.ExifTags
from datetime import datetime
import os
import shutil
import sys
import hashlib
import glob

def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()

def organise_picture(filename, destination):
    current_image = os.path.abspath(filename)
    
    
    img = PIL.Image.open(current_image)
    exif_data = img._getexif()
    
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in PIL.ExifTags.TAGS
    }
    
    dt = datetime.strptime(exif['DateTimeDigitized'],
                                 '%Y:%m:%d %H:%M:%S') 
    
    #print ("should create directory {0}/{1}".format(
    #    dt.year,dt.month))
    
    copyto = os.path.join(destination, str(dt.year) , str(dt.month) , 
            os.path.basename(current_image))
    
    ydir = os.path.join(destination, str(dt.year) )
    mdir = os.path.join(ydir, str(dt.month))
    try:
        os.makedirs(mdir)
        print ("created " , mdir)
    except OSError as oe:
        #print (mdir, " exists : ", oe )
        pass
    print ("copy to " , copyto)
    shutil.copy2(current_image, copyto)

def organise_photos_in_dir(orig_dir, base_directory):
    all_pics = glob.glob(os.path.join(orig_dir,"**","*"), recursive=True)
    print (all_pics)
    return organise_list_of_photos(all_pics, base_directory)
def organise_list_of_photos(all_pics, base_directory):

    #all_pics = os.listdir(orig_dir)

    success = []
    fail = []
    for i,el in enumerate(all_pics):
        print ("Progress {0}/{1} {2}".format(i,len(all_pics),el))
        try:
            #current_picture = os.path.join(orig_dir, el)
            current_picture = el
            organise_picture(current_picture, base_directory)
            success.append(current_picture)
        except OSError as oe:
            fail.append(current_picture)
        except KeyError as ke:
            fail.append(current_picture)


    with open("organise.log","w") as f:
        f.write("Organising pictures \n  from {0}\n  to   {1}\n"
                .format(orig_dir, base_directory))
        f.write("Success: {}/{}\n".format(len(success),len(all_pics)))
        f.write("Fail   : {}/{}\n".format(len(fail),len(all_pics)))
        f.write("Failed file list:\n")
        for failed in fail:
            f.write("{}\n".format(failed))

if __name__ == '__main__':

    iarg = sys.argv[1]
    if iarg == "":
        orig_dir = os.path.abspath("/mnt/share/Pictures/nexus-s/2012-2013/")
    else:
        orig_dir = os.path.abspath(sys.argv[1])

    try :
        base_directory = os.path.abspath(sys.argv[2])
    except IndexError as ie:
        base_directory = os.path.join("/mnt","share","Pictures","tutte")
    print ("organising from {} to {}".format(orig_dir, base_directory))
    organise_photos_in_dir(orig_dir, base_directory)
