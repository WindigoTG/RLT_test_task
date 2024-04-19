from typing import Optional

from motor.motor_asyncio import (
    AsyncIOMotorCollection,
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)
from pymongo.errors import (
    ConfigurationError,
    OperationFailure,
    ServerSelectionTimeoutError,
)


class Database:
    _client: AsyncIOMotorClient = None

    @classmethod
    async def connect_to_database(cls, uri: str) -> bool:
        """ Подключение к удалённой базе данных. """

        try:
            cls._client = AsyncIOMotorClient(uri)
            await cls._client.admin.command('ping')
            return True
        except ConfigurationError:
            print('Incorrect uri')
            return False
        except OperationFailure:
            print('Incorrect credentials')
            return False
        except ServerSelectionTimeoutError:
            print('Unable to connect to database')
            return False

    @classmethod
    def get_database(cls, db_name: str) -> Optional[AsyncIOMotorDatabase]:
        """ Получение желаемой базы данных для работы. """
        if cls._client:
            return cls._client[db_name]

    @classmethod
    def get_collection(
        cls, db_name: str,
        collection_name: str,
    ) -> Optional[AsyncIOMotorCollection]:
        """ Получение желаемой коллекции для работы. """
        if cls._client:
            return cls._client[db_name][collection_name]
