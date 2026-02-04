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
def analyze_videos_in_folder(folder_path, recursive=True):
    result = []
    allowed_exts = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm')

    # 生成待处理的文件列表，根据 recursive 决定遍历方式
    def iter_files():
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    yield root, file
        else:
            try:
                with os.scandir(folder_path) as it:
                    for entry in it:
                        if entry.is_file():
                            yield folder_path, entry.name
            except Exception:
                return

    # 收集符合后缀的文件
    file_entries = []
    for root, file in iter_files():
        if file.lower().endswith(allowed_exts):
            file_entries.append((root, file))

    total = len(file_entries)
    processed = 0

    for root, file in file_entries:
        processed += 1
        file_path = os.path.join(root, file)
        codec_name, video_bitrate, width, height, audio_bitrates = get_video_audio_info(file_path)

        if codec_name:
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

    # 命令行支持:
    #   python videoinfo.py <path> [Y|N]
    # 交互支持: 询问是否遍历子目录（默认 Y）
    if len(sys.argv) == 1:
        File_name = input('请拖入文件夹路径到软件图标上或者拖入终端窗口里,并回车:\n')
        if File_name == '':
            print("no input")
            time.sleep(5)
            exit()
        yn = input('是否遍历子目录? (Y/N) [Y]: ').strip().lower()
        recursive = True if yn == '' or yn.startswith('y') else False
        analyze_videos_in_folder(File_name.strip('"'), recursive=recursive)
    else:
        File_name = sys.argv[1].strip('"')
        # 若提供了第二个命令行参数，则按其决定是否递归（Y/N），否则默认递归
        if len(sys.argv) >= 3:
            arg = sys.argv[2].strip().lower()
            recursive = True if arg.startswith('y') else False
        else:
            recursive = True

        if os.path.isdir(File_name):
            analyze_videos_in_folder(File_name, recursive=recursive)
        else:
            analyze_single_file(File_name)
