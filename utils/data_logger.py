import os
import sys
from datetime import datetime


class Logger:
    st_time = datetime.now()

    def __init__(self, log_path, result_path):
        self.log_path = log_path
        self.result_path = result_path

        if not os.access(log_path, os.F_OK):
            print(f"{log_path}を生成します。")
        elif not os.access(log_path, os.W_OK):
            print(f"{log_path}を開く権限がありません。")
            sys.exit(-301)

        try:
            with open(result_path, 'w') as f:
                f.write(f"encoder,input,mode,qp,bitrate,preset,profile,look_ahead,time(s),file_name\n")
        except PermissionError:
            print(f"{result_path}を開く権限がありません。")
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


def get_delta_ft(td):
    return f"{td.seconds}.{td.microseconds:06}"

