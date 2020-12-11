from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'kouteikanri'

urlpatterns = [
    path('', views.top, name='top'),
    path('<str:line>/<date>/<str:period>/#<int:anchor>', views.KouteiList.as_view(), name='list'),
    path('<str:line>/<date>/<str:period>/', views.KouteiList.as_view(), name='list'),
    url(r'^add/$', views.edit, name='add'),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name='edit'),
    url(r'^delete/(?P<id>\d+)/$', views.delete, name='delete'),
    url(r'^start_or_end/(?P<id>\d+)/$', views.start_or_end, name='start_or_end'),
    url(r'^end_none/(?P<id>\d+)/$', views.end_none, name='end_none'),
]
