import os
import csv

class AuthorizationFilesHandler:
    def __init__(self, directory):
        self.directory = directory
        self.type_file = os.path.join(self.directory, 'types.csv')
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(self.type_file):
            with open(self.type_file, 'w') as file:
                pass

    def authorize_user(self, right, user):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        file_path = os.path.join(self.directory, right)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                pass
            self.set_list_type(right, 'whitelist')  # Set default list-type to whitelist
        with open(file_path, 'a') as file:
            file.write(user + '\n')

    def remove_user(self, right, user):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        file_path = os.path.join(self.directory, right)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
            with open(file_path, 'w') as file:
                for line in lines:
                    if line.strip() != user:
                        file.write(line)
        else:
            print(f"Error: Directory '{self.directory}' or file '{file_path}' does not exist.")

    def set_list_type(self, right, list_type):
        if list_type not in ['whitelist', 'blacklist', 'no-limit', 'prohibited']:
            raise ValueError("Invalid list type. Must be 'whitelist', 'blacklist', 'no-limit', or 'prohibited'.")
        types_data = self._read_types_file()
        types_data[right] = list_type
        self._write_types_file(types_data)

    def get_list_type(self, right):
        types_data = self._read_types_file()
        return types_data.get(right, None)

    def change_list_type(self, right, new_list_type):
        self.set_list_type(right, new_list_type)

    def check_user_right(self, right, user):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        list_type = self.get_list_type(right)
        if list_type == 'whitelist':
            return self._check_whitelist(right, user)
        elif list_type == 'blacklist':
            return self._check_blacklist(right, user)
        elif list_type == 'no-limit':
            return True
        elif list_type == 'prohibited':
            return False
        else:
            raise ValueError("Invalid list type.")

    def _check_whitelist(self, right, user):
        file_path = os.path.join(self.directory, right)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                authorized_users = [line.strip() for line in file.readlines()]
            return user in authorized_users
        else:
            print(f"Error: File '{file_path}' does not exist.")
            return False

    def _check_blacklist(self, right, user):
        file_path = os.path.join(self.directory, right)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                unauthorized_users = [line.strip() for line in file.readlines()]
            return user not in unauthorized_users
        else:
            print(f"Error: File '{file_path}' does not exist.")
            return False

    def _read_types_file(self):
        if os.path.exists(self.type_file):
            with open(self.type_file, 'r') as file:
                reader = csv.reader(file)
                types_data = {row[0]: row[1] for row in reader}
        else:
            types_data = {}
        return types_data

    def _write_types_file(self, types_data):
        with open(self.type_file, 'w') as file:
            writer = csv.writer(file)
            for right, list_type in types_data.items():
                writer.writerow([right, list_type])

