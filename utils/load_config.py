import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml


class GlobalConfig:
    MESSAGE_SERVER_URL = ""
    MESSAGE_SERVER_KEY = ""
    SSIM_parallel_number = 1
    out_dir = ""
    ffmpeg_path = ""
    input_file = ""
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
        ini_path = 'EEtool.ini'
        # iniファイルなかったらとりあえず錬成して、初期値のまま続行
        if not os.access(ini_path, os.F_OK):
            with open(ini_path, "w", encoding='utf8') as f:
                f.write(
"""# SSIMの並列数を指定します。
SSIM_parallel_number: 2

# 進捗をWebAPIに投げつける設定です。
# 現状は開発者専用の機能です。
MESSAGE_SERVER_URL: ""
MESSAGE_SERVER_KEY: ""
"""
                )
            print('EEtool.iniを生成します。')

        if os.access(ini_path, os.R_OK):
            with open(ini_path, 'r', encoding='utf8') as f:
                yml = yaml.safe_load(f)
                try:
                    if isinstance(yml['SSIM_parallel_number'], int):
                        self.SSIM_parallel_number = yml['SSIM_parallel_number']
                    else:
                        print('EEtool.ini内のSSIM_parallel_numberが不正です。')
                        sys.exit(-1)
                    if isinstance(yml['MESSAGE_SERVER_URL'], str):
                        self.MESSAGE_SERVER_URL = yml['MESSAGE_SERVER_URL']
                    else:
                        self.MESSAGE_SERVER_URL = ""
                    if isinstance(yml['MESSAGE_SERVER_KEY'], str):
                        self.MESSAGE_SERVER_KEY = yml['MESSAGE_SERVER_KEY']
                    else:
                        self.MESSAGE_SERVER_KEY = ""
                except:
                    print(f"{ini_path}の中身書き換えましたか？\n削除してEEtoolを再度実行してください。")
                    sys.exit(-1)

        if self.MESSAGE_SERVER_URL == "" or self.MESSAGE_SERVER_KEY == "":
            print('webMessageの送信先が指定されていません。')

        while True:
            try:
                config_path = input("コンフィグファイルを指定してください。[config.yml]\n>")
                if config_path == "":
                    config_path = "config.yml"
                elif os.path.isfile(config_path):
                    pass
                elif not config_path.endswith(".yml"):
                    config_path += ".yml"
                f = open(config_path, 'r', encoding='utf8')
                break
            except FileNotFoundError:
                print("指定されたファイルを読み込めませんでした。")

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

        def ffmpeg():
            def ffmpeg_get():
                if not os.path.isdir(".ffmpeg"):
                    os.mkdir(".ffmpeg")

                # .ffmpegフォルダに何か入ってたら消したい処理
                if len(os.listdir(".ffmpeg")) != 0:
                    print(".ffmpegフォルダ内のファイルを削除します。よろしいですか。[Y/n]")
                    if yes_no_choice(True):
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
                if yes_no_choice(True):
                    self.ffmpeg_path = ".ffmpeg\\ffmpeg"
                else:
                    pass

            try:
                subprocess.run("ffmpeg", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("システムPathに登録されているffmpegを使用しますか？[Y/n]")
                if yes_no_choice(True):
                    self.ffmpeg_path = "ffmpeg"
                    return
                else:
                    print("最新版をGithubからダウンロードしますか？[Y/n]")
                    if yes_no_choice(True):
                        self.ffmpeg_path = ffmpeg_get()
                        return
                    else:
                        print("ffmpegが登録されていません。")
                        sys.exit(-102)
            except FileNotFoundError:
                print("システムPathにffmpegが登録されていません。")
                print("最新版をGithubからダウンロードしますか？[Y/n]")
                if yes_no_choice(True):
                    self.ffmpeg_path = ffmpeg_get()
                    return
                else:
                    print("ffmpegが登録されていません。")
                    sys.exit(-102)

        def input_file():
            if 'input_file' in yml:
                if isinstance(yml['input_file'], str):
                    self.input_file = yml['input_file']
                    return
            print("入力ファイルが指定されていません。\n")
            sys.exit(-103)

        def result_path():
            self.result_path = self.out_dir + self.out_dir.replace("\\", "") + "_result.csv"

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
        ffmpeg()
        input_file()
        result_path()
        encoder()
        bitrate_qp()
        preset()
        look_ahead()
        gop()
        profile()
        loglevel()


def yes_no_choice(default):
    while True:
        select = input().lower()
        if select == '':
            return default
        if select in ['y', 'yes']:
            return True
        if select in ['n', 'no']:
            return False


if __name__ == "__main__":
    g = GlobalConfig()
