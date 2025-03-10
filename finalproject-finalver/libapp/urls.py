
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.borrow_book, name='borrow_book'),  
    path('view_books/', views.view_books, name='view_books'),
    path('return_book/', views.return_book, name='return_book'),
    path('confirm_return/<str:accession_number>/', views.confirm_return, name='confirm_return'),
]




