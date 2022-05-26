---
published: true
title: 'Snippet: Change timezone for DateTime object'
cover_image: 'https://raw.githubusercontent.com/petervanderdoes/dev.to/main/blog-posts/snippet-0001-to-timezone/assets/cover.png'
description: 'Convert a DateTime object from one timezone to another timezone'
tags: Python, snippets
series:
canonical_url:
---

## Information

Convert a Python DateTime object from one timezone to another timezone. This snippet accepts either a naive or aware DateTime object.

## Snippet

```py
# code/timezone.py

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

```

## Found a typo?

If you've found a typo, a sentence that could be improved or anything else that should be updated on this blog post, you can access it through a git repository and make a pull request. Instead of posting a comment, please go directly to [GitHub](https://github.com/petervanderdoes/dev.to/tree/main/blog-posts/snippet-0001-to-timezone) and open a pull request with your changes.

---

###### Photo by Ijaz Rafi - https://unsplash.com/photos/L4hg5o67jdw
