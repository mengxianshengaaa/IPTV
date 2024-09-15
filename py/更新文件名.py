import os
import datetime

# 记录时间的文件路径
time_file_path = '上次更新时间.txt'

# 定义一组固定字符
fixed_characters = ['综合源.txt', '组播优选.txt', '综合源.m3u']

def delete_files():
    try:
        # 尝试读取上次记录的时间
        with open(time_file_path, 'r') as time_file:
            last_update_time = time_file.read()
        print(f"Last update time read: {last_update_time}")
    except FileNotFoundError:
        last_update_time = ""

    # 获取当前目录下的所有文件
    all_files = os.listdir(os.getcwd())

    # 删除非空字符加初始文件名的文件
    for old_filename in all_files:
        for fixed_char in fixed_characters:
            if old_filename.endswith(fixed_char):
                non_empty_prefix = old_filename[:-len(fixed_char)]
                if non_empty_prefix and not old_filename.startswith(last_update_time):
                    full_old_path = os.path.join(os.getcwd(), old_filename)
                    if os.path.exists(full_old_path):
                        os.remove(full_old_path)
                        print(f"Deleted {old_filename}")

def rename_files():
    try:
        # 尝试读取上次记录的时间
        with open(time_file_path, 'r') as time_file:
            last_update_time = time_file.read()
        print(f"Last update time read: {last_update_time}")
    except FileNotFoundError:
        last_update_time = ""

    # 获取当前日期时间
    now = datetime.datetime.now()
    current_date = now.strftime("%m%d%H%M")

    # 获取当前目录下的所有文件
    all_files = os.listdir(os.getcwd())

    # 重命名初始文件名的文件
    for old_filename in all_files:
        for fixed_char in fixed_characters:
            if old_filename.endswith(fixed_char):
                new_filename = f"{current_date}{old_filename}"
                full_old_path = os.path.join(os.getcwd(), old_filename)
                full_new_path = os.path.join(os.getcwd(), new_filename)
                os.rename(full_old_path, full_new_path)
                print(f"Renamed {old_filename} to {new_filename}")

    # 更新记录时间的文件
    with open(time_file_path, 'w') as time_file:
        time_file.write(current_date)

# 先执行删除操作
delete_files()

# 再执行重命名操作
rename_files()

