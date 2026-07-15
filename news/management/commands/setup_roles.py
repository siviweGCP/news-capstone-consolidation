"""
Management command to create user role groups and permissions.

Run with:
python manage.py setup_roles
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from news.models import Article, Newsletter, Publisher


class Command(BaseCommand):
    help = "Create Reader, Editor, and Journalist groups with permissions."

    def handle(self, *args, **options):
        reader_group, _ = Group.objects.get_or_create(name="Reader")
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        journalist_group, _ = Group.objects.get_or_create(name="Journalist")

        article_content_type = ContentType.objects.get_for_model(Article)
        newsletter_content_type = ContentType.objects.get_for_model(Newsletter)
        publisher_content_type = ContentType.objects.get_for_model(Publisher)

        article_permissions = Permission.objects.filter(
            content_type=article_content_type
        )
        newsletter_permissions = Permission.objects.filter(
            content_type=newsletter_content_type
        )
        publisher_permissions = Permission.objects.filter(
            content_type=publisher_content_type
        )

        view_article = article_permissions.get(codename="view_article")
        add_article = article_permissions.get(codename="add_article")
        change_article = article_permissions.get(codename="change_article")
        delete_article = article_permissions.get(codename="delete_article")

        view_newsletter = newsletter_permissions.get(codename="view_newsletter")
        add_newsletter = newsletter_permissions.get(codename="add_newsletter")
        change_newsletter = newsletter_permissions.get(codename="change_newsletter")
        delete_newsletter = newsletter_permissions.get(codename="delete_newsletter")

        view_publisher = publisher_permissions.get(codename="view_publisher")

        reader_group.permissions.set([
            view_article,
            view_newsletter,
            view_publisher,
        ])

        editor_group.permissions.set([
            view_article,
            change_article,
            delete_article,
            view_newsletter,
            change_newsletter,
            delete_newsletter,
            view_publisher,
        ])

        journalist_group.permissions.set([
            add_article,
            view_article,
            change_article,
            delete_article,
            add_newsletter,
            view_newsletter,
            change_newsletter,
            delete_newsletter,
            view_publisher,
        ])

        self.stdout.write(
            self.style.SUCCESS("Role groups and permissions created.")
        )