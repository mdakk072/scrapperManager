import threading
import time
import json
from typing import Dict, Any
from configICD import Config
from ScraperManager import ScraperManager
from ipc import IPC
from utils import Utils

DELIMITER = "::"
STATUS_UPDATE_INTERVAL = 1

class RemoteManager:
    def __init__(self, config: Config):
        self.logger = Utils.get_logger()
        self.logger.info("Initializing RemoteManager")
        self.config = config
        self.logger.debug(f"Configuration loaded: {config}")
        self.manager = ScraperManager(config.base_path, config.profiles)
        self.logger.debug("ScraperManager initialized")
        self.ipc = IPC()
        
        try:
            publisher_address = f"tcp://{config.publish_host}:{config.publish_port}"
            subscriber_address = f"tcp://{config.publish_host}:{config.request_port}"
            response_address = f"tcp://{config.publish_host}:{config.response_port}"
            self.logger.info(f"Initializing IPC publisher at {publisher_address}")
            self.ipc.init_publisher(publisher_address)
            self.logger.info(f"Initializing IPC subscriber at {subscriber_address}")
            self.ipc.init_requester(subscriber_address)
            self.logger.info("IPC publisher and subscriber initialized successfully")
            self.ipc.init_replier(response_address)
            self.logger.info(f"Initializing IPC replier at {response_address}")
        except Exception as e:
            self.logger.error(f"Failed to initialize IPC: {e}", exc_info=True)
            raise

        self.logger.info("RemoteManager initialized successfully")

    def run_communication(self) -> None:
        self.logger.info("Starting communication thread")
        while True:
            try:
                start_time = time.time()
                self.logger.debug("Executing send_status")
                self.send_status()
                self.logger.debug("Completed send_status")
                
                self.logger.debug("Executing poll_commands")
                self.poll_commands()
                self.logger.debug("Completed poll_commands")
                
                elapsed = time.time() - start_time
                sleep_time = max(STATUS_UPDATE_INTERVAL , 0)
                self.logger.info(f"Communication cycle completed in {elapsed:.2f} seconds, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            except Exception as e:
                self.logger.error(f"Error in communication thread: {e}", exc_info=True)
                self.logger.debug("Sleeping for 1 second before retrying communication tasks")
                time.sleep(1)

    def send_status(self) -> None:
        scrapers_status = {scraper_id: json.loads(scraper.to_json()) for scraper_id, scraper in self.manager.scrapers.items()}
        profiles_status = {profile_name: json.loads(profile.to_json()) for profile_name, profile in self.manager.config_profiles.items()}

        try:
            scraper_status_message = 'scraper_status' + DELIMITER + json.dumps(scrapers_status)
            self.logger.debug(f"Publishing scraper status message: {scraper_status_message}")
            self.ipc.publish(scraper_status_message)
            profiles_status_message = 'profiles_status' + DELIMITER + json.dumps(profiles_status)
            
            self.logger.debug(f"Publishing profiles status message: {profiles_status_message}")
            self.ipc.publish(profiles_status_message)
            
            self.logger.info("Status messages published successfully")
        except Exception as e:
            self.logger.error(f"Failed to publish status messages: {e}", exc_info=True)

    def poll_commands(self) -> None:
        self.logger.debug("Polling for incoming commands")
        message = self.ipc.receive_request(timeout=500)
        if message:
            self.logger.debug(f"Received message: {message}")
            try:
                command, data = message.split(DELIMITER, 1)
                self.logger.info(f"Received command: {command} with data: {data}")
                with open("command.txt", "w") as f:
                    f.writelines([command, data])
                self.process_command(command, data)
            except ValueError:
                self.logger.error("Received malformed message", exc_info=True)
        else:
            self.logger.debug("No message received during polling")

    def process_command(self, command: str, data: str) -> None:
        self.logger.info(f"Processing command: {command} with data: {data}")
        try:
            if command == 'start_scraper':
                self.logger.debug(f"Starting scraper with data: {data}")
                self.manager.start_scraper(data)
                self.logger.info(f"Scraper '{data}' started successfully")
            elif command == 'stop_scraper':
                self.logger.debug(f"Stopping scraper with data: {data}")
                self.manager.stop_scraper(data)
                self.logger.info(f"Scraper '{data}' stopped successfully")
            else:
                self.logger.warning(f"Unknown command received: {command}")
        except Exception as e:
            self.logger.error(f"Error processing command '{command}': {e}", exc_info=True)

    def start(self) -> None:
        self.logger.info("Starting RemoteManager threads")
        threads = [
            threading.Thread(target=self.manager.run, name="ManagerThread"),
            threading.Thread(target=self.run_communication, name="CommunicationThread")
        ]

        for thread in threads:
            self.logger.debug(f"Starting thread: {thread.name}")
            thread.daemon = True
            thread.start()
            self.logger.info(f"Thread {thread.name} started")

        self.logger.info("All threads started")

        for thread in threads:
            self.logger.debug(f"Joining thread: {thread.name}")
            thread.join()
            self.logger.info(f"Thread {thread.name} has terminated")
