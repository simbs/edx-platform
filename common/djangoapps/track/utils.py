"""Utility functions and classes for track backends"""

from datetime import datetime, date
import json
import logging

from pytz import UTC

application_log = logging.getLogger('track.backends.application_log')  # pylint: disable=invalid-name


class DateTimeJSONEncoder(json.JSONEncoder):
    """JSON encoder aware of datetime.datetime and datetime.date objects"""

    def default(self, obj):  # pylint: disable=method-hidden
        """
        Serialize datetime and date objects of iso format.

        datatime objects are converted to UTC.
        """
        if isinstance(obj, datetime):
            if obj.tzinfo is None:
                # Localize to UTC naive datetime objects
                obj = UTC.localize(obj)
            else:
                # Convert to UTC datetime objects from other timezones
                obj = obj.astimezone(UTC)
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()

        return super(DateTimeJSONEncoder, self).default(obj)

    def encode(self, obj):
        """
        encode method gets an original object
        and returns result string. obj argument will be the
        object that is passed to json.dumps function
        """
        for key in obj.iterkeys():
            if isinstance(obj[key], str):
                try:
                    obj[key].decode('utf8')
                except UnicodeDecodeError:
                    # Will throw UnicodeDecodeError in cases when there are
                    # latin1 encoded characters in string.
                    #  Example {'string': '\xd3 \xe9 \xf1'}
                    application_log.warning("UnicodeDecodeError Event-Data: %s", obj[key])
                    obj[key] = obj[key].decode('latin1')

        return super(DateTimeJSONEncoder, self).encode(obj)

