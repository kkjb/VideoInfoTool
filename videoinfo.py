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
        # 使用 ffprobe 获取视频流信息（v:0）
        command = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,bit_rate,width,height',
            '-of', 'json', file_path
        ]
        out = subprocess.check_output(command, stderr=subprocess.STDOUT)
        video_json = json.loads(out.decode('utf-8', errors='ignore'))
        streams = video_json.get('streams', [])
        if not streams:
            return None, None, None, None, None
        video_info = streams[0]

        def to_kbps(val):
            try:
                if val is None:
                    return 'N/A'
                # val 有时是字符串，有时是数字
                v = int(float(val))
                return int(round(v / 1000.0))
            except Exception:
                return 'N/A'

        video_bitrate = to_kbps(video_info.get('bit_rate'))
        codec_name = video_info.get('codec_name', 'N/A')
        width = video_info.get('width', 'N/A')
        height = video_info.get('height', 'N/A')

        # 获取音频流信息（所有音频流）
        audio_bitrates = []
        command_audio = [
            'ffprobe', '-v', 'error', '-select_streams', 'a',
            '-show_entries', 'stream=codec_name,bit_rate',
            '-of', 'json', file_path
        ]
        out_audio = subprocess.check_output(command_audio, stderr=subprocess.STDOUT)
        audio_info = json.loads(out_audio.decode('utf-8', errors='ignore'))
        a_streams = audio_info.get('streams', [])

        if not a_streams:
            audio_bitrates = ['N/A']
        else:
            for stream in a_streams:
                ab = stream.get('bit_rate')
                audio_bitrates.append(to_kbps(ab))

        return codec_name, video_bitrate, width, height, audio_bitrates

    except subprocess.CalledProcessError as e:
        print(f"ffprobe error for file {file_path}: {e}")
        return None, None, None, None, None
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None, None, None, None, None

# 遍历文件夹中的所有视频文件
def analyze_videos_in_folder(folder_path):
    result = []
    total = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm')):
                total += 1

    processed = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm')):
                processed += 1
                file_path = os.path.join(root, file)
                codec_name, video_bitrate, width, height, audio_bitrates = get_video_audio_info(file_path)

                if codec_name:
                    # 若有多个音频流，为每个音频流单独一行；没有音频流时 audio_bitrates 为 ['N/A']
                    for audio_bitrate in audio_bitrates:
                        result.append([file, codec_name, video_bitrate, width, height, audio_bitrate])
                else:
                    result.append([file, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])

                # 简单进度提示
                print(f"[{processed}/{total}] {file}")

    # 将结果写入 CSV 文件（保留原来的 GBK 编码以兼容中文 Excel）
    out_csv = os.path.join(folder_path, '分析结果.csv')
    with open(out_csv, mode='w', newline='', encoding='gbk', errors='replace') as f:
        writer = csv.writer(f)
        writer.writerow(['文件名', '编解码器', '视频码率(kbps)', '视频宽度', '视频高度', '音频码率(kbps)'])
        writer.writerows(result)

# 单个文件分析
def analyze_single_file(file_path):
    codec_name, video_bitrate, width, height, audio_bitrates = get_video_audio_info(file_path)

    if codec_name:
        print(f"File: {file_path}")
        print(f"Codec: {codec_name}")
        print(f"Video Bitrate: {video_bitrate} kbps" if video_bitrate != 'N/A' else "Video Bitrate: N/A")
        print(f"Resolution: {width}x{height}" if width != 'N/A' and height != 'N/A' else "Resolution: N/A")
        print("Audio Bitrates:")
        for audio_bitrate in (audio_bitrates or ['N/A']):
            print(f"  {audio_bitrate} kbps" if audio_bitrate != 'N/A' else "  N/A")
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
