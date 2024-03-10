import os
from datetime import datetime
import json
import csv

class TimeSortedFileSystem:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def store_file(self, server, user, data, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        stored_path = datetime.fromtimestamp(timestamp).strftime("%Y/%m/%d/%H-%M-%S-%f")
        year, month, day, time = stored_path.split("/")
        hour, minute, second, millisecond = time.split("-")
        user_dir = os.path.join(self.base_dir, server, year, month, day, user)
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, f"{hour}-{minute}-{second}-{millisecond}")
        with open(file_path, "w") as file:
            stored_data = {"timestamp": timestamp, "data": data, "user": user}
            json.dump(stored_data, file, indent=4)

    def get_data_within_time_range(self, server, start_time, end_time=None, users=None):
        if end_time is None:
            end_time = datetime.now().timestamp()
        data = []
        for root, dirs, files in os.walk(os.path.join(self.base_dir, server)):
            for file_name in files:
                try:
                    file_path = os.path.join(root, file_name)
                    file_time = datetime.strptime(os.path.join(os.path.split(root)[0], file_name),f"{self.base_dir}/%Y/%m/%d/%H-%M-%S-%f").timestamp()
                    # Extract user from file path
                    if start_time <= file_time <= end_time and (users is None or user in users):
                        with open(file_path, "r") as file:
                            raw = json.load(file)
                        if(self.file_check(raw, file_time, user)):
                            data.append(raw)
                except:
                    continue
        return data
    @staticmethod
    def file_check(data, file_time, user):
        try:
            return (data["user"] == user) and (data["timestamp"] == file_time)
        except KeyError:
            return False
