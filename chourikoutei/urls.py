from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'chourikoutei'

urlpatterns = [
    path('', views.top, name='top'),
    path('redirect/', views.redirect_b, name='redirect_b'),
    path('list_all/<str:date>/<str:period>/', views.ListAll.as_view(), name='list_all'),
    path('plot/<str:date>/<str:period>/', views.LineChartsView.as_view(), name='plot'),
    path('<str:line>/<date>/<str:period>/', views.List.as_view(), name='list'),
]
