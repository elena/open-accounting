from django.urls import path, re_path

from reports.ledgers import views as ledgers_views
from reports.subledgers import views as subledgers_views

urlpatterns = [

    path('tb/',
         ledgers_views.TrialBalanceView.as_view(),
         name="trial-balance"),

    re_path(r'^tb/(?P<start>[0-9\-]{7})/(?P<end>[0-9\-]{7})/$',
            ledgers_views.TrialBalanceView.as_view(),
            name="trial-balance-date"),

    re_path(r'^account/(?P<account>[0-9\-]+)/$',
            ledgers_views.AccountDetailView.as_view(),
            name='account-detailview'),

    path('entity/',
         subledgers_views.EntityListView.as_view(),
         name='entity-listview'),

    re_path(r'^entity/(?P<code>.{0,6})/$',
            subledgers_views.EntityDetailView.as_view(),
            name='entity-detailview'),

    path('creditors/',
         subledgers_views.CreditorListView.as_view(),
         name='creditor-listview'),

    re_path(r'^creditors/(?P<code>[\W]{0,6})/$',
            subledgers_views.CreditorDetailView.as_view(),
            name='creditor-detailview'),
]
