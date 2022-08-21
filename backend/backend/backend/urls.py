
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url

app_name = "backend"

urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),

]

schema_view = get_schema_view(
   openapi.Info(
      title="FoodGram API",
      default_version='v1',
      description="Документация для API проекта FoodGram",
      contact=openapi.Contact(email="kirsan94@yandex.ru"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
   url(r'^swagger(?P<format>\.json|\.yaml)$',
       schema_view.without_ui(cache_timeout=0), name='schema-json'),
   url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
       name='schema-swagger-ui'),
   url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
       name='schema-redoc'),
]
