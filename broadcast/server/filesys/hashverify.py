import json
import hashlib

class DataVerifier:
    def __init__(self, data_raw, data_hash):
        self.data_raw = data_raw
        self.data_hash = data_hash

    def verify_data(self, test="subset"):
        data_raw_hashes = {entry["timestamp"]: hashlib.sha256(json.dumps(entry["data"]).encode()).hexdigest() for entry in self.data_raw}
        data_hash_hashes = {entry["timestamp"]: entry["hash"] for entry in self.data_hash}

        if test == "subset":
            return all(data_raw_hashes.get(entry["timestamp"]) == data_hash_hashes.get(entry["timestamp"]) for entry in self.data_hash)
        elif test == "superset":
            return all(data_raw_hashes.get(entry["timestamp"]) == data_hash_hashes.get(entry["timestamp"]) for entry in self.data_raw)
        else:
            raise ValueError("Invalid test specified. Use 'subset' or 'superset'.")


