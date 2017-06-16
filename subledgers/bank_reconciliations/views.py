# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views import generic

from .forms import StatementUploadForm
from .utils import bank_statement_import


def add_statements(request):
    """ Upload statements view. """

    template_name = 'subledgers/bank_reconciliations/form_statements.html'
    context_data = {}

    if request.method == 'POST':
        form = StatementUploadForm(request.POST)
        if form.is_valid():
            context_data['success_obj'] = bank_statement_import(request.POST)
    else:
        form = StatementUploadForm()

    context_data['form'] = form
    return render(request, template_name, context_data)
