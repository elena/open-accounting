from django.conf.urls import include, url

from reports.ledgers import views as ledgers_views


urls = [

    url(r'^tb/$',
        ledgers_views.TrialBalanceView.as_view(),
        name="trial-balance"),

    url(r'^account/(?P<account>[0-9\-]+)/$',
        ledgers_views.AccountDetailView.as_view(),
        name='account-detailview'),

]

urlpatterns = [url(r'^', include(urls, namespace='reports'))]
