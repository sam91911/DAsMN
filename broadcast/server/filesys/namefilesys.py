import os

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

    def get_user_key(self, username, group):
        user_dir = self._get_user_file_path(group)
        key_file = os.path.join(user_dir, f'{username}.pem')
        if os.path.exists(key_file):
            with open(key_file, 'r') as file:
                return file.read()
        return None
