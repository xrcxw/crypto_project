from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('update/', views.update_data, name='update_data'),
    path('coin/<int:coin_id>/', views.coin_detail, name='coin_detail'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('add-to-watchlist/<int:coin_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove-from-watchlist/<int:coin_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('signup/', views.signup, name='signup'),
]