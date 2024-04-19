import asyncio
import datetime

from config.config import load_config
from database.database import Database
from database.data_aggregator import get_aggregated_data, TimeSpan


async def main():
    """"""
    config = load_config()

    if not await Database.connect_to_database(config.database.connection_uri):
        print('Unable to connect to database')
        return

    db_collection = Database.get_collection(
        config.database.db_name,
        config.database.collection_name,
    )


if __name__ == '__main__':
    asyncio.run(main())
