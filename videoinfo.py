# -*- coding: utf-8 -*-

import os
import csv
import subprocess
import sys
import time
import json

# 获取视频和音频的详细信息
def get_video_audio_info(file_path):
    try:
        # 使用 ffprobe 获取视频流信息
        command = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
            'stream=codec_name,bit_rate,width,height', '-of', 'json', file_path
        ]
        video_info = json.loads(subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8'))['streams'][0]

        video_bitrate = int(video_info.get('bit_rate', 0)) / 1000 if video_info.get('bit_rate') else 'N/A'
        codec_name = video_info.get('codec_name', 'N/A')
        width = video_info.get('width', 'N/A')
        height = video_info.get('height', 'N/A')

        # 获取音频流信息
        audio_bitrates = []
        command_audio = [
            'ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries',
            'stream=codec_name,bit_rate', '-of', 'json', file_path
        ]
        audio_info = json.loads(subprocess.check_output(command_audio, stderr=subprocess.STDOUT).decode('utf-8'))
        
        for stream in audio_info['streams']:
            audio_bitrate = stream.get('bit_rate', 'N/A')
            audio_bitrates.append(audio_bitrate)

        return codec_name, video_bitrate, width, height, audio_bitrates

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None, None, None, None, None

# 遍历文件夹中的所有视频文件
def analyze_videos_in_folder(folder_path):
    result = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 支持更多的视频格式
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm')):
                file_path = os.path.join(root, file)
                
                codec_name, video_bitrate, width, height, audio_bitrates = get_video_audio_info(file_path)
                
                if codec_name:
                    # 写入文件信息到结果列表
                    for audio_bitrate in audio_bitrates:
                        result.append([file, codec_name, video_bitrate, width, height, audio_bitrate])
                else:
                    # 如果没有获取到码率，仍然记录文件名
                    result.append([file, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])
    
    # 将结果写入 CSV 文件
    with open(os.path.join(folder_path, '分析结果.csv'), mode='w', newline='', encoding='gbk') as f:
        writer = csv.writer(f)
        writer.writerow(['文件名', '编解码器', '视频码率kbps', '视频宽度', '视频高度', '音频码率kbps'])
        writer.writerows(result)

# 单个文件分析
def analyze_single_file(file_path):
    codec_name, video_bitrate, width, height, audio_bitrates = get_video_audio_info(file_path)
    
    if codec_name:
        print(f"File: {file_path}")
        print(f"Codec: {codec_name}")
        print(f"Video Bitrate: {video_bitrate} kbps")
        print(f"Resolution: {width}x{height}")
        print("Audio Bitrates:")
        for audio_bitrate in audio_bitrates:
            print(f"  {audio_bitrate} kbps")
    else:
        print(f"Error processing file {file_path}")

# 入口函数
if __name__ == '__main__':
    File_name = ''
    
    if len(sys.argv) != 2:
        File_name = input(
            '请拖入文件夹路径到软件图标上或者拖入终端窗口里,并回车:\n'
        )
        if File_name == '':
            print("no input")
            time.sleep(5)
            exit()
        else:
            analyze_videos_in_folder(File_name.strip('"'))
    else:
        File_name = sys.argv[1].strip('"')
        if os.path.isdir(File_name):
            analyze_videos_in_folder(File_name)
        else:
            analyze_single_file(File_name)
