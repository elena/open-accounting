from django.conf.urls import include, url
from . import views


urls = [

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

]

urlpatterns = [url(r'^', include(urls, namespace='bank-reconciliations'))]
