""" Scheduled Job Client exceptions
"""

class InvalidJobConfig(Exception):
    pass


class InvalidJobRequest(Exception):
    pass


class ScheduleJobClientNoOp(Exception):
    pass
