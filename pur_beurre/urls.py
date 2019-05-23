"""pur_beurre URL Configuration

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
from django.urls import path, include
from favorites import views, views_product

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('legal/', views.legal, name='legal'),

    path('search/', views_product.search, name='search'),
    path('results/<int:product_id>/<query>', views_product.results, name='results'),
    path('detail/<int:product_id>/', views_product.detail_product, name='detail'),

    path('boards/', views_product.board_page, name='boards'),
    path('favorite/<int:board_id>/', views_product.favorites_page, name='favorites'),

    path('new-board/<int:product_id>/', views_product.create_board, name='new_board'),
    path('save/<int:product_id>/<int:board_id>/', views_product.save_product, name='save'),

    path('accounts/', include('accounts.urls')),
]
