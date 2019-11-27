from django.conf.urls import include, url
from django.conf.urls.static import static
from mailapp import views
# import mailapp
app_name='mailapp'
urlpatterns = [
     # url(r'^home/',views.home, name = 'home'),
     url(r'^home/$',views.index, name = 'index'),
     url(r'savedata/',views.savedata, name = 'savedata'),
     url(r'^register/$',views.register,name='register'),
     url(r'^user_login/$',views.user_login,name='user_login'),
     url(r'^getparams/$', views.getparams, name = 'getparams')
]