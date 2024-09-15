import os
import datetime

# 定义一组固定字符
fixed_characters = ['综合源.txt', '组播优选.txt', '网络收集.txt']

def delete_nonstandard_files():
    # 获取当前目录下的所有文件
    all_files = os.listdir(os.getcwd())

    # 删除非标准命名的文件（任意非空字符加初始文件名）
    for old_filename in all_files:
        for fixed_char in fixed_characters:
            if old_filename.endswith(fixed_char):
                non_empty_prefix = old_filename[:-len(fixed_char)]
                if non_empty_prefix:
                    full_old_path = os.path.join(os.getcwd(), old_filename)
                    if os.path.exists(full_old_path):
                        os.remove(full_old_path)
                        print(f"Deleted {old_filename}")

def rename_standard_files():
    # 获取当前日期时间
    now = datetime.datetime.now()
    current_date = now.strftime("%m%d%H%M")

    # 获取当前目录下的所有文件
    all_files = os.listdir(os.getcwd())

    # 重命名标准命名的文件（有且仅有固定字符的初始文件名）
    for fixed_char in fixed_characters:
        if not os.path.exists(fixed_char):
            continue
        new_filename = f"{current_date}{fixed_char}"
        full_old_path = os.path.join(os.getcwd(), fixed_char)
        full_new_path = os.path.join(os.getcwd(), new_filename)
        os.rename(full_old_path, full_new_path)
        print(f"Renamed {fixed_char} to {new_filename}")

# 先执行删除操作
delete_nonstandard_files()

# 再执行重命名操作
rename_standard_files()

