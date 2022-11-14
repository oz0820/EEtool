class MessageBuilder:

    def __init__(self, total_count):
        self.total_count = total_count

    def __progress(self, index):
        return f"【{str(index + 1).rjust(len(str(self.total_count)))} / {self.total_count}】"

    def window_title(self, prefix, index):
        return f"title \"{prefix}【{str(index + 1).rjust(len(str(self.total_count)))}/{self.total_count}】\""

    def web_message(self, prefix, index):
        return f"{prefix} {self.__progress(index)}"

    def console_message(self, prefix, index, command_string):
        return f"{prefix} command\t{self.__progress(index)}\t{command_string}"
