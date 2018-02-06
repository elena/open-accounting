from django.urls import path

from . import views


app_name = 'ledgers'

urlpatterns = [
    path('accounts/',
         views.AccountListView.as_view(),
         name="accounts-list"),
]
