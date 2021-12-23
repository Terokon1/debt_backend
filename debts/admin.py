from django.contrib import admin

from debts.models import Debt, DebtRequest

admin.site.register(Debt)
admin.site.register(DebtRequest)
