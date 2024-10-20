import os  # Operating system interactions
import time  # Time operations
import uuid  # Generating unique IDs
import json  # JSON handling
from datetime import datetime  # Date and time operations
from ipc import IPC
from scraper import Scraper
from profileICD import Profile
from utils import Utils  # Inter-process communication

class ScraperManager:
    
    def __init__(self, base_path,profiles):
        self.base_path = base_path
        self.venv_python = os.path.join(base_path, 'venv', 'bin', 'python')
        self.scrapers = {}
        self.config_profiles = {}
        self.ipc = IPC()
        raw_profiles = profiles
        for profile_name, profile_data in raw_profiles.items():
            self.config_profiles[profile_name] = Profile(
                profile_data.config_file,
                profile_data.interval,
                None,
                str(uuid.uuid4()),
                None,
                False
            )

    def start_scraper(self, profile_name):
        """Start a new scraper process."""
        profile = self.config_profiles[profile_name]
        unique_id = str(uuid.uuid4())
        scraper = Scraper(profile.config_file, unique_id, profile_name, self.base_path, self.venv_python, self.ipc)
        scraper.start()
        self.scrapers[unique_id] = scraper
        self.update_profile_execution(profile_name, scraper.last_started, unique_id)
        profile.running = True
        #print(f">> Started scraper [{unique_id}] for profile [{profile_name}]")

    def stop_scraper(self, unique_id):
        """Terminate a running scraper process."""
        scraper = self.scrapers.pop(unique_id, None)
        if scraper:
            scraper.stop()
            self.ipc.sockets.pop(unique_id, None)
            self.scrapers.pop(unique_id, None)

    def schedule_scrapers(self):
        """Main loop to check and start scrapers, and handle their statuses."""
        while True:
            self.check_and_start_scrapers()
            self.check_scrapers_status()
            self.receive_monitoring_data()
            time.sleep(1)

    def check_and_start_scrapers(self):
        """Check if scrapers need to be started based on their schedule."""
        now = datetime.now()
        for profile_name, profile in self.config_profiles.items():
            if profile.running:
                continue

            interval = profile.interval * 60  # convert interval to seconds
            last_exec = profile.last_exec or datetime.min

            if (now - last_exec).total_seconds() >= interval:
                self.start_scraper(profile_name)

    def update_profile_execution(self, profile_name, now, unique_id):
        """Update profile execution details after starting a scraper."""
        profile = self.config_profiles[profile_name]
        profile.last_exec = now
        profile.unique_id = unique_id
        profile.publish_address = self.scrapers[unique_id].address

    def check_scrapers_status(self):
        """Check the status of running scrapers and update profiles when they finish."""
        for unique_id, scraper in list(self.scrapers.items()):
            if scraper.process.poll() is not None:
                now = datetime.now()
                profile_name = scraper.profile_name
                scraper.last_finished = now
                profile = self.config_profiles[profile_name]
                profile.running = False
                profile.last_exec = now
                self.stop_scraper(unique_id)

    def receive_monitoring_data(self):
        """Receive and update monitoring data from scrapers."""
        for unique_id in list(self.scrapers.keys()):
            while True:
                received = self.ipc.receive_published(unique_id)
                if received:
                    self.update_monitoring_data(unique_id, received)
                else:
                    break

    def update_monitoring_data(self, unique_id, received):
        """Update monitoring data for a scraper."""
        try:
            monitoring_data = json.loads(received)
            self.scrapers[unique_id].monitoring_data = monitoring_data
            #with open(f"monitoring_data_{unique_id}.json", "w") as file:
            #    json.dump(monitoring_data, file, indent=4)
        except json.JSONDecodeError:
            print(f">> Failed to decode JSON for [{unique_id}]: {received[:30]}")

    def run(self):
        """Start the main scheduling loop."""
        self.schedule_scrapers()
