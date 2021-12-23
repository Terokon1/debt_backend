import contextlib

from django.db.models.signals import post_save
from django.dispatch import Signal
from rest_framework.test import APITestCase

from debts.models import DebtRequest
from debts.signals import (
    notify_debt_request_creator,
    notify_request_created,
    debt_request_done,
)


class DefaultAPITestCase(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self._disconnect_signals()

    def tearDown(self) -> None:
        super().tearDown()
        self._connect_signals()

    @staticmethod
    def _disconnect_signals():
        Signal.disconnect(debt_request_done, notify_debt_request_creator, sender=DebtRequest)
        Signal.disconnect(post_save, notify_request_created, sender=DebtRequest)

    @staticmethod
    def _connect_signals():
        Signal.connect(debt_request_done, notify_debt_request_creator, sender=DebtRequest)
        Signal.connect(post_save, notify_request_created, sender=DebtRequest)

    @contextlib.contextmanager
    def restore_signals(self):
        try:
            self._connect_signals()
            yield
        finally:
            self._disconnect_signals()
