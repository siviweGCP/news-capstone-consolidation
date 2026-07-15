"""URL routes for the News Application REST API."""

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import api_views


app_name = "news_api"


urlpatterns = [
    path("", api_views.api_home, name="home"),

    path(
        "articles/",
        api_views.article_list,
        name="article-list",
    ),

    path(
        "articles/subscribed/",
        api_views.subscribed_articles,
        name="subscribed-articles",
    ),

    path(
        "articles/<int:pk>/approve/",
        api_views.approve_article,
        name="approve-article",
    ),

    path(
        "articles/<int:pk>/",
        api_views.article_detail,
        name="article-detail",
    ),

    path(
        "newsletters/",
        api_views.newsletter_list,
        name="newsletter-list",
    ),

    path(
        "publishers/",
        api_views.publisher_list,
        name="publisher-list",
    ),

    path(
        "approved/",
        api_views.approved_article_log,
        name="approved-article-log",
    ),

    path(
        "token/",
        obtain_auth_token,
        name="token",
    ),

    path(
        "login/",
        obtain_auth_token,
        name="login",
    ),
]