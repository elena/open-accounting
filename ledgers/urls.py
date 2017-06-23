from django.conf.urls import include, url

from . import views


urls = [

    url(r'^accounts/$',
        views.AccountListView.as_view(),
        name="accounts-list"),

]

urlpatterns = [url(r'^', include(urls, namespace='ledgers'))]
