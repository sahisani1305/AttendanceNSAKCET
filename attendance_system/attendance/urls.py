from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.base_page, name='base_page'),
    path('home/', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('attendance/', views.attendance, name='attendance'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('view_attendance/<int:year>/<int:semester>/<str:class_name>/<str:section>/', views.view_attendance, name='view_attendance'),
    path('get_sections/<str:class_name>/', views.get_sections, name='get_sections'),
    path('student_login/', views.student_login, name='student_login'),
    path('staff_login/', views.staff_login, name='staff_login'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('student_home/', views.student_home, name='student_home'),
    path('attendance_home/', views.attendance_home, name='attendance_home'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('register_student/', views.register_student, name='register_student'),
    path('register_staff/', views.register_staff, name='register_staff'),
    path('get_subjects/<str:class_name>/<int:year>/<int:semester>/', views.get_subjects, name='get_subjects'),
    path('logout/', LogoutView.as_view(next_page='base_page'), name='logout'),
    path('admin_view_attendance/<int:year>/<int:semester>/<str:class_name>/<str:section>/', views.admin_view_attendance, name='admin_view_attendance'),
    path('view_summary/<int:year>/<int:semester>/<str:class_name>/<str:section>/', views.view_summary, name='view_summary'),
    path('admin_view_summary/<int:year>/<int:semester>/<str:class_name>/<str:section>/', views.admin_view_summary, name='admin_view_summary'),

]
