import datetime
import os

# 获取当前日期时间
now = datetime.datetime.now()
current_date = now.strftime("%m%d")

# 要重命名的纯中文文件名列表
chinese_filenames = ['综合源.m3u', '组播优选.txt', '综合源.txt']

# 获取当前目录下的所有文件
all_files = os.listdir(os.getcwd())

# 删除以数字加中文形式命名的文件
for old_filename in all_files:
    if any(char.isdigit() for char in old_filename) and (old_filename.endswith('.txt') or old_filename.endswith('.m3u')):
        full_old_path = os.path.join(os.getcwd(), old_filename)
        if os.path.exists(full_old_path):
            os.remove(full_old_path)
            print(f"Deleted {old_filename}")

# 重命名纯中文文件名的文件
for old_filename in all_files:
    if any(old_filename.endswith(init_filename) for init_filename in chinese_filenames):
        new_filename = f"{current_date}{old_filename}"
        full_old_path = os.path.join(os.getcwd(), old_filename)
        full_new_path = os.path.join(os.getcwd(), new_filename)
        os.rename(full_old_path, full_new_path)
        print(f"Renamed {old_filename} to {new_filename}")

