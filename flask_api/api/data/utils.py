import attr


@attr.s(frozen=True)
class Default:
    DATETIME_FORMAT = '%m/%d/%Y, %H:%M:%S'
    DATETIME_ARG_FORMAT = '%Y-%m-%d-%H-%M-%S'
