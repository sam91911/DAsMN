import os
from datetime import datetime
import json

class FileSystem:
    def __init__(self, directory):
        self.directory = directory

    def save_data(self, data):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
        year = timestamp[:4]
        month = timestamp[4:6]
        day = timestamp[6:8]
        filename = os.path.join(self.directory, year, month, day, f"{timestamp}")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            json.dump(data, f)

    def get_data(self, start_timestamp, stop_timestamp = None):
        start_year = start_timestamp[:4]
        start_month = start_timestamp[4:6]
        start_day = start_timestamp[6:8]
        start_hour = start_timestamp[9:11]
        start_minute = start_timestamp[11:13]
        start_second = start_timestamp[13:15]
        start_millisecond = start_timestamp[16:]

        stop_year = stop_timestamp[:4]
        stop_month = stop_timestamp[4:6]
        stop_day = stop_timestamp[6:8]
        stop_hour = stop_timestamp[9:11]
        stop_minute = stop_timestamp[11:13]
        stop_second = stop_timestamp[13:15]
        stop_millisecond = stop_timestamp[16:]

        result = []
        for year in os.listdir(os.path.join(self.data_directory, start_year)):
            if year < start_year or year > stop_year:
                continue
            for month in os.listdir(os.path.join(self.data_directory, start_year, year)):
                if year == start_year and month < start_month or year == stop_year and month > stop_month:
                    continue
                for day in os.listdir(os.path.join(self.data_directory, start_year, year, month)):
                    if year == start_year and month == start_month and day < start_day or \
                       year == stop_year and month == stop_month and day > stop_day:
                        continue
                    for filename in os.listdir(os.path.join(self.data_directory, start_year, year, month, day)):
                        if year == start_year and month == start_month and day == start_day and \
                           filename < f"{start_hour}{start_minute}{start_second}.{start_millisecond}" or \
                           year == stop_year and month == stop_month and day == stop_day and \
                           filename > f"{stop_hour}{stop_minute}{stop_second}.{stop_millisecond}":
                            continue
                        with open(os.path.join(self.data_directory, start_year, year, month, day, filename), "r") as file:
                            data = json.load(file)
                            result.append(data)
        return result
