import os
import csv
from Crypto.Hash import SHA256

class NameFileSystem:
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def _get_user_file_path(self, group):
        user_dir = os.path.join(self.root_dir, group)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir

    def save_user_key(self, username, public_key, group):
        user_dir = self._get_user_file_path(group)
        key_file = os.path.join(user_dir, f'{username}.pem')
        with open(key_file, 'w') as file:
            file.write(public_key)
        hash_obj = SHA256.new()
        hash_obj.update(public_key.encode())
        hash_value = hash_obj.hexdigest()
        file_path = os.path.join(self.root_dir, group, f"{hash_value}.csv")
        if os.path.exists(file_path):
            with open(file_path, mode='r') as file:
                reader = csv.reader(file)
                data_dict = {row[0]:row[1] for row in reader}
            data_dict[username] = public_key.replace("\n", "|")
        else:
            data_dict = {username: public_key}
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            for user, key in data_dict.items():
                writer.writerow([user, key])

    def get_user_key(self, username, group):
        user_dir = self._get_user_file_path(group)
        key_file = os.path.join(user_dir, f'{username}.pem')
        if os.path.exists(key_file):
            with open(key_file, 'r') as file:
                return file.read()
        return None
    def get_user_name(self, public_key, group):
        hash_obj = SHA256.new()
        hash_obj.update(public_key.encode())
        hash_value = hash_obj.hexdigest()
        file_path = os.path.join(self.root_dir, group, f"{hash_value}.csv")
        public_key = public_key.replace("\n", "|")
        if not os.path.exists(file_path):
            return None
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[1] == public_key:
                    return row[0]  # Return the username
        return None
