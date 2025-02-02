from django.urls import path, include
import rest.views as views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('refresh/', views.AccessTokenRefresh.as_view(), name='refresh-access'),
    path('logout/', views.LogOut.as_view(), name='logout'),
    path('me/', views.User.as_view(), name='me'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),

]
