# -*- coding: utf-8 -*-
from django.views import generic

from ledgers import utils
from ledgers.models import Account


class AccountSet(object):

    # pretty sure this is quite independant, could be put in utils instead
    def get_accounts_set_year(self, fyear):

        months_set = ["" for x in range(0, 12)]
        accounts_set = [
            {'account': a, 'month': ["" for x in range(0, 13)]}
            for a in Account.objects.all().total()
            if a.total]
        months_list = utils.get_months(fyear)

        for i, month in enumerate(months_list):
            for acc_year in accounts_set:
                acc_mth = Account.objects.month(month).total().by_code(
                    acc_year['account'].get_code())
                if acc_mth:
                    acc_year['month'][i] = utils.make_CRDR(acc_mth.total)
                    acc_year['month'][12] = utils.make_CRDR(
                        acc_year['account'].total)

        return accounts_set, months_set


class TrialBalanceView(AccountSet, generic.list.ListView):

    model = Account
    template_name = 'reports/ledgers/trial_balance.html'  # noqa

    def get_context_data(self, *args, **kwargs):
        context = super(TrialBalanceView, self).get_context_data(
            *args, **kwargs)

        fyear = CurrentFinancialYear.objects.get().current_financial_year
        accounts_set, months_set = self.get_accounts_set_year(fyear)

        context['accounts_set'] = accounts_set
        context['months_set'] = months_set
        context['months_headers'] = utils.get_months(fyear)
        return context
