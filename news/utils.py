"""
Utility functions for approval emails and API logging.
"""

import requests

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from .models import CustomUser


def get_article_subscriber_emails(article):
    """
    Return emails of readers who subscribed to the article publisher
    or article journalist.
    """
    subscriber_emails = set()

    if article.publisher:
        publisher_subscribers = CustomUser.objects.filter(
            role=CustomUser.READER,
            subscriptions_to_publishers=article.publisher,
        )

        for subscriber in publisher_subscribers:
            if subscriber.email:
                subscriber_emails.add(subscriber.email)

    journalist_subscribers = CustomUser.objects.filter(
        role=CustomUser.READER,
        subscriptions_to_journalists=article.author,
    )

    for subscriber in journalist_subscribers:
        if subscriber.email:
            subscriber_emails.add(subscriber.email)

    return list(subscriber_emails)


def email_approved_article(article):
    """
    Email approved article content to subscribers.
    During development, the email prints in the terminal.
    """
    recipient_list = get_article_subscriber_emails(article)

    if not recipient_list:
        return 0

    subject = f"New approved article: {article.title}"

    message = (
        f"Title: {article.title}\n\n"
        f"Author: {article.author.username}\n\n"
        f"Publisher: {article.publisher.name if article.publisher else 'Independent'}\n\n"
        f"{article.content}"
    )

    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )


def post_approved_article_to_api(request, article):
    """
    Post approved article data to the project's own REST API endpoint.

    This simulates sharing the approved article externally.
    """
    api_url = request.build_absolute_uri(reverse("approved-log-api"))

    payload = {
        "article": article.id,
        "title": article.title,
        "author_username": article.author.username,
        "publisher_name": article.publisher.name if article.publisher else "",
    }

    response = requests.post(api_url, json=payload, timeout=5)
    response.raise_for_status()

    return response