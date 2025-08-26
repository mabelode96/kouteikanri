from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'chourikoutei'

urlpatterns = [
    path('', views.top, name='top'),
    path('redirect/', views.redirect_b, name='redirect_b'),
    path('list_all/<str:date>/<str:period>/', views.ListAll.as_view(), name='list_all'),
    path('plot/<str:date>/<str:period>/', views.LineChartsView.as_view(), name='plot'),
    path('results/<str:date>/<str:period>/<select>/', views.JissekiView.as_view(), name='results'),
    path('download/<str:date>/<str:period>/', views.download, name='download'),
    path('<str:line>/<date>/<str:period>/', views.List.as_view(), name='list'),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name='edit'),
    url(r'^start_or_end/(?P<id>\d+)/$', views.start_or_end, name='start_or_end'),
    url(r'^end_none/(?P<id>\d+)/$', views.end_none, name='end_none'),
]
