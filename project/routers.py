# -*- coding: utf-8 -*-

from rest_framework import routers

# internal apps
from entities import views as entities_views

router = routers.SimpleRouter()


# Entities
router.register(r'entities',
                entities_views.EntityViewSet)


urlpatterns = router.urls
