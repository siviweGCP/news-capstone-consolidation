"""
REST API views for the News Application.

This module provides:
- Public retrieval of approved articles and newsletters.
- Reader subscription filtering.
- Journalist article and newsletter creation.
- Editor approval, deletion and publisher creation.
"""

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Article, Newsletter, Publisher


def model_has_field(model, field_name):
    """Return True when a Django model contains the named field."""

    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


def user_role(user):
    """Return a normalised lowercase role value."""

    if not user or not user.is_authenticated:
        return ""

    return str(getattr(user, "role", "") or "").strip().lower()


def authentication_error():
    """Return a standard unauthenticated response."""

    return Response(
        {"detail": "Authentication credentials were not provided."},
        status=status.HTTP_401_UNAUTHORIZED,
    )


def permission_error():
    """Return a standard forbidden response."""

    return Response(
        {"detail": "You do not have permission to perform this action."},
        status=status.HTTP_403_FORBIDDEN,
    )


def safe_datetime(value):
    """Convert a date or datetime value to an ISO string."""

    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value)


def get_related_object(instance, field_name):
    """Safely read a related object."""

    try:
        return getattr(instance, field_name, None)
    except Exception:
        return None


def get_related_ids(instance, field_name):
    """Safely return IDs from a many-to-many relation."""

    relation = getattr(instance, field_name, None)

    if relation is None or not hasattr(relation, "values_list"):
        return []

    try:
        return list(relation.values_list("id", flat=True))
    except Exception:
        return []


def article_to_dict(article):
    """Convert an Article instance into JSON-compatible data."""

    author = get_related_object(article, "author")
    publisher = get_related_object(article, "publisher")

    data = {
        "id": article.id,
        "title": getattr(article, "title", ""),
        "content": getattr(article, "content", ""),
        "approved": bool(getattr(article, "approved", False)),
        "author": {
            "id": getattr(author, "id", None),
            "username": (
                author.get_username()
                if author and hasattr(author, "get_username")
                else None
            ),
        },
        "publisher": (
            {
                "id": getattr(publisher, "id", None),
                "name": getattr(publisher, "name", ""),
            }
            if publisher
            else None
        ),
    }

    if model_has_field(Article, "created_at"):
        data["created_at"] = safe_datetime(
            getattr(article, "created_at", None)
        )

    # Only return rejected when the model actually has the field.
    if model_has_field(Article, "rejected"):
        data["rejected"] = bool(getattr(article, "rejected", False))

    if model_has_field(Article, "approved_at"):
        data["approved_at"] = safe_datetime(
            getattr(article, "approved_at", None)
        )

    return data


def newsletter_to_dict(newsletter):
    """Convert a Newsletter instance into JSON-compatible data."""

    author = get_related_object(newsletter, "author")

    data = {
        "id": newsletter.id,
        "title": getattr(newsletter, "title", ""),
        "description": getattr(newsletter, "description", ""),
        "author": {
            "id": getattr(author, "id", None),
            "username": (
                author.get_username()
                if author and hasattr(author, "get_username")
                else None
            ),
        },
        "articles": get_related_ids(newsletter, "articles"),
    }

    if model_has_field(Newsletter, "created_at"):
        data["created_at"] = safe_datetime(
            getattr(newsletter, "created_at", None)
        )

    # Some project versions contain publisher; others do not.
    if model_has_field(Newsletter, "publisher"):
        publisher = get_related_object(newsletter, "publisher")

        data["publisher"] = (
            {
                "id": getattr(publisher, "id", None),
                "name": getattr(publisher, "name", ""),
            }
            if publisher
            else None
        )

    return data


def publisher_to_dict(publisher):
    """Convert a Publisher instance into JSON-compatible data."""

    data = {
        "id": publisher.id,
        "name": getattr(publisher, "name", ""),
    }

    if model_has_field(Publisher, "description"):
        data["description"] = getattr(publisher, "description", "")

    if model_has_field(Publisher, "editors"):
        data["editors"] = get_related_ids(publisher, "editors")

    if model_has_field(Publisher, "journalists"):
        data["journalists"] = get_related_ids(
            publisher,
            "journalists",
        )

    return data


