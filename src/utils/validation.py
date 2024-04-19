import re

_pattern = re.compile(r'^(\d{4})-0?(\d+)-0?(\d+)[T]0?(\d+):0?(\d+):0?(\d+)$')


def validate_iso_string(iso_string: str) -> bool:
    """ Валидация iso формата даты. """
    return isinstance(_pattern.match(iso_string), re.Match)
