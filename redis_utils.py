from typing import NamedTuple, Iterable

from django_redis import get_redis_connection
from rest_framework.renderers import JSONRenderer


class Event(NamedTuple):
    user_id: str
    data: dict

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'data': self.data,
        }


def send_to_pub(events: Iterable[Event]):
    connection = get_redis_connection("default")
    payload = JSONRenderer().render([event.to_dict() for event in events])
    connection.publish("events", payload)
