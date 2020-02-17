from django.urls import path

from . import views

app_name = "arxiv"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('count/', views.article_count, name='article_count'),
    path('article/<int:pk>/', views.ArticleView.as_view(), name='article'),
    path('author/<int:pk>/', views.AuthorView.as_view(), name='author'),
]
