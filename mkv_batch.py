import os
import subprocess

# ==================== 配置区 ====================
# 1. mkvmerge 程序的位置
MKV_MERGE_PATH = r"D:\Program Files\mkvtoolnix-64-bit-97.0\mkvmerge.exe"

# 2. 视频和字幕的匹配原则
VIDEO_EXT = ".mp4"         # 视频后缀
SUB_SUFFIX = ".sc.ass"     # 字幕后缀（脚本会寻找：文件名 + 此后缀）
OUTPUT_FOLDER = "output"    # 输出文件夹名称

# 3. 轨道设置
SUB_LANG = "chi"           # 字幕语言代码 (chi 代表中文)
KEEP_TAGS = False          # 是否保留全局标签 (False 为剔除)
# ================================================

def run_batch():
    # 确保输出目录存在
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"已创建输出文件夹: {OUTPUT_FOLDER}")

    # 获取当前目录下所有文件
    files = os.listdir('.')
    video_files = [f for f in files if f.endswith(VIDEO_EXT)]

    if not video_files:
        print(f"未在当前目录找到 {VIDEO_EXT} 文件。")
        return

    print(f"找到 {len(video_files)} 个视频文件，准备开始混流...\n")

    for vid in video_files:
        name_without_ext = os.path.splitext(vid)[0]
        sub_file = name_without_ext + SUB_SUFFIX
        output_file = os.path.join(OUTPUT_FOLDER, name_without_ext + ".mkv")

        # 构建命令
        cmd = [MKV_MERGE_PATH, "-o", output_file]
        
        # 是否去掉全局标签
        if not KEEP_TAGS:
            cmd.append("--no-global-tags")
        
        # 添加视频文件
        cmd.append(vid)

        # 检查并添加字幕文件
        if os.path.exists(sub_file):
            # 设置字幕语言并添加
            cmd.extend(["--language", f"0:{SUB_LANG}", sub_file])
            print(f"成功匹配: {vid} + {sub_file}")
        else:
            print(f"??  未找到字幕: {sub_file}，将仅转换容器。")

        # 执行命令
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f"? 处理 {vid} 时出错: {e}")

    print("\n=======================================")
    print(f"任务完成！请查看 {OUTPUT_FOLDER} 文件夹。")

if __name__ == "__main__":
    run_batch()