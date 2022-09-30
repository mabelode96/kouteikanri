from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'kouteikanri'

urlpatterns = [
    path('', views.top, name='top'),
    path('all/', views.all_list, name='all'),
    path('set_all/', views.set_all, name='set_all'),
    path('<str:line>/<date>/<str:period>/#<int:anchor>', views.KouteiList.as_view(), name='list'),
    path('<str:line>/<date>/<str:period>/', views.KouteiList.as_view(), name='list'),
    path('set/<str:line>/<date>/<str:period>/', views.SetList.as_view(), name='set_list'),
    url(r'^add/$', views.edit, name='add'),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name='edit'),
    url(r'^copy/(?P<id>\d+)/$', views.copy, name='copy'),
    url(r'^comment/(?P<id>\d+)/$', views.comment, name='comment'),
    url(r'^delete/(?P<id>\d+)/$', views.delete, name='delete'),
    url(r'^start_or_end/(?P<id>\d+)/$', views.start_or_end, name='start_or_end'),
    path('start_cancel/<str:line>/<date>/<str:period>/', views.start_cancel, name='start_cancel'),
    url(r'^end_none/(?P<id>\d+)/$', views.end_none, name='end_none'),
    url(r'^set_comp/(?P<id>\d+)/$', views.set_comp, name='set_comp'),
    path('reset_all/<str:line>/<date>/<str:period>/', views.reset_all, name='reset_all'),
    path('upload/', views.upload, name='upload'),
    path('blank.html', views.blank, name='blank'),
]
