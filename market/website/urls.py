from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('update/<int:pk>', views.update_item, name='update'),
    path('delete/<int:pk>', views.delete_item, name='delete'),
    path('buy/<int:pk>', views.buy_item, name='buy'),
    path('new/', views.new_item, name='new'),
    path('records/', views.view_records, name='records_page'),
    path('check/<int:pk>', views.check_record, name='check_record'),
    path('image_up/<int:pk>', views.image_upload, name='image_upload'),
    path('image_del/<int:i_id>/<int:img_id>', views.image_delete, name='image_delete'),
]
