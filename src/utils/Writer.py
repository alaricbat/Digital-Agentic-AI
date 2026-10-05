import os
import threading
from datetime import datetime

file_write_lock = threading.Lock()

class Writer():

    def __init__(self, tid, file_path, file_name):
        self.__tid = tid
        self.__file_path = file_path
        self.__file_name = file_name

    def write(self, msg):

        now = datetime.now()
        time_part = now.strftime("%B %y %d") 
        pid = os.getpid()

        log_line = f"{time_part} {pid} {self.__tid} {msg} \n"

        full_file_path = self.__file_path + self.__file_name
        log_directory = os.path.dirname(full_file_path)

        with file_write_lock:
            if log_directory and not os.path.exists(log_directory):
                os.makedirs(log_directory, exist_ok=True)

            with open(full_file_path, "a", encoding="utf-8") as f:
                f.write(log_line)
                f.flush()