import datetime
import exifread
import shutil
import os
import piexif


def read_exif_date(file_path):
    with open(file_path, "rb") as f:
        exif_dict = exifread.process_file(f)
    if 'EXIF DateTimeOriginal' in exif_dict:
        datetime_str = str(exif_dict["EXIF DateTimeOriginal"])
    return datetime_str


def update_file_exif_timestamp(in_file, out_file, offset, tzdiff=0):
    in_file = os.path.abspath(in_file)
    out_file = os.path.abspath(out_file)
    
    with open(in_file,"rb") as f:
        exif_dict = exifread.process_file(f)

        
    if "EXIF DateTimeOriginal" in exif_dict:
        datetime_str = str(exif_dict["EXIF DateTimeOriginal"])
        picture_time = datetime.datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
        # apply offset and timezone difference
        new_datetime = picture_time + offset + datetime.timedelta(hours=tzdiff)
        print (new_datetime)
        
        # copy to new file
        shutil.copy(in_file, out_file)
        
        print ("\n\n\nSetting correct Exif datetime in destination file\n\n\n")
        exif_dict_dest = piexif.load(out_file)

        print (f"piexif.ImageIFD.DateTime: {piexif.ImageIFD.DateTime}")
        # exif_dict_dest['0th'][piexif.ImageIFD.DateTime] = str(new_datetime)
        exif_dict_dest['Exif'][piexif.ExifIFD.DateTimeOriginal] = str(new_datetime)
        exif_dict_dest['Exif'][piexif.ExifIFD.DateTimeDigitized] = str(new_datetime)

        
        exif_bytes = piexif.dump(exif_dict_dest)
        piexif.insert(exif_bytes, out_file)
                

cur_folder = os.path.abspath("/Users/edoardo.pasca/Pictures/Lumix/Berlin/darktable_exported")
dest_folder = os.path.abspath("./updated_time")
picture = "P1120880.jpg"
camera_time = datetime.datetime(2025,6,8, 17, 16, 0)
correct_time = datetime.datetime(2025,6,8, 15,21,0)
offset = correct_time - camera_time
tzdiff = 1
# correct_time = camera_time + offset + tz
print (f"Offset: {offset}")

import glob
for picture in glob.glob(f"{cur_folder}/*.jpg"):

    update_file_exif_timestamp(os.path.join(cur_folder,picture),
                            os.path.join(dest_folder,"mod_" + picture),
                            offset,tzdiff)

    print( read_exif_date(os.path.join(dest_folder,"mod_" + picture)))

