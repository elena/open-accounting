from django.conf.urls import include, url

from reports.ledgers import views as ledgers_views


urls = [

    url(r'^tb/$',
        ledgers_views.TrialBalanceView.as_view(),
        name="trial-balance"),

    # url(r'^(?P<account>[0-9\-]+)/$',
    #     # views.BankReconciliationView.as_view(),
    #     views.bank_reconciliation,
    #     name='bank-reconciliation'
    #     ),

]

urlpatterns = [url(r'^', include(urls, namespace='reports'))]
