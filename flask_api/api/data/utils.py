import attr


@attr.s(frozen=True)
class Default:
    DATETIME_FORMAT = "%m/%d/%Y, %H:%M:%S"
