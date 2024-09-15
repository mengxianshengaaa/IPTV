import datetime
import os

# 记录时间的文件路径
time_file_path = '上次更新时间.txt'

# 读取文本文件路径
text_file_path = '2.json'

try:
    print(f"Attempting to read text from {text_file_path}")
    with open(text_file_path, 'r', encoding="utf-8") as f:
        text_data = f.read()
    print(f"Successfully read text data: {text_data}")
except Exception as e:
    print(f"Failed to read text. Initializing empty data structure. Error: {e}")
    text_data = ""

# 尝试读取上次记录的时间
try:
    with open(time_file_path, 'r') as time_file:
        last_update_time = time_file.read()
except FileNotFoundError:
    last_update_time = ""

# 获取当前日期时间
now = datetime.datetime.now()
current_date = now.strftime("%m%d")

# 定义要替换的网址和对应的新内容
urls_to_replace = [
    ('综合源1', f"{current_date}综合源1"),
    ('综合源.txt', f"{current_date}综合源.txt"),
    ('组播优选1', f"{current_date}组播优选1"),
    ('组播优选.txt', f"{current_date}组播优选.txt"),
    # 添加更多需要替换的网址和新内容对
]

new_text_data = text_data
for old_url, new_content in urls_to_replace:
    if old_url in text_data:
        # 检查是否已有上次的时间
        if last_update_time and f"{last_update_time}{old_url}" in text_data:
            new_text_data = new_text_data.replace(f"{last_update_time}{old_url}", f"{current_date}{old_url}")
        else:
            new_text_data = new_text_data.replace(old_url, new_content)

print(f"Writing updated data to {text_file_path}")
with open(text_file_path, 'w', encoding="utf-8") as f:
    f.write(new_text_data)

# 更新记录时间的文件
with open(time_file_path, 'w') as time_file:
    time_file.write(current_date)
