from django.conf.urls import include, url
from django.conf.urls.static import static
from . import views
import mailapp
app_name='mailapp'
urlpatterns = [
     url(r'^/',mailapp.views.index, name = 'index'),
]