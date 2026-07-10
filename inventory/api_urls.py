from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'categorias', api.CategoryViewSet, basename='api-category')
router.register(r'productos', api.ProductViewSet, basename='api-product')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]
