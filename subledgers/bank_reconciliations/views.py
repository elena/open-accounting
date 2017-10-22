# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views import generic

# from rest_framework import permissions
from rest_framework import viewsets

from ledgers.models import Account, Transaction
from ledgers.utils import get_source, make_date
from ledgers.bank_accounts.models import BankAccount

from .forms import StatementUploadForm, BankReconciliationForm
from .models import BankLine
from .serializers import BankLineSerializer
from .utils import import_bank_statement


class BankLineViewSet(viewsets.ModelViewSet):
    queryset = BankLine.objects.all()
    serializer_class = BankLineSerializer
    # permission_classes = [permissions.IsAdminUser]


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
    context_data['object_list'] = BankLine.objects.unreconciled()
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
                'source': get_source(BankLine)
            }
            new_transaction = Transaction(**kwargs)
            new_transaction.save(lines=lines)
            this = BankLine.objects.get(pk=form.cleaned_data.get('pk'))
            this.transaction = new_transaction
            this.save()
            context_data['success'] = "{} {}".format(this, this.transaction)
    return render(request, template_name, context_data)


class BankLineListView(generic.list.ListView):

    model = BankLine
    template_name = 'subledgers/bank_reconciliations/banktransaction_table.html'  # noqa


class BankAccountListView(generic.list.ListView):

    model = BankAccount
    template_name = 'subledgers/bank_reconciliations/bankaccount_list.html'