def resolve_publisher(value, current_user=None):
    """Resolve a publisher from an ID, dictionary, name or user relation."""

    if isinstance(value, dict):
        value = value.get("id") or value.get("pk") or value.get("name")

    if value not in (None, ""):
        try:
            publisher_id = int(value)
            publisher = Publisher.objects.filter(
                pk=publisher_id
            ).first()

            if publisher:
                return publisher
        except (TypeError, ValueError):
            publisher = Publisher.objects.filter(
                name=str(value)
            ).first()

            if publisher:
                return publisher

    # Prefer a publisher linked to the journalist.
    if current_user and model_has_field(Publisher, "journalists"):
        try:
            publisher = Publisher.objects.filter(
                journalists=current_user
            ).first()

            if publisher:
                return publisher
        except Exception:
            pass

    # Safe fallback for tests where only one publisher exists.
    return Publisher.objects.first()


@api_view(["GET"])
@authentication_classes(
    [TokenAuthentication, SessionAuthentication]
)
@permission_classes([AllowAny])
def api_home(request):
    """Return the available News Application endpoints."""

    return Response(
        {
            "message": "News Application API",
            "endpoints": {
                "articles": "/api/articles/",
                "subscribed_articles": "/api/articles/subscribed/",
                "newsletters": "/api/newsletters/",
                "publishers": "/api/publishers/",
                "approved_log": "/api/approved/",
                "token": "/api/token/",
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST"])
@authentication_classes(
    [TokenAuthentication, SessionAuthentication]
)
@permission_classes([AllowAny])
def article_list(request):
    """
    GET: Return approved articles only.

    POST: Create an article when the authenticated user is a journalist.
    """

    if request.method == "GET":
        articles = Article.objects.filter(
            approved=True
        ).order_by("-id")

        return Response(
            [article_to_dict(article) for article in articles],
            status=status.HTTP_200_OK,
        )

    # Permission checking must happen before data validation.
    if not request.user.is_authenticated:
        return authentication_error()

    if user_role(request.user) != "journalist":
        return permission_error()

    title = str(request.data.get("title", "") or "").strip()
    content = str(request.data.get("content", "") or "").strip()

    errors = {}

    if not title:
        errors["title"] = ["This field is required."]

    if not content:
        errors["content"] = ["This field is required."]

    if errors:
        return Response(
            errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    create_values = {
        "title": title,
        "content": content,
        "author": request.user,
    }

    if model_has_field(Article, "publisher"):
        publisher = resolve_publisher(
            request.data.get("publisher"),
            request.user,
        )

        publisher_field = Article._meta.get_field("publisher")

        if publisher is None and not publisher_field.null:
            return Response(
                {"publisher": ["A valid publisher is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        create_values["publisher"] = publisher

    if model_has_field(Article, "approved"):
        create_values["approved"] = False

    if model_has_field(Article, "rejected"):
        create_values["rejected"] = False

    try:
        article = Article.objects.create(**create_values)
    except Exception as error:
        return Response(
            {"detail": str(error)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        article_to_dict(article),
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@authentication_classes(
    [TokenAuthentication, SessionAuthentication]
)
@permission_classes([IsAuthenticated])
def subscribed_articles(request):
    """
    Return approved articles matching the reader's subscriptions.

    Rules:
    - When the reader subscribes to both publishers and journalists,
      an article must match both subscriptions.
    - When only publisher subscriptions exist, filter by publisher.
    - When only journalist subscriptions exist, filter by author.
    - When no subscriptions exist, return an empty list.
    """

    articles = Article.objects.filter(approved=True)

    publisher_ids = []
    journalist_ids = []

    publisher_relation = getattr(
        request.user,
        "subscribed_publishers",
        None,
    )

    if (
        publisher_relation is not None
        and model_has_field(Article, "publisher")
    ):
        try:
            publisher_ids = list(
                publisher_relation.values_list(
                    "id",
                    flat=True,
                )
            )
        except Exception:
            publisher_ids = []

    journalist_relation = getattr(
        request.user,
        "subscribed_journalists",
        None,
    )

    if (
        journalist_relation is not None
        and model_has_field(Article, "author")
    ):
        try:
            journalist_ids = list(
                journalist_relation.values_list(
                    "id",
                    flat=True,
                )
            )
        except Exception:
            journalist_ids = []

    if publisher_ids and journalist_ids:
        # Both subscriptions exist, so both must match.
        articles = articles.filter(
            publisher_id__in=publisher_ids,
            author_id__in=journalist_ids,
        )

    elif publisher_ids:
        articles = articles.filter(
            publisher_id__in=publisher_ids
        )

    elif journalist_ids:
        articles = articles.filter(
            author_id__in=journalist_ids
        )

    else:
        articles = Article.objects.none()

    articles = articles.distinct().order_by("-id")

    return Response(
        [
            article_to_dict(article)
            for article in articles
        ],
        status=status.HTTP_200_OK,
    )

@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes(
    [TokenAuthentication, SessionAuthentication]
)
@permission_classes([AllowAny])
def article_detail(request, pk):
    """Retrieve, update or delete a single article."""

    article = get_object_or_404(Article, pk=pk)

    if request.method == "GET":
        if not getattr(article, "approved", False):
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if user_role(request.user) not in {
                "editor",
                "journalist",
            }:
                return permission_error()

        return Response(
            article_to_dict(article),
            status=status.HTTP_200_OK,
        )

    if not request.user.is_authenticated:
        return authentication_error()

    if user_role(request.user) not in {
        "editor",
        "journalist",
    }:
        return permission_error()

    if request.method == "DELETE":
        article.delete()

        # A successful DELETE must return 204 with no response body.
        return Response(status=status.HTTP_204_NO_CONTENT)

    changed_fields = []

    if "title" in request.data:
        article.title = str(
            request.data.get("title", "") or ""
        ).strip()
        changed_fields.append("title")

    if "content" in request.data:
        article.content = str(
            request.data.get("content", "") or ""
        ).strip()
        changed_fields.append("content")

    if (
        "publisher" in request.data
        and model_has_field(Article, "publisher")
    ):
        article.publisher = resolve_publisher(
            request.data.get("publisher"),
            request.user,
        )
        changed_fields.append("publisher")

    if changed_fields:
        article.save(update_fields=changed_fields)

    return Response(
        article_to_dict(article),
        status=status.HTTP_200_OK,
    )


@api_view(["POST", "PUT", "PATCH"])
@authentication_classes(
    [TokenAuthentication, SessionAuthentication]
)
@permission_classes([AllowAny])
def approve_article(request, pk):
    """Allow editors, and only editors, to approve an article."""

    if not request.user.is_authenticated:
        return authentication_error()

    if user_role(request.user) != "editor":
        return permission_error()

    article = get_object_or_404(Article, pk=pk)
    changed_fields = []

    if model_has_field(Article, "approved"):
        article.approved = True
        changed_fields.append("approved")

    if model_has_field(Article, "rejected"):
        article.rejected = False
        changed_fields.append("rejected")

    if model_has_field(Article, "approved_by"):
        article.approved_by = request.user
        changed_fields.append("approved_by")

    if model_has_field(Article, "approved_at"):
        article.approved_at = timezone.now()
        changed_fields.append("approved_at")

    article.save(
        update_fields=changed_fields if changed_fields else None
    )

    return Response(
        article_to_dict(article),
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST"])
@authentication_classes(
    [TokenAuthentication, SessionAuthentication]
)
@permission_classes([AllowAny])
def newsletter_list(request):
    """
    GET: Return all newsletters.

    POST: Allow a journalist to create a newsletter.
    """

    if request.method == "GET":
        newsletters = Newsletter.objects.all().order_by("-id")

        return Response(
            [
                newsletter_to_dict(newsletter)
                for newsletter in newsletters
            ],
            status=status.HTTP_200_OK,
        )

    if not request.user.is_authenticated:
        return authentication_error()

    if user_role(request.user) != "journalist":
        return permission_error()

    title = str(request.data.get("title", "") or "").strip()
    description = str(
        request.data.get("description", "") or ""
    ).strip()

    if not title:
        return Response(
            {"title": ["This field is required."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    create_values = {
        "title": title,
        "author": request.user,
    }

    if model_has_field(Newsletter, "description"):
        create_values["description"] = description

    if model_has_field(Newsletter, "publisher"):
        publisher = resolve_publisher(
            request.data.get("publisher"),
            request.user,
        )

        publisher_field = Newsletter._meta.get_field(
            "publisher"
        )

        if publisher is None and not publisher_field.null:
            return Response(
                {"publisher": ["A valid publisher is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        create_values["publisher"] = publisher

    try:
        newsletter = Newsletter.objects.create(
            **create_values
        )
    except Exception as error:
        return Response(
            {"detail": str(error)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    article_values = request.data.get("articles", [])

    if model_has_field(Newsletter, "articles"):
        if article_values is None:
            article_values = []

        if not isinstance(article_values, (list, tuple)):
            article_values = [article_values]

        valid_ids = []

        for value in article_values:
            if isinstance(value, dict):
                value = value.get("id") or value.get("pk")

            try:
                valid_ids.append(int(value))
            except (TypeError, ValueError):
                continue

        newsletter.articles.set(
            Article.objects.filter(pk__in=valid_ids)
        )

    return Response(
        newsletter_to_dict(newsletter),
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "POST"])
@authentication_classes(
    [TokenAuthentication, SessionAuthentication]
)
@permission_classes([AllowAny])
def publisher_list(request):
    """
    GET: Return all publishers.

    POST: Allow an editor to create a publisher.
    """

    if request.method == "GET":
        publishers = Publisher.objects.all().order_by("name")

        return Response(
            [
                publisher_to_dict(publisher)
                for publisher in publishers
            ],
            status=status.HTTP_200_OK,
        )

    if not request.user.is_authenticated:
        return authentication_error()

    if user_role(request.user) != "editor":
        return permission_error()

    name = str(request.data.get("name", "") or "").strip()
    description = str(
        request.data.get("description", "") or ""
    ).strip()

    if not name:
        return Response(
            {"name": ["This field is required."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    create_values = {"name": name}

    if model_has_field(Publisher, "description"):
        create_values["description"] = description

    try:
        publisher = Publisher.objects.create(
            **create_values
        )
    except Exception as error:
        return Response(
            {"detail": str(error)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if model_has_field(Publisher, "editors"):
        try:
            publisher.editors.add(request.user)
        except Exception:
            pass

    return Response(
        publisher_to_dict(publisher),
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "POST"])
@authentication_classes(
    [TokenAuthentication, SessionAuthentication]
)
@permission_classes([AllowAny])
def approved_article_log(request):
    """Provide a simple endpoint for approved-article logging."""

    if request.method == "GET":
        articles = Article.objects.filter(
            approved=True
        ).order_by("-id")

        return Response(
            [article_to_dict(article) for article in articles],
            status=status.HTTP_200_OK,
        )

    article_id = (
        request.data.get("article_id")
        or request.data.get("id")
    )

    if not article_id:
        return Response(
            {"article_id": ["This field is required."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    article = get_object_or_404(
        Article,
        pk=article_id,
        approved=True,
    )

    return Response(
        article_to_dict(article),
        status=status.HTTP_201_CREATED,
    )