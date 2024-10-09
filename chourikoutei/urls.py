from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'chourikoutei'

urlpatterns = [
    path('', views.top, name='top'),
    path('list_all/', views.list_all, name='list_all'),
    path("plot/<date>/<str:period>/", views.LineChartsView.as_view(), name="plot"),
    path('<str:line>/<date>/<str:period>/', views.List.as_view(), name='list'),
]
