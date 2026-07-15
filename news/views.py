"""Web and API views for registration, publishing, approval, and subscriptions."""

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomUserRegistrationForm
from .models import Article, Newsletter, Publisher


def home(request):
    articles = Article.objects.filter(approved=True).order_by("-created_at")
    publishers = Publisher.objects.all().order_by("name")
    newsletters = Newsletter.objects.all().order_by("-created_at")

    context = {
        "articles": articles,
        "publishers": publishers,
        "newsletters": newsletters,
    }

    return render(request, "news/home.html", context)


def register(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("home")

        messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserRegistrationForm()

    return render(request, "news/register.html", {"form": form})


def article_list(request):
    articles = Article.objects.all().order_by("-created_at")

    context = {
        "articles": articles,
    }

    return render(request, "news/article_list.html", context)


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)

    context = {
        "article": article,
    }

    return render(request, "news/article_detail.html", context)


def article_review(request):
    # Your Article model does NOT have a rejected field.
    # Pending review means approved is False.
    pending_articles = Article.objects.filter(
        approved=False
    ).order_by("-created_at")

    context = {
        "articles": pending_articles,
    }

    return render(request, "news/article_review.html", context)


def publisher_list(request):
    publishers = Publisher.objects.all().order_by("name")

    context = {
        "publishers": publishers,
    }

    return render(request, "news/publisher_list.html", context)


def newsletter_list(request):
    newsletters = Newsletter.objects.all().order_by("-created_at")

    context = {
        "newsletters": newsletters,
    }

    return render(request, "news/newsletter_list.html", context)