from django.urls import path
from .views import offers_list, change_status

urlpatterns = [
    path('offers/', offers_list, name='offers_list'),
    path('change-status/<int:offer_id>/<str:new_status>/', change_status, name='change_status'),
]