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
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from . import routers
from subledgers.views import upload_view, dump_view, test_view


urlpatterns = [

    # trivial urls
    path('', TemplateView.as_view(template_name="index.html")),
    path('demo/', TemplateView.as_view(template_name="demo.html")),

    path('dump/', dump_view, name="dump-view"),

    path('test/', test_view, name="test-view"),

    # "The Upload"
    path('upload/', upload_view, name="upload-view"),

    # internal app urls

    path('ledgers/', include('ledgers.urls')),

    # re_path(r'^journals/',
    #     include('subledgers.journals.urls')),

    path('bank/reconciliations/',
         include('subledgers.bank_reconciliations.urls')),

    path('acp/', include('subledgers.creditors.urls')),

    # reports

    path(r'reports/', include('reports.urls')),

    # external urls

    # re_path(r'^api/', include(routers, namespace='api')),

    re_path(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
