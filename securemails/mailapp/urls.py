from django.conf.urls import include, url
from django.conf.urls.static import static
from mailapp import views
# import mailapp
app_name='mailapp'
urlpatterns = [
     url(r'^$',views.index, name = 'index'),
     url(r'savedata/',views.savedata, name = 'savedata'),
     url(r'^getparams/$', views.getparams, name = 'getparams')
]