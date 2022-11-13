import csv
import os
import random
from pathlib import Path


def ssim_stats(result_path, out_dir):
    csv_line = []
    with open(result_path, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        for line in reader:
            csv_line.append(line)

    csv_index = csv_line.pop(0)
    csv_index.append("ssim Ave")
    csv_index.append("ssim Bottom 0.1%")
    csv_index.append("size(MB)")

    for i in range(len(csv_line)):
        video_path = Path(out_dir+csv_line[i][-1])
        ssim_txt_path = video_path.with_suffix(".ssim.txt")
        ssim_csv_path = ssim_txt_path.with_suffix(".csv")

        ssim_csv_list = [["frame", "Y", "U", "V", "ALL", "SN"]]
        all_mux = []

        with open(ssim_txt_path, 'r', encoding='utf8') as f:
            for line in f.readlines():
                frame, y, u, v, all, sn = line.split()
                frame = frame.split(":")[1]
                y = y.split(":")[1]
                u = u.split(":")[1]
                v = v.split(":")[1]
                all = all.split(":")[1]
                sn = sn[1:-1]
                ssim_csv_list.append([frame, y, u, v, all, sn])
                all_mux.append(float(all))

        writer = csv.writer(ssim_csv_path.open('w', encoding='utf8', newline=""))
        writer.writerows(ssim_csv_list)

        all_mux.sort()
        csv_line[i].append(str(sum(all_mux)/(len(all_mux))))
        csv_line[i].append(str(all_mux[int(len(all_mux)/1000)]))
        csv_line[i].append(str(os.path.getsize(video_path)/1024/1024))
    csv_line.insert(0, csv_index)

    try:
        with open(result_path, 'w', encoding='utf8', newline="") as f:
            writer = csv.writer(f)
            writer.writerows(csv_line)
    except PermissionError:
        print(f"{result_path}を開く権限がありません。")

        ex_result_path = result_path+str(random.randint(1000, 9999))+'.csv'
        with open(ex_result_path, 'w', encoding='utf8', newline="") as f:
            writer = csv.writer(f)
            writer.writerows(csv_line)
        print(f"{ex_result_path}に保存しました。")


if __name__ == "__main__":
    ssim_stats('result.csv', "out\\")
