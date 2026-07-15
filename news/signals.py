from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model for the News Application.

    Roles:
    - Reader: can view approved articles and newsletters.
    - Journalist: can create articles and newsletters.
    - Editor: can review, approve, edit and delete content.
    """

    READER = "Reader"
    EDITOR = "Editor"
    JOURNALIST = "Journalist"

    ROLE_CHOICES = [
        (READER, "Reader"),
        (EDITOR, "Editor"),
        (JOURNALIST, "Journalist"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=READER,
    )

    subscribed_publishers = models.ManyToManyField(
        "Publisher",
        blank=True,
        related_name="subscribers",
    )

    subscribed_journalists = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="journalist_subscribers",
        limit_choices_to={"role": JOURNALIST},
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


class Publisher(models.Model):
    """
    A publisher can have multiple editors and journalists.
    """

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="editor_publishers",
        limit_choices_to={"role": CustomUser.EDITOR},
    )

    journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="journalist_publishers",
        limit_choices_to={"role": CustomUser.JOURNALIST},
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Articles are written by journalists.

    An article can be independent or linked to a publisher.
    Editors approve articles before readers can view them publicly.
    """

    title = models.CharField(max_length=200)
    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
        limit_choices_to={"role": CustomUser.JOURNALIST},
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.author and self.author.role != CustomUser.JOURNALIST:
            raise ValidationError("Only journalists can author articles.")

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """
    A newsletter is a curated collection of articles.
    Journalists create newsletters.
    Editors and journalists can edit/delete newsletters.
    """

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="newsletters",
        limit_choices_to={"role": CustomUser.JOURNALIST},
    )

    articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name="newsletters",
    )

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.author and self.author.role != CustomUser.JOURNALIST:
            raise ValidationError("Only journalists can author newsletters.")

    def __str__(self):
        return self.title