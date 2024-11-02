from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from .views import (search_courses, get_course_by_id, add_course_schedule, get_all_course_schedules, add_course, get_all_courses, Login,
                    Register, logout, register_course_for_student, get_student_courses, get_courses_with_completed_prerequisites, get_recent_courses)


urlpatterns = [
    path('course_schedule/add/', add_course_schedule,
         name='add_course_schedule'),  # T
    path('course_schedule/all/', get_all_course_schedules,
         name='get_all_course_schedules'),  # T
    path('course/add/', add_course, name='add_course'),  # T
    path('course/all/', get_all_courses, name='get_all_courses'),  # T
    path('course/<int:course_id>/', get_course_by_id,
         name='get_course_by_id'),  # T
    path('register/', Register.as_view(), name='register'),  # T
    path('login/', Login.as_view(), name='login'),  # T
    path('logout/', logout, name='logout'),  # T
    path('search/', search_courses, name='search_courses'),
    path('register_course/', register_course_for_student, name='register_course'),
    path('student/courses/', get_student_courses, name='get_student_courses'),
    path('student/eligible_courses/', get_courses_with_completed_prerequisites,
         name='get_courses_with_completed_prerequisites'),  # T
    path('recent_courses/', get_recent_courses, name='get_recent_courses'),




]
