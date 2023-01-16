# -*- coding: utf-8 -*-

import ffmpeg
import os 
import fnmatch
import sys

def get_video_info(filepath):

    probe = ffmpeg.probe(filepath)
    
    # get bitrate in kbps format, only accurate to integer
    # The code is not suitable for the mkv format, a new branch is needed , and the correct container structure needs to be selected according to the suffix.
    
    video_dict_sample['filename']   = filepath
    # bps to kbps
    video_dict_sample["bit_rate"]        = str( int( int(probe['streams'][0]['bit_rate'] )/1000 ))
    
    video_dict_sample["codec_name"]     = probe['streams'][0]['codec_name']
    video_dict_sample["width"]          = probe['streams'][0]['width']
    video_dict_sample["height"]         = probe['streams'][0]['height']
    
    # add one info into the global dictionary
    video_info_list.append(video_dict_sample)

    # print (str(video_bitrate) + " kbps" +"\n")


def filter_mp4_video(video_path):

    video_list = []

    # find all mp4 files
    # case sensitive to uppercase or lowercase letters 
    for path, dir_list, file_list in os.walk(video_path):
        for file_name in file_list:
            if file_name.endswith(('.mp4', '.MP4', '.Mp4', '.mP4')):
                video_list.append(os.path.join(path, file_name))
                print(os.path.join(path, file_name))
                pass
    return video_list


    # test_file_path = "D:\\Users\\XXX\\Videos\\Archived\\amdryzenlogo.mp4"

    # video_path = "D:\\Users\\XXX\\Videos\\Archived\\"

    #get_video_info(test_file_path)

### two input folder path 

if __name__ == '__main__':

    video_info_list =[ ]

    video_dict_sample = {
        "filename": "GDM_Main.rfa",
        "codec_name": "AVC",
        "bit_rate": "2000",
        "width": "1920",
        "height": "1080",
    }

    if len(sys.argv) != 2:
        video_path = input('请拖入视频文件夹,并回车:\n')
            
        if video_path == '':
            print("no input")
            time.sleep(5)
            exit()
        else:
            mp4_list = filter_mp4_video(video_path.strip('"'))

            for i in range(len(mp4_list)):
                get_video_info(mp4_list[i])
                print(video_info_list[i])
             
    else:
        # print("参数1：")
        # print(sys.argv[1])
        # time.sleep(5)
        # print("参数2：")
        # print(sys.argv[1].strip('"'))
        # time.sleep(5)
        video_path = sys.argv[1].strip('"')
        mp4_list = filter_mp4_video(sys.argv[1].strip('"'))


        