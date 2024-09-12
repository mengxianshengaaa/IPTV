import datetime

filenames = ["综合源.txt", "综合源.m3u", "组播优选.txt", "酒店优选.txt"]

now = datetime.datetime.now()
current_date = now.strftime("%d%h")

new_filenames = [f"{current_date}_{filename}" for filename in filenames]

print(new_filenames)
