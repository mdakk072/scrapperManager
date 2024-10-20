from utils import Utils
from configICD import Config

from remoteManager import RemoteManager

class MainApp:
    @staticmethod
    def start():
        config_data = Utils.read_yaml("config.yaml")
        if not config_data:
            print("Error reading config file")
            exit(1)
        
        config = Config.parse(config_data)
        logger = Utils.setup_logging(config.log_path,config.log_level,config.log_console,config.log_file)
        logger.info("Starting Remote Manager")
        remote_manager = RemoteManager(config)
        remote_manager.start()

if __name__ == "__main__":
    
    MainApp.start()