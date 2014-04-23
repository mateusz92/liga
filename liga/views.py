from django.shortcuts import render
from datetime import datetime
from django.db.utils import ConnectionDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import loader, RequestContext
from django.http import HttpResponseRedirect


def home(request):
    template = loader.get_template('home.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))
