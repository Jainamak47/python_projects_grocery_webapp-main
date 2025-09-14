from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('', include('grocery_app.urls')),  
]
