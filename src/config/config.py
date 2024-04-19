import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class DatabaseConfig:
    connection_uri: str
    db_name: str
    collection_name: str


@dataclass
class TelegramBotConfig:
    token: str


@dataclass
class Config:
    database: DatabaseConfig
    telegram_bot: TelegramBotConfig


def load_config(path: Optional[str] = None) -> Config:
    load_dotenv(path)

    return Config(
        database=DatabaseConfig(
            connection_uri=os.environ['DATABASE_CONNECTION_URI'],
            db_name=os.environ['DATABASE_NAME'],
            collection_name=os.environ['COLLECTION_NAME'],
        ),
        telegram_bot=TelegramBotConfig(
            token=os.environ['BOT_TOKEN']
        )
    )
