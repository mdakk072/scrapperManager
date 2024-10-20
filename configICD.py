from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ProfileConfig:
    config_file: str
    interval: int

@dataclass
class Config:
    profiles: Dict[str, ProfileConfig]
    base_path: str
    publish_host: str
    publish_port: int
    response_port: int
    request_port: int
    log_path: str = 'app.log'
    log_level: str = 'INFO'
    log_console: bool = True
    log_file: bool = False 

    @classmethod
    def parse(cls, data: Dict[str, Any]) -> 'Config':
        profiles = {
            name: ProfileConfig(
                config_file=profile['config_file'],
                interval=profile['interval']
            )
            for name, profile in data['profiles'].items()
        }

        return cls(
            profiles=profiles,
            base_path=data['base_path'],
            publish_host=data['publish_host'],
            publish_port=data['publish_port'],
            response_port=data['response_port'],
            request_port=data['request_port'],
            log_path=data["log_path"],
            log_console=data["log_console"],
            log_file=data["log_file"]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'profiles': {
                name: {
                    'config_file': profile.config_file,
                    'interval': profile.interval
                }
                for name, profile in self.profiles.items()
            },
            'base_path': self.base_path,
            'publish_host': self.publish_host,
            'publish_port': self.publish_port,
            'request_port': self.request_port,
            'response_port': self.response_port,
            'log_path': self.log_path,
            'log_console': self.log_console,
            'log_file': self.log_file
            
        }