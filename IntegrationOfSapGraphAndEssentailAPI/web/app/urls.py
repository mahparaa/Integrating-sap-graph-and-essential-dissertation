from . import views
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('/', views.index),
    path('sap-graph', views.sap_graph),
    path('login/sap', views.login_sap),
    path('sap/callback', views.sap_login_callback),
    path('essential-architecture', views.essentail_architecture)
]