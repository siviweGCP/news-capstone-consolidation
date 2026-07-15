from django.conf import settings
from django.core.mail import send_mail


def get_user_role(user):
    if not user or not user.is_authenticated:
        return ""

    return str(getattr(user, "role", "")).lower()


def is_editor(user):
    return user.is_authenticated and get_user_role(user) == "editor"


def is_journalist(user):
    return user.is_authenticated and get_user_role(user) == "journalist"


def is_reader(user):
    return user.is_authenticated and get_user_role(user) == "reader"


def is_admin(user):
    return user.is_authenticated and user.is_superuser


def user_can_manage_publisher(user, publisher):
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if is_editor(user):
        try:
            return publisher.editors.filter(id=user.id).exists()
        except Exception:
            return False

    return False


def user_can_write_for_publisher(user, publisher):
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    try:
        if is_journalist(user) and publisher.journalists.filter(id=user.id).exists():
            return True

        if is_editor(user) and publisher.editors.filter(id=user.id).exists():
            return True
    except Exception:
        return False

    return False


def get_publisher_subscriber_emails(publisher):
    emails = []

    if publisher is None:
        return emails

    try:
        subscriptions = publisher.subscriptions.select_related("user").all()

        for subscription in subscriptions:
            email = getattr(subscription.user, "email", "")

            if email:
                emails.append(email)

    except Exception:
        try:
            from .models import Subscription

            subscriptions = Subscription.objects.filter(
                publisher=publisher
            ).select_related("user")

            for subscription in subscriptions:
                email = getattr(subscription.user, "email", "")

                if email:
                    emails.append(email)

        except Exception:
            emails = []

    return list(set(emails))


def email_approved_article_to_subscribers(article):
    publisher = getattr(article, "publisher", None)

    if publisher is None:
        return 0

    recipient_emails = get_publisher_subscriber_emails(publisher)

    if not recipient_emails:
        return 0

    subject = f"New approved article: {article.title}"

    message = f"""
A new article has been approved and published.

Title: {article.title}
Publisher: {publisher.name}

{article.content}
"""

    send_mail(
        subject,
        message,
        getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        recipient_emails,
        fail_silently=True,
    )

    return len(recipient_emails)


def email_newsletter_to_subscribers(newsletter):
    recipient_emails = []

    try:
        articles = newsletter.articles.all()

        for article in articles:
            publisher = getattr(article, "publisher", None)
            recipient_emails.extend(get_publisher_subscriber_emails(publisher))

    except Exception:
        recipient_emails = []

    recipient_emails = list(set(recipient_emails))

    if not recipient_emails:
        return 0

    subject = f"Newsletter: {newsletter.title}"

    message = f"""
A new newsletter has been published.

Title: {newsletter.title}

{newsletter.description}
"""

    send_mail(
        subject,
        message,
        getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        recipient_emails,
        fail_silently=True,
    )

    return len(recipient_emails)


def post_approved_article_to_api(article):
    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "author": article.author.username if article.author else "",
        "publisher": article.publisher.name if article.publisher else "",
        "approved": article.approved,
        "created_at": article.created_at,
    }


def notify_subscribers(article):
    return email_approved_article_to_subscribers(article)


def send_article_email_to_subscribers(article):
    return email_approved_article_to_subscribers(article)


def send_approved_article_email(article):
    return email_approved_article_to_subscribers(article)


def send_newsletter_to_subscribers(newsletter):
    return email_newsletter_to_subscribers(newsletter)


def email_newsletter_to_all_subscribers(newsletter):
    return email_newsletter_to_subscribers(newsletter)


def can_approve_article(user, article):
    publisher = getattr(article, "publisher", None)
    return user_can_manage_publisher(user, publisher)


def can_edit_article(user, article):
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if getattr(article, "author_id", None) == user.id:
        return True

    return False


def can_delete_article(user, article):
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if is_editor(user):
        return True

    if getattr(article, "author_id", None) == user.id:
        return True

    return False


def can_create_publisher(user):
    if not user or not user.is_authenticated:
        return False

    return user.is_superuser or is_editor(user)


def can_create_article(user):
    if not user or not user.is_authenticated:
        return False

    return user.is_superuser or is_journalist(user)


def can_create_newsletter(user):
    if not user or not user.is_authenticated:
        return False

    return user.is_superuser or is_editor(user) or is_journalist(user)


def approve_article_and_notify(article):
    article.approved = True
    article.save()

    email_approved_article_to_subscribers(article)
    post_approved_article_to_api(article)

    return article


def approve_article_service(article):
    return approve_article_and_notify(article)


def publish_article(article):
    return approve_article_and_notify(article)