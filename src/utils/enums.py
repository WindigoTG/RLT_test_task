from enum import Enum, EnumMeta


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseEnum(Enum, metaclass=MetaEnum):
    pass


class GroupType(BaseEnum):
    """ Перечисление доступных типов группировки данных. """
    Hour = "hour"
    Day = "day"
    Month = "month"
