# -*- coding: utf-8 -*-

import ffmpeg
import os 
import fnmatch


def get_video_info(filepath):

    probe = ffmpeg.probe(filepath)
    
    # get bitrate in kbps format, only accurate to integer
    # The code is not suitable for the mkv format, a new branch is needed , and the correct container structure needs to be selected according to the suffix.
    
    video_bitrate = int( int(probe['streams'][0]['bit_rate'] )/1000 )
    
    print (str(video_bitrate) + " kbps" +"\n")



if __name__ == '__main__':
    test_file_path = "D:\\Users\\kkjb\\Videos\\Archived\\amdryzenlogo.mp4"

    video_path = "D:\\Users\\kkjb\\Videos\\Archived\\"

    video_list = []

    # find all mp4 files
    # case sensitive to uppercase letters 
    for path, dir_list, file_list in os.walk(video_path):
        for file_name in file_list:
            if file_name.endswith(('.mp4', '.MP4', '.Mp4', '.mP4')):
                video_list.append(os.path.join(path, file_name))
                pass




    get_video_info(test_file_path)

