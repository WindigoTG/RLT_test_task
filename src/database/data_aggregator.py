from datetime import datetime
from enum import Enum
from typing import Dict, Optional

import pymongo
from motor.motor_asyncio import AsyncIOMotorCollection


class TimeSpan(Enum):
    Hour = "hour"
    Day = "day"
    Month = "month"


FORMAT_BY_TIME_SPAN = {
    TimeSpan.Hour: "%Y-%m-%dT%H:00:00",
    TimeSpan.Day: "%Y-%m-%dT00:00:00",
    TimeSpan.Month: "%Y-%m-01T00:00:00",
}


async def get_aggregated_data(
    collection: AsyncIOMotorCollection,
    date_from: datetime,
    date_to: datetime,
    time_span: TimeSpan
) -> Optional[Dict]:

    date_format = FORMAT_BY_TIME_SPAN[time_span]

    stage_match = {
        "$match": {
            "$and": [
                {"dt": {"$gte": date_from}},
                {"dt": {"$lte": date_to}},
            ],
        },
    }

    stage_group_first = {
        "$group": {
            "_id": {
                "$dateToString": {"format": date_format, "date": "$dt"}
            },
            "sum": {"$sum": "$value"},
        }
    }

    stage_sort = {
        "$sort": {
            "_id": pymongo.ASCENDING
        }
    }

    stage_group_second = {
        "$group": {
          "_id": None,
          "dataset": {"$push": "$sum"},
          "labels": {"$push": "$_id"},
        }
    }

    stage_project = {
        "$project": {"dataset": True, "labels": True, "_id": False}
    }

    cursor = collection.aggregate(
        [
            stage_match,
            stage_group_first,
            stage_sort,
            stage_group_second,
            stage_project,
        ]
    )

    result = await cursor.to_list(length=1)

    if result:
        return result[0]
