import PIL.Image
import PIL.ExifTags
from datetime import datetime
import os
import shutil
import sys
import json
# import tqdm
# from tqdm import tqdm
import hashlib
# https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def organise_picture(filename, destination):
    current_image = os.path.abspath(filename)
    
    mdir = get_destination_directory(filename, destination)
    copyto = os.path.join(mdir, os.path.basename(current_image))
    # print ("copy to " , copyto)
    
    shutil.copy2(current_image, copyto)
    return (exif, mdir, os.path.basename(current_image))

def get_exif_info(filename):
    '''Tries to extract the exif info from filename
    
    :param filename: File name of the JPG picture
    :type filename: str, path
    returns a dictionary with the exif info. Returns an empty dictionary if the 
    exif info is not found.
    '''
    
    fname = os.path.abspath(filename)
    img = PIL.Image.open(fname)
    exif_data = img._getexif()
    if exif_data:
        exif = {
            PIL.ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in PIL.ExifTags.TAGS
        }
    
    else:
        exif = {}
    
    return exif

def get_picture_date_from_exif(exif):
    '''Extracts the month/year of picture taken from exif info
    
    :param exif: exif data
    :type exif: dict

    raises a KeyError if the exif does not contain DateTimeDigitized
    '''
    dt = datetime.strptime(exif['DateTimeDigitized'],
                                '%Y:%m:%d %H:%M:%S') 
    
    return (str(dt.year), str(dt.month))
    


def get_destination_directory(filename, base_directory):
    '''Returns the destination directory from exif info
    
    The directory name year/month is appended to base_directory. The year/month are
    extracted from the exif info. Should the exif information not be available it returns
    'generic'.

    '''

    exif = get_exif_info(filename)
    try:

        year, month = get_picture_date_from_exif(exif)
        return os.path.join(base_directory, year, month)
    except KeyError:
        return os.path.join(base_directory, 'generic')


    


def should_organise(filename, base_directory, method='stat'):
    '''Checks if a picture needs to be organised
    
    :param filename: filename of the picture to be organised
    :param base_directory: directory where you want to store the picture (organised in subdir year/month
    :param method: decision logic can be md5sum or stat (file size)
    '''
    fname = os.path.basename(filename)
    mdir = get_destination_directory(filename, base_directory)
    destination_fname = os.path.join(mdir, fname)
    if os.path.exists(destination_fname):
        if method == 'md5sum':
            dest_md5 = md5(destination_fname)
            local_md5 = md5(filename)
            return not dest_md5 == local_md5
        elif method == 'stat':
            dest_size = os.stat(destination_fname).st_size
            local_size = os.stat(filename).st_size
            return not dest_size == local_size
    else:
        return True

if __name__ == '__main__':

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


    mlib = []
    
    for i,el in enumerate(all_pics):
        # print ("Progress {0}/{1} {2}".format(i,len(all_pics),el))
        try:
            current_picture = os.path.join(orig_dir, el)
            # print (current_picture, base_directory)
            # tqdm.write ("",current_picture, base_directory)
            if should_organise(current_picture, base_directory, 'stat'):
                exif, mdir, fname = organise_picture(current_picture, base_directory)
                success.append(current_picture)
                exif_filtered = {}
                for k,v in exif.items():
                    if type(v) != bytes:
                        exif_filtered[k] = v
                md5sum = md5(current_picture)
                mlib.append({'filename': fname, 
                             'exif': exif_filtered, 
                             'directory': mdir,
                             'md5' : md5sum })
            else:
                # print("Skipping ", os.path.basename(current_picture))
                # tqdm.write("Skipping ", os.path.basename(current_picture))
                pass
        except OSError as oe:
            fail.append(current_picture)

    # if any picture has been copied
    if len(mlib) > 1:
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

    try:
        with open(os.path.join(base_directory, 'library.json'), "r") as f:
            remote_mlib = json.load(f)
    except FileNotFoundError as err:
        mlib = []
        print("Caught error: ", err, mlib)
        with open(os.path.join(base_directory, 'library.json'), "w") as fw:
            json.dump(mlib, fw)
    except json.decoder.JSONDecodeError as jde:
        print ("Some error in library", jde)

    try:
        with open(os.path.join(base_directory, 'library.json'), "w") as fw:
            json.dump(mlib, fw)
    except json.decoder.JSONDecodeError as jde:
        print ("Some error in library", jde)
