import PIL.Image
import PIL.ExifTags
from datetime import datetime
import os
import shutil


current_image = os.path.abspath('P1030090.JPG')


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

base_directory = os.path.join("/mnt","share","Pictures","macchinanovaedo")
copyto = os.path.join(base_directory, str(dt.year) , str(dt.month) , 
        os.path.basename(current_image))

ydir = os.path.join(base_directory, str(dt.year) )
mdir = os.path.join(ydir, str(dt.month))
try:
    os.makedirs(mdir)
    print ("created " , mdir)
except OSError as oe:
    print (mdir, " exists : ", oe )

print ("copy to " , copyto)
shutil.copy2(current_image, copyto)
