# myapp/middleware.py
from django.http import HttpResponseRedirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login_pages = [reverse('student_login'), reverse('staff_login'), reverse('admin_login'), reverse('base_page')]
        if not request.user.is_authenticated and request.path not in login_pages:
            return HttpResponseRedirect(reverse('base_page'))
        return self.get_response(request)