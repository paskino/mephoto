import PIL.Image
import PIL.ExifTags
from datetime import datetime
import os
import shutil



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
    
    print ("should create directory {0}/{1}".format(
        dt.year,dt.month))
    
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
    #shutil.copy2(current_image, copyto)


#base_directory = os.path.join("/mnt","share","Pictures","macchinanovaedo")
base_directory = os.path.abspath("/mnt/share/Pictures/nexus-s/2012-2013/")
all_pics = os.listdir(base_directory)
success = []
fail = []
for i,el in enumerate(all_pics):
    print ("Progress {0}/{1} {2}".format(i,len(all_pics),el))
    try:
        current_picture = os.path.join(base_directory, el)
        organise_picture(current_picture, 
            base_directory)
        success.append(current_picture)
    except OSError as oe:
        fail.append(current_picture)
    break


