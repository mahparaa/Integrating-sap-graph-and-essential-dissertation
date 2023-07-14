from . import views
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('/', views.index),
    path('sap-graph', views.sap_graph),
    path('login/sap', views.login_sap),
    path('logout/sap', views.sap_logout_remove_cookies),
    path('sap/callback', views.sap_login_callback),
    path('sap/download', views.sap_sync_all_the_entites),
    path('sap/network', views.load_sap_graph_nodes_and_edges),
    path('sap/neo4j', views.sync_to_neo4j),
    path('sap/neo4j/search', views.search_from_neo4j),
    path('essential-architecture', views.essentail_architecture),
    path('ea/login', views.login_to_ea),
    path('ea/login/handle', views.handle_login_to_ea),
    path('ea/create/information/concepts', views.create_information_concepts),
    path('ea/apply/armining', views.handle_ar_mining)
]