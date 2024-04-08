from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

admin.site.site_header = "Fashion Store"
admin.site.site_title = "WebServer"
admin.site.index_title = " "

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),  # Đây là URL pattern của ứng dụng của bạn
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
