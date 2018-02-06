# -*- coding: utf-8 -*-
from django.urls import path

from . import views


app_name = 'bank-reconciliations'

urlpatterns = [

    # Reconcile index
    path('',
         views.BankAccountListView.as_view(),
         name='bank-reconciliation-index'),

    # Categorisation view
    path('sort/',
         views.bank_categorisation,
         name='bank-categorisation'),

    # Bank reconciliation by Account
    path('<int:account>/',
         views.bank_reconciliation,
         name='bank-reconciliation'),

    # Reconcile listview
    path('table/',
         views.BankLineListView.as_view(),
         name='bank-transaction-listview'),

    # Statement upload
    path('statements/',
         views.add_statements,
         name='bank-statement-upload'),

    # API urls
    path('api/<int:pk>/',
         views.BankLineViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'post': 'update',
             'patch': 'partial_update'})),
]
