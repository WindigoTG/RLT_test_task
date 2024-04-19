import json
from datetime import datetime
from json import JSONDecodeError
from typing import Optional, Tuple


from utils.enums import GroupType
from utils.validation import validate_iso_string


def parse_incoming_data(
    data_string: str,
) -> Optional[Tuple[datetime, datetime, GroupType]]:
    """ Распарсить входящий запрос от пользователя. """
    try:
        request_data = json.loads(data_string)
    except JSONDecodeError:
        return

    date_from = request_data.get('dt_from')
    date_to = request_data.get('dt_upto')
    group_type = request_data.get('group_type')

    if len(request_data) != 3 or not all((date_from, date_to, group_type)):
        return

    if not all(
        (
            validate_iso_string(date_from),
            validate_iso_string(date_to),
            group_type in GroupType,
        )
    ):
        return

    try:
        date_from = datetime.fromisoformat(date_from)
        date_to = datetime.fromisoformat(date_to)
        group_type = GroupType(group_type)
    except ValueError:
        return

    return date_from, date_to, group_type
