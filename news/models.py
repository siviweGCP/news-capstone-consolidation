"""Database models for users, publishers, articles, newsletters, and subscriptions."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    editors = models.ManyToManyField(
        "CustomUser",
        blank=True,
        related_name="publisher_editor_roles"
    )

    journalists = models.ManyToManyField(
        "CustomUser",
        blank=True,
        related_name="publisher_journalist_roles"
    )

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    READER = "reader"
    EDITOR = "editor"
    JOURNALIST = "journalist"

    ROLE_CHOICES = (
        (READER, "Reader"),
        (EDITOR, "Editor"),
        (JOURNALIST, "Journalist"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=READER
    )

    subscribed_publishers = models.ManyToManyField(
        Publisher,
        blank=True,
        related_name="subscribed_readers"
    )

    subscribed_journalists = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="journalist_subscribers"
    )

    def __str__(self):
        return self.username


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="articles"
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="articles",
        null=True,
        blank=True
    )

    approved = models.BooleanField(default=False)

    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_articles"
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def approve(self, editor):
        self.approved = True
        self.approved_by = editor
        self.save()

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="newsletters"
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="newsletters",
        null=True,
        blank=True
    )

    articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name="newsletters"
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Subscription(models.Model):
    reader = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("reader", "publisher")

    def __str__(self):
        return f"{self.reader.username} subscribed to {self.publisher.name}"