from django.urls import path
from . import views

urlpatterns = [
    path('', views.org_list_view, name='org_list'),
    path('create/', views.create_organization_view, name='org_create'),
    path('<int:org_id>/', views.org_detail_view, name='org_detail'),
    path('<int:org_id>/invite/', views.invite_user_view, name='org_invite'),
    path('<int:org_id>/leave/', views.org_leave_view, name='org_leave'),
    path('invitations/confirm/<uuid:token>/', views.confirm_invitation_view, name='invite_confirm'),
    path('invitations/decline/<uuid:token>/', views.decline_invitation_view, name='invite_decline'),  # <-- новинка
]
