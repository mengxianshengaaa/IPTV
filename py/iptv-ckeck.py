import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# 要检测的文件和结果文件的文件名
input_file = '综合源.txt'
output_file = 'valid_sources.txt'




def is_link_valid(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return 200 <= response.status_code < 308
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return False

def process_file(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as file:
        lines = [line for line in file if line.strip() and not line.strip().startswith('#')]

    # 根据系统CPU核心数创建线程池
    with ThreadPoolExecutor() as executor:
        # 使用字典存储future和对应的URL
        future_to_line = {executor.submit(is_link_valid, line.split(',')[1].strip()): line for line in lines}

        with tqdm(total=len(future_to_line), desc="Processing lines") as progress:
            with open(output_filename, 'w', encoding='utf-8') as output_file:
                for future in as_completed(future_to_line):
                    line = future_to_line[future]
                    if future.result():
                        output_file.write(line)
                    progress.update(1)

# 执行函数
process_file(input_file, output_file)
print(f"有效链接已写入到 {output_file}")
