import subprocess
import sys
from datetime import datetime

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
            if 'ffmpeg_path' in yml:
                if isinstance(yml['ffmpeg_path'], str):
                    self.ffmpeg_path = yml['ffmpeg_path']
            try:
                subprocess.run("ffmpeg", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("ffmpegのパスが指定されていません。\nシステムPathに登録されているffmpegを使用します。")
                self.ffmpeg_path = "ffmpeg"
                return
            except FileNotFoundError:
                print("ffmpegのパスが指定されていません。")
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


if __name__ == "__main__":
    g = GlobalCFG()

