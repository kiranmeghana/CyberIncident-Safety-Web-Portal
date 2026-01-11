from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # The JSON endpoint used by both mini-bot and full-bot
    path('query/', views.chatbot_query, name='chatbot_query'),
    
    # The dedicated page for the AI Analysis Bot from Resources
    path('full/', views.full_chat_view, name='full_chat'),
    
    path('full-analysis/', views.full_chat_view, name='full_chat'),
]