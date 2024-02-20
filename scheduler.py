import json
import os
import itertools
import pandas as pd
import numpy as np
import pytz

from psinterface import register_task


from datetime import datetime, date, timedelta

# TODO: reimplement interval handling with portion

LOCALTIMEZONE = pytz.timezone("America/New_York")


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


def get_random_times(day, num=1, time_bounds=None, buffer=None):
    """Picks `num` times in the `allowed_range` of `day`, with at least `buffer` minutes between them.
    Throws an exception if this is not possible"""
    start, end = time_bounds["start"], time_bounds["end"]
    start = datetime.combine(day, start)
    end = datetime.combine(day, end)

    num_mins = (end - start).seconds // 60
    assert num_mins > 0, "End time must be after start time"
    if buffer is None:
        return [start + timedelta(minutes=m) for m in np.random.randint(num_mins)]

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

        timezone_time = LOCALTIMEZONE.localize(
            start + timedelta(minutes=actual_minutes), is_dst=None
        )
        res.append(timezone_time)

        interval_deletion(
            intervals,
            (actual_minutes - buffer, actual_minutes + buffer),
        )

    return res


def main():
    with open("schedules.json") as f:
        schedules = json.load(f)["schedule-info"]

    tomorrow = date.today() + timedelta(days=1)

    # TODO: for high frequency events, random.choice will scale too slowly
    for schedule in schedules:
        repetition_dist = schedule["repetition-probs"]
        if schedule["frequency"] == "daily":
            days = list(pd.date_range(tomorrow, periods=7))

            time_bounds = {
                k: datetime.strptime(v, "%H%M").time()
                for k, v in schedule["time-bounds"].items()
            }

            nums = np.random.choice(
                list(map(lambda x: int(x), repetition_dist.keys())),
                p=list(repetition_dist.values()),
                size=(len(days),),
            )

            try:
                datetimes = list(
                    itertools.chain.from_iterable(
                        [
                            get_random_times(day, num, time_bounds, buffer=60)
                            for day, num in zip(days, nums)
                        ]
                    )
                )
            except Exception as e:
                raise Exception(
                    f"There was an issue selected a valid set of times! {str(e)}"
                )
        else:
            raise NotImplementedError("Only daily schedules are currently supported")

        # TODO: implement scheduling here
        filename = schedule["file"]
        file_path = os.path.join("api-calls", filename)
        for dt in datetimes:
            register_task(file_path, dt, f"Run {filename}")


if __name__ == "__main__":
    with open("cache/log.txt", "a") as f:
        f.write(str(datetime.now().replace(microsecond=None)) + "\n")
    main()
