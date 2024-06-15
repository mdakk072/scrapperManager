import threading
import time
from ScraperManager import ScraperManager
from ipc import IPC
import json

DELIMITER = "::"

class RemoteScraperManager:
    def __init__(self, base_path, port):
        self.manager = ScraperManager(base_path)
        self.ipc = IPC()
        self.ipc.init_publisher(port)
        self.base_path = base_path

    def send_status(self):
        while True:
            scrapers_status = {scraper_id: json.loads(scraper.to_json()) for scraper_id, scraper in self.manager.scrapers.items()}
            profiles_status = {profile_name: json.loads(profile.to_json()) for profile_name, profile in self.manager.config_profiles.items()}

            # Publish the status with delimiter
            self.ipc.publish('scraper_status' + DELIMITER + json.dumps(scrapers_status))
            self.ipc.publish('profiles_status' + DELIMITER + json.dumps(profiles_status))
            
            time.sleep(5)  # Send status every 5 seconds

    def start(self):
        manager_thread = threading.Thread(target=self.manager.run)
        manager_thread.daemon = True
        manager_thread.start()

        status_thread = threading.Thread(target=self.send_status)
        status_thread.daemon = True
        status_thread.start()

        manager_thread.join()
        status_thread.join()

if __name__ == "__main__":
    base_path = "/home/mdakk072/projects/coreScraperProject/kijijiCarScraper"
    port = "tcp://localhost:7500"  # Example port number
    remote_manager = RemoteScraperManager(base_path, port)
    remote_manager.start()
