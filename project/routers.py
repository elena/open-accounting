# -*- coding: utf-8 -*-
from django.conf.urls import url

from rest_framework import routers

# internal apps
from entities import views as entities_views
from ledgers import views as ledgers_views
from subledgers.bank_reconciliations import views as bank_reconciliations_views


additional_routing_patterns = [

    url(r'^bank-reconciliations/(?P<pk>[0-9]+)/$',
        bank_reconciliations_views.BankLineViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'post': 'update',
            'patch': 'partial_update'})
        ),
]


router = routers.SimpleRouter()

# Django Contrib
router.register(r'users',
                ledgers_views.UserViewSet)

# Entities
router.register(r'entities',
                entities_views.EntityViewSet)

# Ledgers
router.register(r'ledgers',
                ledgers_views.TransactionViewSet)

# Subledgers
router.register(r'bank-reconciliations',
                bank_reconciliations_views.BankLineViewSet)


urlpatterns = additional_routing_patterns + router.urls
