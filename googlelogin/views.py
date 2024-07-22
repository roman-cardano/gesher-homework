from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class GoogleLoginView(LoginRequiredMixin, TemplateView, ):
    template_name = 'googlelogin/home.html'
