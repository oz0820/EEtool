import csv
import os
from pathlib import Path


def ssim_stats(result_path, out_dir):
    b_list = []
    with open(result_path, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        for line in reader:
            b_list.append(line)

    b_index = b_list.pop(0)
    b_index.append("ssim Ave")
    b_index.append("ssim Bottom 0.1%")
    b_index.append("size(MB)")

    for i in range(len(b_list)):
        video_path = Path(out_dir+b_list[i][-1])
        ssim_txt_path = video_path.with_suffix(".ssim.txt")
        ssim_csv_path = ssim_txt_path.with_suffix(".csv")

        ssim_list = [["frame", "Y", "U", "V", "ALL", "SN"]]
        all_mux = []

        with open(ssim_txt_path, 'r', encoding='utf8') as f:
            for line in f.readlines():
                s1, s2, s3, s4, s5, s6 = line.split()
                frame = s1.split(":")[1]
                y = s2.split(":")[1]
                u = s3.split(":")[1]
                v = s4.split(":")[1]
                all = s5.split(":")[1]
                sn = s6[1:-1]
                ssim_list.append([frame, y, u, v, all, sn])
                all_mux.append(float(all))

        writer = csv.writer(ssim_csv_path.open('w', encoding='utf8', newline=""))
        writer.writerows(ssim_list)

        all_mux.sort()
        b_list[i].append(str(sum(all_mux)/(len(all_mux))))
        b_list[i].append(str(all_mux[int(len(all_mux)/1000)]))
        b_list[i].append(str(os.path.getsize(video_path)/1024/1024))
    b_list.insert(0, b_index)

    try:
        with open(result_path, 'w', encoding='utf8', newline="") as f:
            writer = csv.writer(f)
            writer.writerows(b_list)
    except PermissionError:
        print(f"{result_path}を開く権限がありません。")


if __name__ == "__main__":
    ssim_stats('result.csv', "out\\")
