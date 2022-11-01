import os
import shutil
import subprocess

from src.utils.generate_command import generate_cmd
from src.utils.load_config import GlobalCFG
from src.utils.data_logger import Logger
from src.utils.SSIM_stats import ssim_stats

log_path = "encode.log"
result_path = "result.csv"


def main():
    logger = Logger(log_path, result_path)
    gl_config = GlobalCFG()
    if not os.path.isdir(gl_config.out_dir):
        os.mkdir(gl_config.out_dir)

    commands = generate_cmd(gl_config)
    encode(commands, logger)

    ssim_stats(result_path, gl_config.out_dir)


def encode(commands, logger):
    digit = '0'+str(len(str(len(commands))))
    count = len(commands)

    for i in range(len(commands)):
        print(f"run encode command\t{i+1:{digit}}/{count}\t{commands[i].get_encode_cmd()}")
        os.system(f"title encode【{i+1:{digit}}/{count}】{commands[i].get_encode_cmd()}")
        logger.encode_start(commands[i])
        subprocess.run(commands[i].get_encode_cmd())
        logger.encode_end(commands[i])

    for i in range(len(commands)):
        print(f"run ssim command\t{i + 1:{digit}}/{count}\t{commands[i].get_generate_ssim_cmd()}")
        os.system(f"title ssim【{i + 1:{digit}}/{count}】{commands[i].get_generate_ssim_cmd()}")
        subprocess.run(commands[i].get_generate_ssim_cmd())
        shutil.move("ssim.tmp", commands[i].get_moved_ssim_path())


if __name__ == "__main__":
    main()
