# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from . import views


urls = [

    # Reconcile index
    url(r'^$',
        views.BankAccountListView.as_view(),
        name='bank-reconciliation-index'
        ),

    # Categorisation view
    url(r'^sort/$',
        views.bank_categorisation,
        name='bank-categorisation'
        ),

    # Bank reconciliation by Account
    url(r'^(?P<account>[0-9\-]+)/$',
        views.bank_reconciliation,
        name='bank-reconciliation'
        ),

    # Reconcile listview
    url(r'^table/$',
        views.BankLineListView.as_view(),
        name='bank-transaction-listview'
        ),

    # Statement upload
    url(r'^statements/$',
        views.add_statements,
        name='bank-statement-upload'
        ),

    # API urls
    url(r'^api/(?P<pk>[0-9]+)/$',
        views.BankLineViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'post': 'update',
            'patch': 'partial_update'})
        ),
]

urlpatterns = [url(r'^', include(urls, namespace='bank-reconciliations'))]
