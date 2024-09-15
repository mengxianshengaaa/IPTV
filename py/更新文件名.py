import os

# 要重命名的文件名列表（初始文件名）
initial_filenames = ['综合源.m3u', '组播优选.txt', '综合源.txt']

# 获取当前目录下的所有文件
all_files = os.listdir(os.getcwd())

# 第一步：删除以数字加中文格式命名的 txt 和 m3u 文件
for old_filename in all_files:
    if (old_filename.endswith('.txt') or old_filename.endswith('.m3u')) and any(char.isdigit() for char in old_filename):
        full_old_path = os.path.join(os.getcwd(), old_filename)
        if os.path.exists(full_old_path):
            os.remove(full_old_path)
            print(f"Deleted {old_filename}")

# 第二步：重命名初始文件名的文件
for old_filename in all_files:
    if any(old_filename.endswith(init_filename) for init_filename in initial_filenames):
        new_filename = f"{old_filename[:-len(old_filename.split('.')[-1])]}_新命名{old_filename.split('.')[-1]}"
        full_old_path = os.path.join(os.getcwd(), old_filename)
        full_new_path = os.path.join(os.getcwd(), new_filename)
        os.rename(full_old_path, full_new_path)
        print(f"Renamed {old_filename} to {new_filename}")

