from django.shortcuts import render
# from django.views.generic import (
#     View
# )
from django.views import View

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')

class AboutView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'about.html')
