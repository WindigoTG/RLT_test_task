from datetime import datetime

from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional

import pymongo
from motor.motor_asyncio import AsyncIOMotorCollection

from utils.enums import GroupType


FORMAT_BY_GROUP_TYPE = {
    GroupType.Hour: "%Y-%m-%dT%H:00:00",
    GroupType.Day: "%Y-%m-%dT00:00:00",
    GroupType.Month: "%Y-%m-01T00:00:00",
}

STEP_BY_GROUP_TYPE = {
    GroupType.Hour: relativedelta(hours=1),
    GroupType.Day: relativedelta(days=1),
    GroupType.Month: relativedelta(months=1)
}


def _get_iso_dates_list(
    date_from: datetime,
    date_to: datetime,
    time_span: GroupType,
) -> List[str]:
    """ Получить список iso дат, входящих в желаемый диапазон. """
    new_date = date_from
    dates = []
    step = STEP_BY_GROUP_TYPE[time_span]

    while new_date <= date_to:
        dates.append(new_date)
        new_date += step

    return [date.isoformat() for date in dates]


async def get_aggregated_data(
    collection: AsyncIOMotorCollection,
    date_from: datetime,
    date_to: datetime,
    time_span: GroupType
) -> Optional[Dict]:
    """ Получение агрегированных данных. """

    date_format = FORMAT_BY_GROUP_TYPE[time_span]

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

    stage_project_first = {
        "$project": {
            "_id": False,
            "date": '$_id',
            "sum": True,
        }
    }

    stage_group_test = {
        "$group": {
            "_id": None,
            "points": {"$push": "$$ROOT"}
        }
    }

    dates = _get_iso_dates_list(date_from, date_to, time_span)

    stage_project_second = {
        "$project":{
            "points": {
                "$map": {
                    "input": dates,
                    "as": "date",
                    "in": {
                        "$let": {
                            "vars": {
                                "dateIndex": {
                                    "$indexOfArray": ["$points.date", "$$date"]
                                }
                            },
                            "in": {
                                "$cond": {
                                    "if": {"$ne": ["$$dateIndex", -1]},
                                    "then": {
                                        "$arrayElemAt": [
                                            "$points",
                                            "$$dateIndex",
                                        ]
                                    },
                                    "else": {"sum": 0, "date": "$$date"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    stage_unwind = {
        "$unwind": "$points"
    }

    stage_replace_root = {
        "$replaceRoot": {"newRoot": "$points"}
    }

    stage_group_second = {
        "$group": {
          "_id": None,
          "dataset": {"$push": "$sum"},
          "labels": {"$push": "$date"},
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
            stage_project_first,
            stage_group_test,
            stage_project_second,
            stage_unwind,
            stage_replace_root,
            stage_group_second,
            stage_project,
        ]
    )

    result = await cursor.to_list(length=1)

    if result:
        return result[0]
