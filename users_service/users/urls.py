from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('user/current-user/', views.CurrentUserView.as_view(), name='current-user'),
    path('user/list/', views.UserListView.as_view(), name='list-user'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='details-user'),
    path('user/<str:role>/', views.UserRoleView.as_view(), name='role-user'),
    path('user/update/<int:id>/', views.UpdateUserView.as_view(), name='update-user'),
    path('user/delete/<int:pk>/', views.DeleteUserView.as_view(), name='user-delete'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
