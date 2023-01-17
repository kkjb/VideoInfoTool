# VideoInfoTool

read the bit rate and resolution

drag the folder into the terminal window  and press enter

the code will auto print the MP4 file format information  in the format below

{'filename': 'XXXXX.mp4', 'codec_name': 'h264', 'bit_rate': '1497', 'width': 1280, 'height': 720}

you can also modify the code for output audio info in the steam[1]


you must have ffmpeg-python and ffprobe.exe installed in C:\Windows\system32\ folder 

pip install ffmpeg-python


TO DO FUNCTIONS

1. single file as the input file
2. more containers supported, like mkv files
3. Catch exceptions for those abnormal cases
