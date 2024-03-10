import os
import csv

class AuthorizationFilesHandler:
    def __init__(self, directory):
        self.directory = directory
        self.type_file = 'types.csv'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def authorize_user(self, server, right, user):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(os.path.join(self.directory, server)):
            os.makedirs(os.path.join(self.directory, server))
        file_path = os.path.join(self.directory, server, right)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                pass
            self.set_list_type(right, 'whitelist')  # Set default list-type to whitelist
        with open(file_path, 'a') as file:
            file.write(user + '\n')

    def remove_user(self, server, right, user):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(os.path.join(self.directory, server)):
            os.makedirs(os.path.join(self.directory, server))
        file_path = os.path.join(self.directory, server, right)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
            with open(file_path, 'w') as file:
                for line in lines:
                    if line.strip() != user:
                        file.write(line)
        else:
            print(f"Error: Directory '{self.directory}' or file '{file_path}' does not exist.")

    def set_list_type(self, server, right, list_type):
        if list_type not in ['whitelist', 'blacklist', 'no-limit', 'prohibited']:
            raise ValueError("Invalid list type. Must be 'whitelist', 'blacklist', 'no-limit', or 'prohibited'.")
        types_data = self._read_types_file(server)
        types_data[right] = list_type
        self._write_types_file(server, types_data)

    def get_list_type(self, server, right):
        types_data = self._read_types_file(server)
        return types_data.get(right, None)

    def change_list_type(self, server, right, new_list_type):
        self.set_list_type(server, right, new_list_type)

    def check_user_right(self, server, right, user):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(os.path.join(self.directory, server)):
            os.makedirs(os.path.join(self.directory, server))
        list_type = self.get_list_type(server, right)
        if list_type is None:
            return None
        if list_type == 'whitelist':
            return self._check_whitelist(server, right, user)
        elif list_type == 'blacklist':
            return self._check_blacklist(server, right, user)
        elif list_type == 'no-limit':
            return True
        elif list_type == 'prohibited':
            return False
        else:
            raise ValueError("Invalid list type.")

    def check_server(self, server):
        server_dir = os.path.join(self.directory, server)
        return os.path.isdir(server_dir)

    def create_server(self, server):
        server_dir = os.path.join(self.directory, server)
        if not os.path.exists(server_dir):
            os.makedirs(server_dir)
        type_file = os.path.join(server_dir, self.type_file)
        if not os.path.exists(type_file):
            with open(type_file, "w") as f:
                pass
        return

    def _check_whitelist(self, server, right, user):
        file_path = os.path.join(self.directory, server, right)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                authorized_users = [line.strip() for line in file.readlines()]
            return user in authorized_users
        else:
            print(f"Error: File '{file_path}' does not exist.")
            return False

    def _check_blacklist(self, server, right, user):
        file_path = os.path.join(self.directory, server, right)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                unauthorized_users = [line.strip() for line in file.readlines()]
            return user not in unauthorized_users
        else:
            print(f"Error: File '{file_path}' does not exist.")
            return False

    def _read_types_file(self, server):
        type_file = os.path.join(self.directory, server, self.type_file)
        if os.path.exists(type_file):
            with open(type_file, 'r') as file:
                reader = csv.reader(file)
                types_data = {row[0]: row[1] for row in reader}
        else:
            types_data = {}
        return types_data

    def _write_types_file(self, server, types_data):
        type_file = os.path.join(self.directory, server, self.type_file)
        with open(type_file, 'w') as file:
            writer = csv.writer(file)
            for right, list_type in types_data.items():
                writer.writerow([right, list_type])

