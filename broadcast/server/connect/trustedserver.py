import json
import os

class TrustedServerManager:
    def __init__(self, directory):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    def load_trusted_servers(self, group_name):
        file_path = os.path.join(self.directory, f"{group_name}.json")
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_trusted_servers(self, group_name, trusted_servers):
        file_path = os.path.join(self.directory, f"{group_name}.json")
        with open(file_path, 'w') as file:
            json.dump(trusted_servers, file)

    def add_trusted_server(self, group_name, ip, public_key):
        trusted_servers = self.load_trusted_servers(group_name)
        if ip not in trusted_servers:
            trusted_servers[ip] = public_key
            self.save_trusted_servers(group_name, trusted_servers)

    def remove_trusted_server(self, group_name, ip):
        trusted_servers = self.load_trusted_servers(group_name)
        if ip in trusted_servers:
            del trusted_servers[ip]
            self.save_trusted_servers(group_name, trusted_servers)

    def get_trusted_servers(self, group_name):
        return self.load_trusted_servers(group_name)

    def change_public_key(self, group_name, ip, new_public_key):
        trusted_servers = self.load_trusted_servers(group_name)
        if ip in trusted_servers:
            trusted_servers[ip] = new_public_key
            self.save_trusted_servers(group_name, trusted_servers)

    @staticmethod
    def is_private_ip(ip):
        try:
            ip_address = ipaddress.ip_address(ip)
            return ip_address.is_private
        except ValueError:
            return False


