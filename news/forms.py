from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Article, Newsletter, Publisher, Subscription


User = get_user_model()


def model_has_field(model, field_name):
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False


def existing_fields(model, possible_fields):
    valid_fields = []

    for field_name in possible_fields:
        if model_has_field(model, field_name):
            valid_fields.append(field_name)

    return valid_fields


class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email address")

    class Meta:
        model = User
        fields = existing_fields(User, ["username", "email", "role"]) + [
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        if "email" in self.cleaned_data:
            user.email = self.cleaned_data["email"]

        if "role" in self.cleaned_data:
            user.role = self.cleaned_data["role"]

        if commit:
            user.save()

        return user


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = existing_fields(
            Article,
            [
                "title",
                "content",
                "publisher",
            ],
        )


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = existing_fields(
            Publisher,
            [
                "name",
                "description",
                "editors",
                "journalists",
            ],
        )


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = existing_fields(
            Newsletter,
            [
                "title",
                "description",
                "articles",
            ],
        )


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = existing_fields(
            Subscription,
            [
                "publisher",
            ],
        )


RegisterForm = CustomUserRegistrationForm
RegistrationForm = CustomUserRegistrationForm
UserRegisterForm = CustomUserRegistrationForm
CustomUserCreationForm = CustomUserRegistrationForm
