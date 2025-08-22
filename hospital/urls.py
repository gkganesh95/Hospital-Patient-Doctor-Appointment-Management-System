from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_patient, name='register_patient'),
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<int:pk>/edit/', views.edit_appointment, name='edit_appointment'),
    path('appointments/<int:pk>/delete/', views.delete_appointment, name='delete_appointment'),
    path('appointments/<int:pk>/status/', views.update_status, name='update_status'),
]
