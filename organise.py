import PIL.Image
import PIL.ExifTags
from datetime import datetime
import os
import shutil
import sys
import json



def organise_picture(filename, destination):
    current_image = os.path.abspath(filename)
    
    
    img = PIL.Image.open(current_image)
    exif_data = img._getexif()
    if exif_data:
        exif = {
            PIL.ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in PIL.ExifTags.TAGS
        }
    
        dt = datetime.strptime(exif['DateTimeDigitized'],
                                    '%Y:%m:%d %H:%M:%S') 
        
        #print ("should create directory {0}/{1}".format(
        #    dt.year,dt.month))
        
        
        ydir = os.path.join(destination, str(dt.year) )
        mdir = os.path.join(ydir, str(dt.month))
        try:
            os.makedirs(mdir)
            print ("created " , mdir)
        except OSError as oe:
            #print (mdir, " exists : ", oe )
            pass
    else:
        exif = {}
        mdir = os.path.join(destination, "generic")
        
    copyto = os.path.join(mdir, os.path.basename(current_image))
    print ("copy to " , copyto)
    
    shutil.copy2(current_image, copyto)
    return (exif, mdir, os.path.basename(current_image))


base_directory = os.path.join("/mnt","share","Pictures","tutte")
#base_directory = os.path.abspath("./store")

iarg = sys.argv[1]
if iarg == "":
    orig_dir = os.path.abspath("/mnt/share/Pictures/nexus-s/2012-2013/")
else:
    orig_dir = os.path.abspath(sys.argv[1])

all_pics = os.listdir(orig_dir)
success = []
fail = []


try:
    with open(os.path.join(base_directory, 'library.json'), "r") as f:
        mlib = json.load(f)
except FileNotFoundError as err:
    mlib = []
    print("Caught error: ", err, mlib)
    with open(os.path.join(base_directory, 'library.json'), "w") as fw:
        json.dump(mlib, fw)

for i,el in enumerate(all_pics):
    print ("Progress {0}/{1} {2}".format(i,len(all_pics),el))
    try:
        current_picture = os.path.join(orig_dir, el)
        exif, mdir, fname = organise_picture(current_picture, base_directory)
        success.append(current_picture)
        exif_filtered = {}
        for k,v in exif.items():
            if type(v) != bytes:
                exif_filtered[k] = v
        mlib.append({'filename': fname, 'exif': exif_filtered, 'directory': mdir})
            
    except OSError as oe:
        fail.append(current_picture)

for k,v in mlib[0]['exif'].items():
    print (k, type(v))


with open("organise.log","w") as f:
    f.write("Organising pictures \n  from {0}\n  to   {1}\n"
            .format(orig_dir, base_directory))
    f.write("Success: {}/{}\n".format(len(success),len(all_pics)))
    f.write("Fail   : {}/{}\n".format(len(fail),len(all_pics)))
    f.write("Failed file list:\n")
    for failed in fail:
        f.write("{}\n".format(failed))

with open(os.path.join(base_directory, 'library.json'), "w") as fw:
    json.dump(mlib, fw)

