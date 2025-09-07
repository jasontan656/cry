from datetime import datetime, timezone, timedelta

import uuid

class Time :

    PHILIPPINES_TZ = timezone(timedelta(hours=8))

    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

    @classmethod
    def now(cls) -> datetime:

        return datetime.now(cls.PHILIPPINES_TZ)

    @classmethod
    def timestamp(cls) ->str:

        current_time = cls.now().strftime(cls.TIMESTAMP_FORMAT)
        unique_id = str(uuid.uuid4())
        timestamp_with_uuid = f"{current_time}_{unique_id}"
        return timestamp_with_uuid
# output format ex : 2024-01-15T14:30:25+0800_12345678-1234-5678-9012-123456789012
time = Time()
