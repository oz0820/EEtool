import sys


class Command:
    def __init__(self, gl_cfg, opts):
        self.gl_cfg = gl_cfg
        self.opts = opts

        try:
            self.encoder = opts['encoder']
            self.preset = opts['preset']
            self.profile = opts['profile']
            self.look_ahead = opts['look_ahead']
            self.mode = opts['mode']
            self.gop = opts['gop']
        except KeyError:
            print('内部エラー')
            sys.exit(-201)

        if self.mode == "quality":
            self.qp = opts['qp']
            self.out_name = f"encoder={self.encoder}.mode={self.mode}.qp={self.qp}.look_ahead={self.look_ahead}.preset={self.preset}.gop={self.gop}.profile={self.profile}.mp4"
        if self.mode == "bitrate":
            self.bitrate = opts['bitrate']
            self.out_name = f"encoder={self.encoder}.mode={self.mode}.bitrate={self.bitrate}.look_ahead={self.look_ahead}.preset={self.preset}.gop={self.gop}.profile={self.profile}.mp4"

        self.out_video_path = gl_cfg.out_dir + self.out_name

    # qsvで10bitエンコードする場合はオプション付加が必要
    def add_10bit_opt(self):
        if self.encoder.find("qsv") != -1 and self.profile == "main10":
            return "-pix_fmt p010le "
        else:
            return ""

    def is_bender(self):
        if self.encoder.find("qsv") != -1:
            return 'intel'
        elif self.encoder.find("nvenc") != -1:
            return 'nvidia'

    def get_encode_cmd(self):
        gl_cfg = self.gl_cfg
        nvenc_pre = ["-1", "p1", "p2", "p3", "p4", "p5", "p6", "p7"]
        qsv_pre = ["-1", "7", "6", "5", "4", "3", "2", "1"]
        if self.mode == 'quality':
            if self.is_bender() == 'intel':
                cmd = f"{gl_cfg.ffmpeg_path} -loglevel {gl_cfg.loglevel} -i {gl_cfg.input_file} {self.add_10bit_opt()}" \
                      f"-preset {qsv_pre[int(self.preset)]} -look_ahead_depth {self.look_ahead} -profile:v {self.profile} " \
                      f"-c:v {self.encoder} -q:v {self.qp} -g {self.gop} -an -y {self.out_video_path}"
                return cmd
            if self.is_bender() == 'nvidia':
                cmd = f"{gl_cfg.ffmpeg_path} -loglevel {gl_cfg.loglevel} -i {gl_cfg.input_file} {self.add_10bit_opt()}" \
                      f"-preset {nvenc_pre[int(self.preset)]} -rc-lookahead {self.look_ahead} -profile:v {self.profile} " \
                      f"-c:v {self.encoder} -qp {self.qp} -g {self.gop} -an -y {self.out_video_path}"
                return cmd

        if self.mode == 'bitrate':
            if self.is_bender() == 'intel':
                cmd = f"{gl_cfg.ffmpeg_path} -loglevel {gl_cfg.loglevel} -i {gl_cfg.input_file} {self.add_10bit_opt()}" \
                      f"-preset {qsv_pre[int(self.preset)]} -look_ahead_depth {self.look_ahead} -profile:v {self.profile} " \
                      f"-c:v {self.encoder} -b:v {self.bitrate} -g {self.gop} -an -y {self.out_video_path}"
                return cmd
            if self.is_bender() == 'nvidia':
                cmd = f"{gl_cfg.ffmpeg_path} -loglevel {gl_cfg.loglevel} -i {gl_cfg.input_file} {self.add_10bit_opt()}" \
                      f"-preset {nvenc_pre[int(self.preset)]} -rc-lookahead {self.look_ahead} -profile:v {self.profile} " \
                      f"-c:v {self.encoder} -b:v {self.bitrate} -g {self.gop} -an -y {self.out_video_path}"
                return cmd
        print("エンコードコマンド生成に異常があります。")
        sys.exit(-221)

    def get_generate_ssim_cmd(self):
        gl_cfg = self.gl_cfg
        return f"{gl_cfg.ffmpeg_path} -loglevel {gl_cfg.loglevel} -i {self.out_video_path} -i {gl_cfg.input_file} -filter_complex ssim=f=ssim.tmp -an -f null - -y"

    def get_moved_ssim_path(self):
        return f"{self.out_video_path[:-3]}ssim.txt"


def generate_cmd(gl_cfg):
    commands = []
    for encoder in gl_cfg.encoder:
        for preset in gl_cfg.preset:
            for profile in gl_cfg.profile:
                for look_ahead in gl_cfg.look_ahead:
                    for gop in gl_cfg.gop:

                        # qpとbitrateはどちらか一方の空が許可されているので
                        for qp in gl_cfg.qp:
                            opt = {
                                "encoder": encoder,
                                "preset": preset,
                                "profile": profile,
                                "look_ahead": look_ahead,
                                "qp": qp,
                                "gop": gop,
                                "mode": "quality"
                            }
                            commands.append(Command(gl_cfg, opt))

                        for bitrate in gl_cfg.bitrate:
                            opt = {
                                "encoder": encoder,
                                "preset": preset,
                                "profile": profile,
                                "look_ahead": look_ahead,
                                "bitrate": bitrate,
                                "gop": gop,
                                "mode": "bitrate"
                            }
                            commands.append(Command(gl_cfg, opt))

    return commands
