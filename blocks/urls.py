"""
blocks URL Configuration
"""

from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('<int:block_height>/', views.block, name='block')
]