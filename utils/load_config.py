import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml


class GlobalCFG:
    out_dir = ""
    ffmpeg_path = ""
    input_file = []
    result_path = ""
    yml = {}

    encoder = []
    bitrate = []
    qp = []
    preset = []
    look_ahead = []
    profile = []
    gop = []

    loglevel = ""

    def __init__(self):
        while True:
            try:
                cfg_path = input("コンフィグファイルを指定してください。[config.yml]\n>")
                if cfg_path == "":
                    cfg_path = "config.yml"
                f = open(cfg_path, 'r', encoding='utf8')
                break
            except FileNotFoundError:
                print("コンフィグファイルを読み込めませんでした。")

        yml = yaml.safe_load(f)
        f.close()
        self.yml = yml
        self.yml_import(self.yml)

    # 整合チェックしながら設定を取り込む
    def yml_import(self, yml):
        def out_dir():
            if 'out_dir' in yml:
                if isinstance(yml['out_dir'], str):
                    self.out_dir = yml['out_dir']
                    if self.out_dir[-1:] != "\\":
                        self.out_dir += "\\"

                    sp = self.out_dir.split("<time>")
                    if len(sp) == 2:
                        self.out_dir = sp[0] + datetime.now().strftime('%Y%m%d_%H%M%S') + sp[1]
                    return
            print("出力先フォルダが指定されていません。")
            sys.exit(-101)

        def result_path():
            self.result_path = self.out_dir + "result.csv"

        def ffmpeg():
            def ffmpeg_get():
                if not os.path.isdir(".ffmpeg"):
                    os.mkdir(".ffmpeg")

                # .ffmpegフォルダに何か入ってたら消したい処理
                if len(os.listdir(".ffmpeg")) != 0:
                    print(".ffmpegフォルダ内のファイルを削除します。よろしいですか。[Y/n]")
                    if y_n():
                        for d in Path(".ffmpeg").glob("*"):
                            if d.is_dir():
                                shutil.rmtree(d)
                            else:
                                d.unlink(missing_ok=True)
                    else:
                        print("多分バグるので削除を許可してください。")
                        sys.exit(-1)

                url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
                print(f"ダウンロードします。\n{url}")
                subprocess.run(f"curl -L {url} -o .ffmpeg\\ffmpeg.zip", shell=False)
                print("解凍します。")
                shutil.unpack_archive(".ffmpeg\\ffmpeg.zip", ".ffmpeg")

                rm_list = []  # 解凍後削除するファイルたち
                for s in Path(".ffmpeg").glob("*"):
                    if s.is_dir():
                        if len(list(s.glob("bin"))) != 0:
                            for file in s.glob("bin\\*"):
                                shutil.move(file, ".ffmpeg")
                    rm_list.append(s)
                for s in rm_list:
                    if s.is_dir():
                        shutil.rmtree(s)
                    else:
                        s.unlink(missing_ok=True)
                return ".ffmpeg\\ffmpeg"

            if 'ffmpeg_path' in yml:
                if isinstance(yml['ffmpeg_path'], str):
                    self.ffmpeg_path = yml['ffmpeg_path']
                    return
            print("ffmpegのパスが指定されていません。")

            if os.path.isfile(".ffmpeg\\ffmpeg.exe"):
                print(".ffmpeg内のffmpegを使用しますか？[Y/n]")
                if y_n():
                    self.ffmpeg_path = ".ffmpeg\\ffmpeg"
                else:
                    pass

            try:
                subprocess.run("ffmpeg", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("システムPathに登録されているffmpegを使用しますか？[Y/n]")
                if y_n():
                    self.ffmpeg_path = "ffmpeg"
                    return
                else:
                    print("最新版をGithubからダウンロードしますか？[Y/n]")
                    if y_n():
                        self.ffmpeg_path = ffmpeg_get()
                        return
                    else:
                        print("ffmpegが登録されていません。")
                        sys.exit(-102)
            except FileNotFoundError:
                print("システムPathにffmpegが登録されていません。")
                print("最新版をGithubからダウンロードしますか？[Y/n]")
                if y_n():
                    self.ffmpeg_path = ffmpeg_get()
                    return
                else:
                    print("ffmpegが登録されていません。")
                    sys.exit(-102)

        def input_dir():
            if 'input_file' in yml:
                if isinstance(yml['input_file'], str):
                    self.input_file = yml['input_file']
                    return
            print("入力ファイルが指定されていません。\n")
            sys.exit(-103)

        def encoder():
            if 'encoder' in yml:
                if isinstance(yml['encoder'], list):
                    self.encoder = yml['encoder']
                    return
            print("エンコーダーが指定されていません。")
            sys.exit(-104)

        def bitrate_qp():
            def bitrate():
                if 'bitrate' in yml:
                    if isinstance(yml['bitrate'], list):
                        self.bitrate = yml['bitrate']
                        return
                self.bitrate = []

            def qp():
                if 'qp' in yml:
                    if isinstance(yml['qp'], list):
                        self.qp = yml['qp']
                        return
                self.qp = []

            bitrate()
            qp()

            if self.bitrate == [] and self.qp == []:
                print("ビットレート、品質がどちらも指定されていません。")
                sys.exit(-105)

        def preset():
            if 'preset' in yml:
                if isinstance(yml['preset'], list):
                    self.preset = yml['preset']
                    return
            print("presetが指定されていません。")
            sys.exit(-106)

        def look_ahead():
            if 'look_ahead' in yml:
                if isinstance(yml['look_ahead'], list):
                    self.look_ahead = yml['look_ahead']
                    return
            print("look_aheadが指定されていません。")
            sys.exit(-107)

        def gop():
            if 'gop' in yml:
                if isinstance(yml['gop'], list):
                    self.gop = yml['gop']
                    return
            print("gopが指定されていません。")
            sys.exit(-108)

        def profile():
            if 'profile' in yml:
                if isinstance(yml['profile'], list):
                    self.profile = yml['profile']
                    return
            print("profileが指定されていません。")
            sys.exit(-109)

        def loglevel():
            if 'loglevel' in yml:
                if isinstance(yml['loglevel'], str):
                    self.loglevel = yml['loglevel']
                    return
            self.loglevel = "info"
            sys.exit(-109)

        out_dir()
        result_path()
        ffmpeg()
        input_dir()
        encoder()
        bitrate_qp()
        preset()
        look_ahead()
        gop()
        profile()
        loglevel()


def y_n():
    while True:
        s = input()
        if s == 'N' or s == "n" or s == "No" or s == "NO" or s == "no" or s == "nO":
            return False
        if s == "" or s == "Y" or s == "y" or s == "Yes" or s == "yes":
            return True


if __name__ == "__main__":
    g = GlobalCFG()
