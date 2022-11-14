import os
import shutil
import subprocess
import sys

from utils.generate_command import generate_cmd
from utils.load_config import GlobalConfig
from utils.data_logger import Logger
from utils.SSIM_stats import ssim_stats
from utils.message_builder import MessageBuilder
from concurrent.futures import ThreadPoolExecutor


log_path = "encode.log"
VERSION = "2022.11.14.1"

RUN_ENCODE = True
RUN_SSIM = True

# ThreadPoolExecutor
global tpe


def main():
    global tpe
    global_config = GlobalConfig()
    tpe = ThreadPoolExecutor(max_workers=global_config.SSIM_parallel_number)

    if not os.path.isdir(global_config.out_dir):
        os.mkdir(global_config.out_dir)

    commands, total_count = generate_cmd(global_config)
    logger = Logger(log_path, global_config)
    do_encode(commands, total_count, logger)
    do_ssim(commands, total_count, logger)
    tpe.shutdown()
    if RUN_SSIM:
        ssim_stats(global_config.result_path, global_config.out_dir)


def do_encode(commands, total_count, logger):
    message_builder = MessageBuilder(total_count)
    logger.send_web_message("")
    if RUN_ENCODE:
        for i, command in enumerate(commands):
            print(message_builder.console_message('encode', i, command.get_encode_cmd()))
            os.system(message_builder.window_title("encode", i))
            logger.send_web_message(message_builder.web_message("start encode", i))
            logger.encode_start(command)
            subprocess.run(command.get_encode_cmd())
            logger.encode_end(command)


def do_ssim(commands, total_count, logger):
    message_builder = MessageBuilder(total_count)
    def ssim(command, i):
        ssim_tmp = (command.global_config.out_dir + f"_{i:09}.ssim").replace("\\", "")
        print(message_builder.console_message("ssim", i, command.ssim_cmd(ssim_tmp)))
        os.system(message_builder.window_title("ssim", i))
        subprocess.run(command.ssim_cmd(ssim_tmp))
        shutil.move(ssim_tmp, command.moved_ssim_path())
        logger.send_web_message(message_builder.web_message("end ssim", i))

    if RUN_SSIM:
        tpe.map(ssim, commands, range(len(commands)))


if __name__ == "__main__":
    args = sys.argv
    if '-h' in args or '-help' in args:
        print("-v, -version: \tShow version.\n"
              "-no-ssim: \tDo not run ssim.")
        sys.exit(0)
    if '-v' in args or '-version' in args:
        print(VERSION)
        sys.exit(0)
    if '-no-ssim' in args:
        RUN_SSIM = False

    main()
