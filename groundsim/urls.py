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
from groundsim.nova import views as nova_views
from groundsim.mse import views as mse_views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # internal
    path('admin/', admin.site.urls),
    path('list/', mse_views.SatelliteListHandler.as_view()),
    path('update/', mse_views.UpdateSatellite.as_view()),

    # MSE (Tier 2) API mission selection
    path('mse_mission_list', mse_views.ListMissions.as_view()),
    path('mse_mission_details', mse_views.GetMissionDetails.as_view()),
    path('mse_init/', mse_views.InitializeHandler.as_view()),
    path('mse_step/', mse_views.SimulationController.as_view()),
    path('mse_reset/', mse_views.ResetController.as_view()),
    path('mse_save/', mse_views.SaveController.as_view()),
    path('mse_action/', mse_views.ActionController.as_view()),

    # webNOVA (Tier 1) API
    path('nova/instruments/', nova_views.NovaInstrumentListController.as_view()),
    path('nova/times_on_target/', nova_views.NovaSchedulerController.as_view()),
    path('nova/image_schedule/', nova_views.NovaImagerController.as_view()),
    path('nova/image_download/', nova_views.NovaDownloadController.as_view()),
]
