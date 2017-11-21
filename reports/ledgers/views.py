# -*- coding: utf-8 -*-
from django.views import generic

from ledgers import utils
from ledgers.models import Account, Transaction
from ledgers.periods.models import CurrentFinancialYear


class AccountSet(object):

    # pretty sure this is quite independant, could be put in utils instead
    def get_accounts_set_year(self, months_list):

        accounts_set = [
            {'account': a, 'month': [
                "" for x in range(0, len(months_list) + 1)]}
            for a in Account.objects.all().total()
            if a.total]

        for i, month in enumerate(months_list):
            for acc_year in accounts_set:
                acc_mth = Account.objects.month(month).total().by_code(
                    acc_year['account'].get_code())
                if acc_mth:
                    acc_year['month'][i] = utils.make_CRDR(acc_mth.total)
                    acc_year['month'][len(months_list)] = utils.make_CRDR(
                        acc_year['account'].total)

        return accounts_set


class TrialBalanceView(AccountSet, generic.list.ListView):

    model = Account
    template_name = 'reports/ledgers/trial_balance.html'  # noqa

    def get_context_data(self, *args, **kwargs):
        context = super(TrialBalanceView, self).get_context_data(
            *args, **kwargs)
        if self.kwargs.get('start') and self.kwargs.get('end'):
            months_list = utils.get_months(
                self.kwargs.get('start'), self.kwargs.get('end'))
        else:
            fyear = CurrentFinancialYear.objects.get().current_financial_year
            months_list = utils.get_months_fyear(fyear)

        context['accounts_set'] = self.get_accounts_set_year(months_list)
        context['months_headers'] = months_list
        return context


class AccountDetailView(generic.detail.DetailView):

    model = Account
    template_name = 'reports/ledgers/account_detail.html'  # noqa

    def get_object(self, *args, **kwargs):
        return self.get_queryset().by_code(self.kwargs['account'])

    def get_context_data(self, *args, **kwargs):
        context = super(AccountDetailView, self).get_context_data(
            *args, **kwargs)

        context['transaction_list'] = t = Transaction.objects.filter(
            lines__account=self.get_object()).order_by('date')
        print(t)
        return context
