from datetime import datetime
import subprocess
import json

class Scraper:
    """Class representing a single scraper."""
    def __init__(self, config_file, unique_id, profile_name, base_path, venv_python, ipc):
        self.config_file = config_file
        self.unique_id = unique_id
        self.profile_name = profile_name
        self.base_path = base_path
        self.venv_python = venv_python
        self.ipc = ipc
        self.address = f"tcp://localhost:{self.ipc.get_free_port()}"
        self.process = None
        self.last_started = None
        self.monitoring_data = {}

    def start(self):
        """Start the scraper process."""
        cmd = [
            self.venv_python, "main.py",
            "-c", self.config_file,
            "-i", self.unique_id,
            "-p", self.address
        ]
        self.process = subprocess.Popen(cmd, cwd=self.base_path)
        self.last_started = datetime.now()
        self.ipc.init_subscriber(self.unique_id, self.address)
        return self.process

    def stop(self):
        """Terminate the scraper process."""
        if self.process:
            self.process.terminate()
            self.process.wait()

    def to_dict(self):
        """Return a dictionary representation of the scraper."""
        return {
            "unique_id": self.unique_id,
            "profile_name": self.profile_name,
            "last_started": self.last_started,
            "address": self.address,
            "monitoring_data": self.monitoring_data
        }

    def to_json(self):
        """Return a JSON representation of the scraper."""
        def default(o):
            if isinstance(o, datetime):
                return o.isoformat()
            raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')
        
        return json.dumps(self.to_dict(), default=default)
