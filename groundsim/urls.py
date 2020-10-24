"""groundsim URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from groundsim import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # internal
    path('admin/', admin.site.urls),
    path('list/', views.SatelliteListHandler.as_view()),
    path('update/', views.UpdateSatellite.as_view()),
    # mission control
    path('mse_init/', views.InitializeHandler.as_view()),
    path('mse_step/', views.SimulationController.as_view()),
    path('mse_reset/', views.ResetController.as_view()),
    path('mse_save/', views.SaveController.as_view()),
    # path('mse_log/', views.LogListHandler.as_view()),

    # satellite TT&C - locally computed
    # path('location/', views.LocationHandler.as_view()),
    # path('telemetry/', views.TelemetryHandler.as_view()),
    # path('log/', views.LogListHandler.as_view()),
    # path('instruments/', views.InstrumentsListHandler.as_view()),
    # path('get_frame/', views.ImagerFrameHandler.as_view()),
]
