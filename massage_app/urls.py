from django.urls import path
from . import views

app_name = 'massage_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('book-now/', views.booknow, name='booknow'),
    path('login/', views.login_view, name='login'),
]
