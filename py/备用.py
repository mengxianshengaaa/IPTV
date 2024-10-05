def append_text_between_files(file1_path, file2_path):
    with open(file1_path, 'r', encoding='utf-8') as file1:
        content1 = file1.read()
        lines1 = content1.split('\n')
        seen = set()
        unique_lines1 = []
        for line in lines1:
            if line not in seen:
                seen.add(line)
                unique_lines1.append(line)
    with open(file2_path, 'r', encoding='utf-8') as file2:
        content2 = file2.read()
        lines2 = content2.split('\n')
        seen = set()
        unique_lines2 = []
        for line in lines2:
            if line not in seen:
                seen.add(line)
                unique_lines2.append(line)
    combined_lines = unique_lines2 + unique_lines1
    with open(file2_path, 'w', encoding='utf-8') as file2:
        file2.write('\n'.join(combined_lines))
file_path1 = '网络收集.txt'
file_path2 = '综合源.txt'
append_text_between_files(file_path1, file_path2)


#TXT转M3U#
import datetime
def txt_to_m3u(input_file, output_file):
    # 读取txt文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 打开m3u文件并写入内容
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    current_time = now.strftime("%Y/%m/%d %H:%M")
    with open(output_file, 'w', encoding='utf-8') as f:  
        f.write('#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml" catchup="append" catchup-source="?playseek=${(b)yyyyMMddHHmmss}-${(e)yyyyMMddHHmmss}"\n')
        #f.write(f'#EXTINF:-1 group-title="更新时间",请您欣赏\n')    
        #f.write(f'https://vd2.bdstatic.com/mda-nk3am8nwdgqfy6nh/sc/cae_h264/1667555203921394810/mda-nk3am8nwdgqfy6nh.mp4\n')    
        #f.write(f'#EXTINF:-1 group-title="{current_time}",虚情的爱\n')    
        #f.write(f'https://vd2.bdstatic.com/mda-mi1dd05gmhwejdwn/sc/cae_h264/1630576203346678103/mda-mi1dd05gmhwejdwn.mp4\n')    
        # 初始化genre变量
        genre = ''
        # 遍历txt文件内容
        for line in lines:
            line = line.strip()
            if "," in line:  # 防止文件里面缺失",”号报错
                # if line:
                # 检查是否是genre行
                channel_name, channel_url = line.split(',', 1)
                if channel_url == '#genre#':
                    genre = channel_name
                    print(genre)
                else:
                    # 将频道信息写入m3u文件
                    f.write(f'#EXTINF:-1 tvg-logo="https://live.fanmingming.com/tv/{channel_name}.png" group-title="{genre}",{channel_name}\n')
                    f.write(f'{channel_url}\n')
# 将txt文件转换为m3u文件
txt_to_m3u('综合源.txt', '综合源.m3u')


import datetime
now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
current_time = now.strftime("%Y/%m/%d %H:%M")   #:%M
# 打开文本文件并将时间添加到开头
file_path = "综合源.m3u"
with open(file_path, 'r+', encoding='utf-8') as f:
    content = f.read()
    f.seek(0, 0)
    f.write(f'{content}\n')
    #f.write(f'#EXTINF:-1 group-title="更新时间",请您欣赏\n')    
    #f.write(f'http://em.21dtv.com/songs/60144971.mkv\n')    
    f.write(f'#EXTINF:-1 group-title="{current_time}更新",虚情的爱\n')    
    f.write(f'https://vd2.bdstatic.com/mda-mi1dd05gmhwejdwn/sc/cae_h264/1630576203346678103/mda-mi1dd05gmhwejdwn.mp4\n')   




import datetime
now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
current_time = now.strftime("%Y/%m/%d %H:%M")
# 打开文本文件并将时间添加到开头
file_path = "综合源.txt"
with open(file_path, 'r+', encoding='utf-8') as f:
    content = f.read()
    f.seek(0, 0)
    f.write(f'{content}\n')
    f.write(f'')
    #f.write(f'请您欣赏,https://vd2.bdstatic.com/mda-mi1dd05gmhwejdwn/sc/cae_h264/1630576203346678103/mda-mi1dd05gmhwejdwn.mp4\n')
    f.write(f'{current_time}更新,#genre#\n')
    f.write(f'虚情的爱,https://vd2.bdstatic.com/mda-mi1dd05gmhwejdwn/sc/cae_h264/1630576203346678103/mda-mi1dd05gmhwejdwn.mp4\n')
