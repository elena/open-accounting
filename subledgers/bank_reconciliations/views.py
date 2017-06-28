# -*- coding: utf-8 -*-
# from django.core.urlresolvers import reverse, reverse_lazy
# from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.views import generic

from rest_framework import viewsets

from ledgers.utils import get_source, make_date
from .models import BankTransaction
from .serializers import BankTransactionSerializer

class BankTransactionViewSet(viewsets.ModelViewSet):
    queryset = BankTransaction.objects.all()
    serializer_class = BankTransactionSerializer


from ledgers.models import Account, Transaction
from ledgers.utils import get_source
from ledgers.bank_accounts.models import BankAccount

from .forms import StatementUploadForm, BankReconciliationForm
from .models import BankTransaction
def add_statements(request):
    """ Upload statements view. """

    template_name = 'subledgers/bank_reconciliations/form_statements.html'
    context_data = {}

    if request.method == 'POST':
        form = StatementUploadForm(request.POST)
        if form.is_valid():
            context_data['success_obj'] = import_bank_statement(request.POST)
    else:
        form = StatementUploadForm()

    context_data['form'] = form
    return render(request, template_name, context_data)


def bank_reconciliation(request, account):

    template_name = 'subledgers/bank_reconciliations/banktransaction_list.html'

    context_data = {}
    context_data['object_list'] = BankTransaction.objects.unreconciled()
    context_data['bank_account'] = Account.objects.by_code(account)
    context_data['account_list'] = Account.objects.regular(
    ).order_by('element', 'number')

    if request.method == 'POST':
        form = BankReconciliationForm(request.POST)
        context_data['success'] = request.POST
        if form.is_valid():
            value = form.cleaned_data.get('value')
            line_account = form.cleaned_data.get('account')
            lines = (account, line_account, value)
            kwargs = {
                'user': request.user,
                'date':  make_date(str(form.cleaned_data.get('date'))),
                'source': get_source(BankTransaction)
            }
            new_transaction = Transaction(**kwargs)
            new_transaction.save(lines=lines)
            this = BankTransaction.objects.get(pk=form.cleaned_data.get('pk'))
            this.transaction = new_transaction
            this.save()
            context_data['success'] = "{} {}".format(this, this.transaction)
    return render(request, template_name, context_data)


class BankTransactionListView(generic.list.ListView):

    model = BankTransaction
    template_name = 'subledgers/bank_reconciliations/banktransaction_table.html'  # noqa


class BankAccountListView(generic.list.ListView):

    model = BankAccount
    template_name = 'subledgers/bank_reconciliations/bankaccount_list.html'
