from django.db.models import Q, QuerySet

from accounts.models import Account
from debts.models import Debt, DebtRequest


def get_related_debts(user: Account) -> QuerySet[Debt]:
    return Debt.objects \
        .filter(Q(debtor=user) | Q(creditor=user)) \
        .order_by('-created')


def get_related_debt_requests(user: Account) -> QuerySet[Debt]:
    return DebtRequest.objects \
        .filter(Q(debtor=user) | Q(creditor=user)) \
        .filter(connected_debt__isnull=True, declined=False) \
        .order_by('-created')
