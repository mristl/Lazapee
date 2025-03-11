from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.employees, name='employees'),
    path('payslip', views.create_payslip, name='create_payslip'),
    path('delete_payslip/<int:pk>/', views.delete_payslip, name='delete_payslip'),
    path('payslip', views.payslip, name='payslip'),
    path('view_payslip_detail/<int:pk>/', views.view_payslip_detail, name='view_payslip_detail'),
    path('create_employee', views.create_employee, name='create_employee'),
    path('delete_employee/<int:pk>/', views.delete_employee, name='delete_employee'),
    path('update_employee/<int:pk>/', views.update_employee, name='update_employee'),
    path('add_overtime/<int:pk>/', views.add_overtime, name='add_overtime'),
    path('reset_overtime/<int:pk>/', views.reset_overtime, name='reset_overtime'),
]
