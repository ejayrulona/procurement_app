"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls", namespace="core")),
    path("activity_logs/", include("apps.activity_logs.urls", namespace="activity_logs")),
    path("inventory/", include("apps.inventory.urls", namespace="inventory")),
    path("users/", include("apps.users.urls", namespace="users")),
    path("notification/", include("apps.notification.urls", namespace="notification")),
    path("ppmp/", include("apps.ppmp.urls", namespace="ppmp")),
    path("app/", include("apps.app.urls", namespace="app")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)