# TODO: This should somehow compute the schedule for data collection, and set up cron jobs accordingly (?)

# How should I compute times?
import json
import os
from datetime import datetime, date, time
import pandas as pd
import numpy as np


# class AllowedRange:
#     def __init__(self, start_time, end_time):
#         self.start = start_time
#         self.end = end_time

#     def contains(self, element):
#         # Should I try to convert element to a datetime object to check for inclusion?
#         pass


with open("schedules.json") as f:
    schedules = json.load(f)["schedule-info"]

today = date.today()

# TODO: for high frequency events, random.choice will scale too slowly
for schedule in schedules:
    file = os.path.join("api-calls", schedule["file"])
    repetition_dist = file["repetition-probs"]
    time_bounds = {k: time.strptime(v, "%H%M") for k, v in file["time-bounds"]}
    if file["frequency"] == "daily":
        days = list(pd.date_range(today, periods=7))
        nums = np.random.choice(
            list(range(len(repetition_dist))), p=repetition_dist, size=(len(days),)
        )
        try:
            datetimes = [
                get_random_times(day, num, time_bounds, buffer=60)
                for day, num in zip(days, nums)
            ]
        except Exception as e:
            raise Exception(
                f"There was an issue selected a valid set of times! {e.message}"
            )
    else:
        raise NotImplementedError("Currently only accepts daily schedules")

    # TODO: implement scheduling here
    print(datetimes)


def get_random_times(day, num=1, time_bounds=None, buffer=None):
    """Picks `num` times in the `allowed_range` of `day`, with at least `buffer` minutes between them.
    Throws an exception if this is not possible"""
    start, end = time_bounds
    num_mins = (end - start).minutes
    # from now on we need the starting time to includ the date
    start_dt = datetime.combine(day, start)
    assert num_mins > 0, "End time must be after start time"
    if buffer is None:
        return [
            start_dt + datetime.timedelta(minutes=m)
            for m in np.random.randint(num_mins)
        ]

    intervals = [(0, num_mins)]
    res = []
    # TODO: this doesn't deal with the edge case where some choices of initial time succeed and some fail
    for _ in range(num):
        # intervals are inclusive
        sizes = [b - a + 1 for a, b in intervals]
        minute_selected = np.random.randint(sum(sizes))

        # determine the i-th minute in valid_intervals
        # valid_intervals should never overlap and should always remain sorted
        i = 0
        next_size = sizes[0]
        while i < len(intervals) - 1 and minute_selected > next_size:
            i += 1
            minute_selected -= next_size
            next_size = sizes[i]
        actual_minutes = intervals[i][0] + minute_selected
        res.append(start_dt + datetime.timedelta(minutes=actual_minutes))

        interval_deletion(
            intervals,
            (actual_minutes - buffer, actual_minutes + buffer),
        )

    return res


def interval_deletion(intervals, invalid_interval):
    # each interval in `intervals` is inclusive, and the `invalid_interval` is deleted inclusively as well
    invalid_start, invalid_end = invalid_interval
    i = 0
    while i < len(intervals):
        # guaranteed a < b
        a, b = intervals[i]

        if a > invalid_end:
            # valid because intervals remain sorted
            break
        if b < invalid_start:
            i += 1
            continue

        # guaranteed a <= ie and b >= is. here 'is' refers to invalid start and 'ie' to inv. end
        # a  .  .  .  b  .
        # . is  .  .  . ie
        if a < invalid_start and b <= invalid_end:
            intervals[i] = (a, invalid_start - 1)

        # .  a  .  .  .  b
        # is .  .  ie .  .
        if a >= invalid_start and b > invalid_end:
            intervals[i] = (invalid_end + 1, b)

        #  .  a  .  b  .  .
        # is  .  .  .  . ie
        if a >= invalid_start and b <= invalid_end:
            # just delete this interval
            intervals.pop(i)

        # a  .  .  .  b
        # .  is  . ie .
        if a < invalid_start and b > invalid_end:
            intervals[i] = (invalid_end + 1, b)
            intervals.insert(i, (a, invalid_start - 1))
