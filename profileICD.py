from datetime import datetime
import json

class Profile:
    """Class representing a profile."""
    def __init__(self, config_file, interval, last_exec, unique_id, publish_address, running):
        self.config_file = config_file
        self.interval = interval
        self.last_exec = last_exec
        self.unique_id = unique_id
        self.publish_address = publish_address
        self.running = running

    def to_dict(self):
        """Return a dictionary representation of the profile."""
        return {
            "config_file": self.config_file,
            "interval": self.interval,
            "last_exec": self.last_exec.isoformat() if self.last_exec else None,
            "unique_id": self.unique_id,
            "publish_address": self.publish_address,
            "running": self.running
        }

    def to_json(self):
        """Return a JSON representation of the profile."""
        return json.dumps(self.to_dict())
