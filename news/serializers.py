"""
Django REST Framework serializers.
"""

from rest_framework import serializers

from .models import (
    ApprovedArticleLog,
    Article,
    CustomUser,
    Newsletter,
    Publisher,
)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser.
    """

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role"]


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for Publisher.
    """

    class Meta:
        model = Publisher
        fields = ["id", "name", "description"]


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for Article.
    """

    author = UserSerializer(read_only=True)
    publisher_detail = PublisherSerializer(source="publisher", read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "created_at",
            "approved",
            "publisher",
            "publisher_detail",
        ]
        read_only_fields = ["author", "created_at", "approved"]

    def create(self, validated_data):
        """
        Automatically set article author to the logged-in user.
        """
        request = self.context["request"]
        return Article.objects.create(author=request.user, **validated_data)


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for Newsletter.
    """

    author = UserSerializer(read_only=True)
    articles = ArticleSerializer(many=True, read_only=True)
    article_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Article.objects.all(),
        source="articles",
        write_only=True,
        required=False,
    )

    class Meta:
        model = Newsletter
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "author",
            "articles",
            "article_ids",
        ]
        read_only_fields = ["author", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        articles = validated_data.pop("articles", [])
        newsletter = Newsletter.objects.create(
            author=request.user,
            **validated_data,
        )
        newsletter.articles.set(articles)
        return newsletter


class ApprovedArticleLogSerializer(serializers.ModelSerializer):
    """
    Serializer for approved article log endpoint.
    """

    class Meta:
        model = ApprovedArticleLog
        fields = [
            "id",
            "article",
            "title",
            "author_username",
            "publisher_name",
            "logged_at",
        ]
        read_only_fields = ["logged_at"]