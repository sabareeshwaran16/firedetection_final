from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Dashboard and features
    path('', views.index, name='dashboard'),
    path('image-detect/', views.image_detect, name='image_detect'),
    path('video-stream/', views.video_stream, name='video_stream'),
    path('video-feed/', views.video_feed, name='video_feed'),
    path('logs/', views.logs_view, name='logs'),
    path('logs/export-pdf/', views.export_logs_pdf, name='export_logs_pdf'),
    path('api/stats/', views.api_stats, name='api_stats'),
]