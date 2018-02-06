# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views import generic

# from rest_framework import permissions
from rest_framework import viewsets

from ledgers.bank_accounts.models import BankAccount
from ledgers.models import Account, Transaction
from ledgers.utils import get_source, make_date
from subledgers.settings import SUBLEDGERS_AVAILABLE


from .forms import StatementUploadForm, BankReconciliationForm
from .models import BankLine, BankEntry
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


def bank_categorisation(request):
    template_name = "subledgers/bank_reconciliations/bank_categorisation.html"
    context_data = {
        'object_list': BankLine.objects.unreconciled(),
        'subledger_list': SUBLEDGERS_AVAILABLE,
    }
    # @@TOOD: figure out how to display already sorted.

    if request.method == 'POST':
        context_data['request'] = request.POST
        subledger = request.POST['subledger']
        log = []

        for field in request.POST:
            if field.split('-')[0]=='catpk':
                # @@TODO make this a method of some kind.
                pk = field.split('-')[1]
                bank_line = BankLine.objects.get(pk=pk)
                if request.POST['manual-account']:
                    account = request.POST['manual-account']
                else:
                    account = SUBLEDGERS_AVAILABLE[subledger]['account']

                transaction_kwargs = {
                    'user': request.user,
                    'date':  bank_line.date,
                    'source': get_source(BankEntry),
                    'value': bank_line.value,
                    'account_DR': account,
                    'account_CR': bank_line.bank_account.account
                }
                bank_entry = BankEntry(
                    bank_line=bank_line,
                    subledger=subledger
                )
                bank_entry.save_transaction(transaction_kwargs)
                log.append(bank_entry)

        context_data['test'] = log

    return render(request, template_name, context_data)


def bank_reconciliation(request, account):

    template_name = 'subledgers/bank_reconciliations/banktransaction_list.html'

    context_data = {
        'object_list': BankLine.objects.unreconciled(),
        'bank_account': Account.objects.by_code(account),
        'account_list': Account.objects.regular(
        ).order_by('element', 'number')
    }

    if request.method == 'POST':
        form = BankReconciliationForm(request.POST)
        context_data['success'] = request.POST

        if form.is_valid():
            transaction_kwargs = {
                'user': request.user,
                'date':  str(form.cleaned_data.get('date')),
                'source': get_source(BankLine),
                'value': form.cleaned_data.get('value'),
                'account_DR': account,
                'account_CR': form.cleaned_data.get('account'),
            }
            this = BankLine.objects.get(pk=form.cleaned_data.get('pk'))
            this.save_transaction(transaction_kwargs)
            context_data['success'] = "{} {}".format(this, this.transaction)
    return render(request, template_name, context_data)


class BankLineListView(generic.list.ListView):

    model = BankLine
    template_name = 'subledgers/bank_reconciliations/banktransaction_table.html'  # noqa


class BankAccountListView(generic.list.ListView):

    model = BankAccount
    template_name = 'subledgers/bank_reconciliations/bankaccount_list.html'
