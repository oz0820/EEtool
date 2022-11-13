import os
import sys
import requests
from datetime import datetime


class Logger:
    st_time = datetime.now()

    def __init__(self, log_path, global_config):
        self.log_path = log_path
        self.global_config = global_config
        self.result_path = global_config.result_path

        if not os.access(log_path, os.F_OK):
            print(f"{log_path}を生成します。")
        elif not os.access(log_path, os.W_OK):
            print(f"{log_path}を開く権限がありません。")
            sys.exit(-301)

        try:
            with open(self.result_path, 'w') as f:
                f.write(f"encoder,input,mode,qp,bitrate,preset,profile,look_ahead,time(s),file_name\n")
        except PermissionError:
            print(f"{self.result_path}を開く権限がありません。")
            sys.exit(-302)

    def encode_start(self, cmd):
        with open(self.log_path, 'a', encoding="utf8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')}\tstart\t{cmd.get_encode_cmd()}\n")
        self.st_time = datetime.now()

    def encode_end(self, cmd):
        delta_time = datetime.now() - self.st_time
        with open(self.log_path, 'a', encoding="utf8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')}\tend\t{cmd.get_encode_cmd()}\n")

        with open(self.result_path, 'a', encoding='utf8') as f:
            if cmd.mode == 'quality':
                f.write(f"{cmd.encoder},{cmd.global_config.input_file},{cmd.mode},{cmd.qp},,{cmd.preset},{cmd.profile},{cmd.look_ahead},{get_delta_ft(delta_time)},{cmd.out_name}\n")
            elif cmd.mode == 'bitrate':
                f.write(f"{cmd.encoder},{cmd.global_config.input_file},{cmd.mode},,{cmd.bitrate},{cmd.preset},{cmd.profile},{cmd.look_ahead},{get_delta_ft(delta_time)},{cmd.out_name}\n")

    def send_web_message(self, message):
        if self.global_config.MESSAGE_SERVER_URL == "" or self.global_config.MESSAGE_SERVER_KEY == "":
            return
        try:
            requests.get(f"{self.global_config.MESSAGE_SERVER_URL}?key={self.global_config.MESSAGE_SERVER_KEY}&message={message}", timeout=(2, 2))
        except:
            print("webMessageの送信に失敗しました。")


def get_delta_ft(td):
    return f"{td.seconds}.{td.microseconds:06}"

