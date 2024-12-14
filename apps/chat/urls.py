from django.urls import path
from . import views
from . import utils

app_name = 'chat'


urlpatterns = [
    path('', views.home, name='home'),
    path('conversation-list', views.conversation_list, name='conversation_list'),
    path('c/<slug:slug>/', views.conversation_detail, name='conversation_detail'),
    path('create_conversation/', views.create_conversation, name='create_conversation'),
    path('get_conversation_title/<slug:slug>/', views.get_conversation_title, name='get_conversation_title'),

    path('c/<slug:slug>/star/', utils.star_conversation, name='star_conversation'),
    path('c/<slug:slug>/rename/', utils.rename_conversation, name='rename_conversation'),
    path('c/<slug:slug>/delete/', utils.delete_conversation, name='delete_conversation'),
]
