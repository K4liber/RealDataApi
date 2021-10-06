import attr


@attr.s(frozen=True)
class Default:
    DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'
    DATETIME_ARG_FORMAT = '%Y-%m-%d-%H-%M-%S'
    TIMESTAMPS_RANGE_IN_DAYS = 7
