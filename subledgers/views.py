# -*- coding: utf-8 -*-
from django.shortcuts import render

from subledgers.forms import UploadForm


def upload_view(request, import_function=None):

    template_name = 'subledgers/upload_form.html'
    context_data = {}

    if request.method == 'POST':
        form = UploadForm(request.POST)

        if form.is_valid():
            data = utils.dump_to_kwargs(request.POST['input_data'],
                                        request.user,
                                        request.POST['object_name'])
            context_data['results'] = utils.create_objects(data)
            template_name = 'subledgers/upload_form.html'
            return render(request, template_name, context_data)
    else:
        form = UploadForm()

    context_data['form'] = form
    return render(request, template_name, context_data)
