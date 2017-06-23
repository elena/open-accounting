# -*- coding: utf-8 -*-
"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from . import routers, views
from subledgers.views import upload_view


urlpatterns = [

    url(r'upload/', upload_view),

    # internal app urls

    url(r'^accounts/',
        include('ledgers.urls')),

    url(r'^bank/reconciliations/',
        include('subledgers.bank_reconciliations.urls')),


    # external urls

    url(r'^api/', include(routers, namespace='api')),

    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
