from django.conf.urls import include, url
from . import views


urls = [

    # Statement upload
    url(r'^statements/$',
        views.add_statements,
        name='bank-statement-upload'
    ),

]

urlpatterns = [url(r'^', include(urls, namespace='bank-reconciliations'))]
