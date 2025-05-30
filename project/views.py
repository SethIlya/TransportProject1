from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from project.models import Project
from django.views.generic import TemplateView

class ShowProjectView(TemplateView):
    template_name = "show_project.html"

    def get_context_data(self, **kwargs: any) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.all()

        return context
    