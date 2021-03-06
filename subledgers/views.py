# -*- coding: utf-8 -*-
# from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.utils.module_loading import import_string

from ledgers import utils
from subledgers.forms import UploadForm, BasicForm
from subledgers.models import Entry


def upload_view(request, import_function=None):

    if request.user.is_authenticated:

        template_name = 'subledgers/upload_form.html'
        context_data = {}

        if request.method == 'POST':
            form = UploadForm(request.POST)
            context_data['dump'] = request.POST

            print(request.POST)

            if request.POST.get('object_name'):
                data = Entry.dump_to_objects(
                    request.POST['input_data'],
                    request.user, request.POST['object_name'],
                    live=int(request.POST['live']),
                )
            else:
                data = Entry.dump_to_objects(
                    request.POST['input_data'], request.user,
                    live=int(request.POST['live']),
                )
            template_name = 'subledgers/upload_form.html'
            context_data['results'] = data
            form = UploadForm()
            context_data['form'] = form
            return render(request, template_name, context_data)
        else:
            form = UploadForm()
            context_data['form'] = form
            return render(request, template_name, context_data)
    else:
        return redirect("/admin/login/?next=/upload/")


def dump_view(request):

    template_name = 'dump.html'
    context_data = {}

    form = BasicForm()
    context_data['form'] = form

    if request.method == 'POST':
        context_data['results'] = request.POST
        return render(request, template_name, context_data)

    return render(request, template_name, context_data)
