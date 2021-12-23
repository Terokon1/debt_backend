import contextlib

import factory
from django.db.models import Model, ProtectedError
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDecimal


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = 'accounts.Account'

    username = factory.Faker('user_name')
    password = factory.Faker('password')


class FriendRequestFactory(DjangoModelFactory):
    class Meta:
        model = 'accounts.FriendRequest'

    from_user = factory.SubFactory(AccountFactory)
    to_user = factory.SubFactory(AccountFactory)


class DebtFactory(DjangoModelFactory):
    class Meta:
        model = 'debts.Debt'

    money = FuzzyDecimal(0.1, 10000.33)
    creditor = factory.SubFactory(AccountFactory)
    debtor = factory.SubFactory(AccountFactory)
    description = factory.Faker('text')


class DebtRequestFactory(DjangoModelFactory):
    class Meta:
        model = 'debts.DebtRequest'

    money = FuzzyDecimal(0.1, 10000.33)
    creditor = factory.SubFactory(AccountFactory)
    debtor = factory.SubFactory(AccountFactory)
    description = factory.Faker('text')


@contextlib.contextmanager
def delete_after(obj: Model) -> Model:
    try:
        yield obj
    finally:
        try:
            obj.delete()
        except ProtectedError:
            pass
