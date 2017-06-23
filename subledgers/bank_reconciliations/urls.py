# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from . import views


urls = [

    # Reconcile listview
    url(r'^$',
        views.BankAccountListView.as_view(),
        name='bank-reconciliation-index'
    ),

    # Statement upload
    url(r'^statements/$',
        views.add_statements,
        name='bank-statement-upload'
    ),

    url(r'^api/(?P<pk>[0-9]+)/$',
        views.BankTransactionViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'post': 'update',
            'patch': 'partial_update'})
    ),

    # Reconcile listview
    url(r'^(?P<account>[0-9\-]+)/$',
        views.bank_reconciliation,
        name='bank-reconciliation'
    ),

]

urlpatterns = [url(r'^', include(urls, namespace='bank-reconciliations'))]
