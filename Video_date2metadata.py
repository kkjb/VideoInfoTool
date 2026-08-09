# -*- coding: utf-8 -*-

import os
import sys
import re
import subprocess


# ============================================================
# 配置
# ============================================================

FFMPEG = "ffmpeg.exe"

OUTPUT_DIR = "output"


# 支持的视频格式
VIDEO_EXT = {
    ".mp4",
    ".mov",
    ".m4v",
    ".mkv",
    ".avi",
    ".mts",
    ".m2ts",
    ".ts"
}


# 支持的图片格式
# 图片也使用 FFmpeg 处理，但需要单独处理
IMAGE_EXT = {
    ".jpg",
    ".jpeg",
    ".png",
    ".heic",
    ".webp",
    ".tif",
    ".tiff"
}


# ============================================================
# 从文件名读取时间
#
# 支持：
#
# VID_20260709_182307.mp4
# IMG_20260709_182307.jpg
# PXL_20260709_182307.jpg
#
# 也支持：
#
# 20260709_182307.mp4
# 20260709-182307.mp4
# ============================================================

def parse_datetime(filename):

    name = os.path.basename(filename)

    match = re.search(
        r"(\d{8})[_-](\d{6})",
        name
    )

    if not match:
        return None

    date_part = match.group(1)
    time_part = match.group(2)

    year = date_part[0:4]
    month = date_part[4:6]
    day = date_part[6:8]

    hour = time_part[0:2]
    minute = time_part[2:4]
    second = time_part[4:6]

    # 简单检查日期时间是否合法
    try:
        import datetime

        datetime.datetime.strptime(
            year + month + day + hour + minute + second,
            "%Y%m%d%H%M%S"
        )

    except ValueError:
        return None

    return (
        year + "-"
        + month + "-"
        + day
        + "T"
        + hour + ":"
        + minute + ":"
        + second
        + "+08:00"
    )


# ============================================================
# 检查 FFmpeg
# ============================================================

def check_ffmpeg():

    if os.path.isfile(FFMPEG):
        return True

    # 如果当前目录没有，尝试系统 PATH
    try:
        result = subprocess.run(
            [FFMPEG, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return result.returncode == 0

    except FileNotFoundError:
        return False


# ============================================================
# FFmpeg 写入视频 creation_time
# ============================================================

def process_video(src, dst, creation_time):

    cmd = [
        FFMPEG,

        "-hide_banner",

        "-loglevel",
        "error",

        "-y",

        "-i",
        src,

        # 保留所有视频、音频、字幕、数据流
        "-map",
        "0",

        # 不重新编码
        "-c",
        "copy",

        # 写入创建时间
        "-metadata",
        "creation_time=" + creation_time,

        dst
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:

        print()
        print("FFmpeg 处理失败:")
        print(src)
        print()
        print(result.stderr)

        return False

    return True


# ============================================================
# FFmpeg 写入图片时间
#
# JPEG 等图片可以使用 FFmpeg 写 metadata，
# 但 FFmpeg 对不同图片格式的 metadata 支持并不完全一致。
#
# 如果是图片，仍然尝试写 creation_time。
# ============================================================

def process_image(src, dst, creation_time):

    cmd = [
        FFMPEG,

        "-hide_banner",

        "-loglevel",
        "error",

        "-y",

        "-i",
        src,

        "-map",
        "0",

        "-c",
        "copy",

        "-metadata",
        "creation_time=" + creation_time,

        dst
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:

        print()
        print("FFmpeg 处理失败:")
        print(src)
        print()
        print(result.stderr)

        return False

    return True


# ============================================================
# 主程序
# ============================================================

def main():

    # --------------------------------------------------------
    # 获取拖入的文件夹
    # --------------------------------------------------------

    if len(sys.argv) < 2:

        print("请将文件夹直接拖到此 Python 脚本上。")

        input("\n按 Enter 退出...")

        return


    folder = sys.argv[1]


    if not os.path.isdir(folder):

        print("错误：输入的不是文件夹。")

        input("\n按 Enter 退出...")

        return


    # --------------------------------------------------------
    # 检查 FFmpeg
    # --------------------------------------------------------

    if not check_ffmpeg():

        print("错误：找不到 ffmpeg.exe")

        print()

        print("请将 ffmpeg.exe 放在：")

        print(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        print()

        print("或者将 FFmpeg 加入系统 PATH。")

        input("\n按 Enter 退出...")

        return


    # --------------------------------------------------------
    # 输出目录
    # --------------------------------------------------------

    output_dir = os.path.join(
        folder,
        OUTPUT_DIR
    )


    os.makedirs(
        output_dir,
        exist_ok=True
    )


    # --------------------------------------------------------
    # 统计
    # --------------------------------------------------------

    total = 0
    success = 0
    failed = 0
    skipped = 0


    print()
    print("========================================")
    print("文件名时间 → FFmpeg creation_time")
    print("========================================")
    print()

    print("输入目录:")
    print(folder)

    print()

    print("输出目录:")
    print(output_dir)

    print()

    print("时间按照文件名原样处理，时区固定为 +08:00")
    print()


    # --------------------------------------------------------
    # 遍历文件
    # --------------------------------------------------------

    for root, dirs, files in os.walk(folder):

        # 不处理 output
        dirs[:] = [
            d for d in dirs
            if os.path.abspath(
                os.path.join(root, d)
            ).lower()
            !=
            os.path.abspath(output_dir).lower()
        ]


        for filename in files:

            ext = os.path.splitext(
                filename
            )[1].lower()


            if (
                ext not in VIDEO_EXT
                and
                ext not in IMAGE_EXT
            ):
                continue


            total += 1


            src = os.path.join(
                root,
                filename
            )


            # ------------------------------------------------
            # 从文件名解析时间
            # ------------------------------------------------

            creation_time = parse_datetime(
                filename
            )


            if creation_time is None:

                print(
                    "[跳过] 无法识别时间:",
                    filename
                )

                skipped += 1

                continue


            # ------------------------------------------------
            # 输出文件名
            #
            # 所有文件统一放到 output
            # ------------------------------------------------

            dst = os.path.join(
                output_dir,
                filename
            )


            print(
                "[处理]",
                filename
            )

            print(
                "       creation_time =",
                creation_time
            )


            # ------------------------------------------------
            # 视频
            # ------------------------------------------------

            if ext in VIDEO_EXT:

                result = process_video(
                    src,
                    dst,
                    creation_time
                )


            # ------------------------------------------------
            # 图片
            # ------------------------------------------------

            else:

                result = process_image(
                    src,
                    dst,
                    creation_time
                )


            if result:

                success += 1

                print(
                    "       OK"
                )

            else:

                failed += 1

                print(
                    "       FAILED"
                )


            print()


    # --------------------------------------------------------
    # 完成
    # --------------------------------------------------------

    print()
    print("========================================")
    print("处理完成")
    print("========================================")

    print(
        "发现文件:",
        total
    )

    print(
        "成功:",
        success
    )

    print(
        "失败:",
        failed
    )

    print(
        "跳过:",
        skipped
    )

    print()

    print(
        "输出目录:",
        output_dir
    )

    print()

    input("按 Enter 退出...")


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":
    main()