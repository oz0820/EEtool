import os
import shutil
import subprocess
import sys

from utils.generate_command import generate_cmd
from utils.load_config import GlobalConfig
from utils.data_logger import Logger
from utils.SSIM_stats import ssim_stats

log_path = "encode.log"

RUN_ENCODE = True
RUN_SSIM = True


def main():
    global_config = GlobalConfig()
    if not os.path.isdir(global_config.out_dir):
        os.mkdir(global_config.out_dir)

    logger = Logger(log_path, global_config.result_path)
    commands = generate_cmd(global_config)
    encode(commands, logger)

    if RUN_SSIM:
        ssim_stats(gl_config.result_path, gl_config.out_dir)


def encode(commands, logger):
    count = len(commands)

    if RUN_ENCODE:
        for i in range(len(commands)):
            progress = f"【{str(i+1).rjust(len(str(count)))} / {count}】"
            print(f"run encode command\t{progress}\t{commands[i].get_encode_cmd()}")
            os.system(f"title encode{progress}{commands[i].get_encode_cmd()}")
            logger.encode_start(commands[i])
            subprocess.run(commands[i].get_encode_cmd())
            logger.encode_end(commands[i])

    if RUN_SSIM:
        for i in range(len(commands)):
            progress = f"【{str(i+1).rjust(len(str(count)))} / {count}】"
            print(f"run ssim command\t{progress}\t{commands[i].get_generate_ssim_cmd()}")
            os.system(f"title ssim{progress}{commands[i].get_generate_ssim_cmd()}")
            subprocess.run(commands[i].get_generate_ssim_cmd())
            shutil.move("ssim.tmp", commands[i].get_moved_ssim_path())


if __name__ == "__main__":
    args = sys.argv
    if 'ssim=false' in args:
        RUN_SSIM = False
    main()
