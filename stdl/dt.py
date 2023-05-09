import random
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Generator

from dateutil.parser import parse as parse_datetime_str

local_tz = datetime.now().astimezone().tzinfo


@dataclass
class TimerStop:
    total: timedelta
    since_last: timedelta
    at: float
    label: str | None = None

    def __str__(self) -> str:
        if self.label is None:
            return f"total={self.total}, since_last=({self.since_last}), at={fmt_datetime(self.at)}"
        return f"{self.label} | total={self.total}, since_last={self.since_last}, at={fmt_datetime(self.at)}"


class Timer:
    """A simple timer class that keeps track of all the stops."""

    def __init__(self, *, ms: bool = True):
        self.ms = ms
        self.reset()

    def stop(self, label: str | None = None) -> TimerStop:
        """
        Stop the timer.

        Args:
            label (str | None, optional): Label for the stop. Defaults to None.

        Returns:
            TimerStop: The stop data
        """
        t = time.time()
        elapsed_total = t - self.start
        since_last = t - self.stops[-1].at
        if not self.ms:
            elapsed_total = round(elapsed_total)
            since_last = round(since_last)

        elapsed_total = timedelta(seconds=elapsed_total)
        since_last = timedelta(seconds=since_last)

        timer_stop = TimerStop(
            total=elapsed_total,
            since_last=since_last,
            at=t,
            label=label,
        )
        self.stops.append(timer_stop)
        return timer_stop

    def reset(self) -> None:
        """Reset the timer."""
        self.start = time.time()
        self.stops: list[TimerStop] = [
            TimerStop(
                total=timedelta(seconds=0),
                since_last=timedelta(seconds=0),
                at=self.start,
                label="start",
            )
        ]

    def print_stops(self) -> None:
        for stop in self.stops:
            print(stop)


def fmt_datetime(
    d: str | float | int | None | datetime = None,
    fmt: str = "Ymd",
    d_sep: str = "-",
    t_sep: str = ":",
    *,
    ms: bool = False,
    utc: bool = True,
) -> str:
    """Format date and time

    Args:
        d (str | float | None | datetime, optional): Input datetime. Defaults to None.
        fmt (str, optional): Date format. Defaults to "Ymd".
        d_sep (str, optional): Date values separator. Defaults to "-".
        t_sep (str, optional): Time values separator. Defaults to ":".
        ms (bool, optional): include miliseconds. Defaults to False.
        utc (bool, optional):  Use the UTC timezone when building a datetime object from a timestamp. Defaults to True.

    Raises:
        TypeError: Raises TypeError if the type of ``d`` is not one of the following: float, str, None, datetime, int

    Returns:
        str: Formated date and time.

    Examples:
    --------
    >>> fmt_datetime()
    '2022-11-22 22:40:04' # current date and time
    >>> fmt_datetime(0)
    "1970-01-01 00:00:00"
    >>> fmt_datetime(0, fmt="dmY", d_sep="/")
    "01/01/1970 00:00:00"
    """
    if d is None:
        d = datetime.fromtimestamp(time.time(), **{"tz": timezone.utc} if utc else {})

    elif isinstance(d, str):
        d = parse_datetime_str(d)
    elif isinstance(d, (float, int)):
        d = datetime.fromtimestamp(d, **{"tz": timezone.utc} if utc else {})
    elif isinstance(d, datetime):
        pass
    else:
        raise TypeError(type(d))
    date_fmt = f"%{fmt[0]}{d_sep}%{fmt[1]}{d_sep}%{fmt[2]}"
    time_fmt = f"%H{t_sep}%M{t_sep}%S"
    if ms:
        time_fmt += ".%f"
    dt_str = d.strftime(f"{date_fmt} {time_fmt}")
    return dt_str[:-3] if ms else dt_str


def fmt_time(
    t: float | datetime | int | None = None, sep: str = ":", *, ms: bool = False, utc: bool = True
) -> str:
    """
    Format time

    Args:
        t (float | datetime | int | None, optional): Input time. Defaults to current time if it's not provided.
        sep (str, optional): Character(s) that separates hours, minutes, seconds... Defaults to ":".
        ms (bool, optional): include miliseconds. Defaults to False.
        utc (bool, optional): Use the UTC timezone when building a time object from a timestamp. Defaults to True.

    Raises:
        TypeError: Raises TypeError if the type of ``t`` is not one of the following: float, None, datetime, int

    Returns:
        str: Formated time.
    """
    if t is None:
        tm = datetime.fromtimestamp(time.time(), **{"tz": timezone.utc} if utc else {})
    elif isinstance(t, datetime):
        tm = t.time()
    elif isinstance(t, (int, float)):
        tm = datetime.fromtimestamp(t, **{"tz": timezone.utc} if utc else {})
    else:
        raise TypeError(type(t))
    ts = tm.strftime(f"%H{sep}%M{sep}%S")
    if ms:
        ms_str = f"{int(tm.microsecond / 1000)}".zfill(3)
        ts = f"{ts}.{ms_str}"
    return ts


def fmt_date(
    d: float | date | datetime | int | None = None,
    fmt: str = "Ymd",
    sep: str = "-",
) -> str:
    """
    Format date

    Args:
        d (float | date | datetime | int | None ): Input date. Defaults to current date if it's not provided.
        fmt (str, optional): Date format. Defaults to "Ymd".
        sep (str, optional): Character(s) that separates days, months and years. Defaults to "-".

    Raises:
        TypeError: Raises TypeError if the type of ``d`` is not one of the following: float, None, date, datetime, int

    Returns:
        str: Formated date.

    Examples
    --------
    >>> fmt_date(date(2022,11,22))
    '2022-11-22'
    >>> fmt_date(date(2022,11,22), sep="/")
    '2022/11/22'
    >>> fmt_date(date(2022,11,22), sep="/", fmt="dmY")
    '22/11/2022'
    >>> fmt_date()
    '2022-11-22'
    """
    if d is None:
        d = date.fromtimestamp(time.time())
    elif isinstance(d, (float, int)):
        d = date.fromtimestamp(d)
    elif isinstance(d, datetime):
        d = d.date()
    elif isinstance(d, date):
        pass
    else:
        raise TypeError(type(d))
    return d.strftime(f"%{fmt[0]}{sep}%{fmt[1]}{sep}%{fmt[2]}")


def date_range(start: date, end: date) -> Generator[date, None, None]:
    """
    Returns a generator for dates between ``start`` and ``end``

    Examples
    --------
    >>> for i in date_range(date(2022,11,19), date(2022,11,22)): print(i)
    2022-11-19
    2022-11-20
    2022-11-21
    """
    for n in range(int((end - start).days)):
        yield start + timedelta(n)


def sleep(lo: float, hi: float | None = None) -> float:
    """
    Sleeps for a random duration within a specified range.

    Args:
        lo (float): The lower bound of the sleep duration range (inclusive).
        hi (float, optional): The upper bound of the sleep duration range (inclusive). If not provided, the function will sleep for the exact duration specified by `lo`.

    Returns:
        float: The actual sleep duration.

    Raises:
        ValueError: If `hi` is provided and `lo` is greater than `hi`.
    """

    if hi is None:
        time.sleep(lo)
        return lo
    if lo < hi:
        raise ValueError(f"Minimum sleep time is higher that maximum. {(lo,hi)}")
    t = random.uniform(lo, hi)
    time.sleep(t)
    return t


__all__ = [
    "Timer",
    "parse_datetime_str",
    "fmt_datetime",
    "fmt_time",
    "fmt_date",
    "date_range",
    "sleep",
    "local_tz",
    "timezone",
    "date",
    "datetime",
    "time",
]
