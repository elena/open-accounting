# -*- coding: utf-8 -*-
from django.conf.urls import url

from rest_framework import routers

# internal apps
from entities import views as entities_views
from subledgers.bank_reconciliations import views as bank_reconciliations_views


additional_routing_patterns = [

    url(r'^bank-reconciliations/(?P<pk>[0-9]+)/$',
        bank_reconciliations_views.BankTransactionViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'post': 'update',
            'patch': 'partial_update'})
        ),
]


router = routers.SimpleRouter()


# Entities
router.register(r'entities',
                entities_views.EntityViewSet)


# Subledgers
router.register(r'bank-reconciliations',
                bank_reconciliations_views.BankTransactionViewSet)


urlpatterns = additional_routing_patterns + router.urls
