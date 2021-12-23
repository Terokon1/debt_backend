from django.urls import path

from debts.api import DebtAPIView, DebtRequestAPIView

app_name = 'debts'
urlpatterns = [
    path('', DebtAPIView.as_view(), name='debts'),
    path('requests/', DebtRequestAPIView.as_view(), name='debts_requests'),
]
