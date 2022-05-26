import datetime as dt
import pytz


def to_timezone(datetime_value, tz):
    """
    Convert the given datetime object to a datetime object with the given timezone.
    Accepts both aware and naive datetime objects

    Parameters
    ----------
    datetime_value: datetime.datetime
    tz: pytz.timezone

    Returns
    -------
    datetime.datetime
    """
    if not isinstance(datetime_value, dt.datetime):
        raise SyntaxError

    if not hasattr(tz, "zone") or tz.zone not in pytz.all_timezones:
        raise SyntaxError

    if (
        datetime_value.tzinfo is not None
        and datetime_value.tzinfo.utcoffset(datetime_value) is not None
    ):
        datetime_value = datetime_value.astimezone(tz)
    else:
        datetime_value = tz.localize(datetime_value)

    return datetime_value
