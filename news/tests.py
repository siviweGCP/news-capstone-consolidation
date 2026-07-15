from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Article, Newsletter, Publisher


User = get_user_model()


class NewsApplicationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.reader = User.objects.create_user(
            username="reader1",
            email="reader1@example.com",
            password="Password123",
            role="Reader",
        )

        self.journalist = User.objects.create_user(
            username="journalist1",
            email="journalist1@example.com",
            password="Password123",
            role="Journalist",
        )

        self.editor = User.objects.create_user(
            username="editor1",
            email="editor1@example.com",
            password="Password123",
            role="Editor",
        )

        self.publisher = Publisher.objects.create(
            name="Test Publisher",
            description="A test publisher",
        )

        self.reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.journalist)

        self.approved_article = Article.objects.create(
            title="Approved Article",
            content="This article is approved.",
            author=self.journalist,
            publisher=self.publisher,
            approved=True,
        )

        self.pending_article = Article.objects.create(
            title="Pending Article",
            content="This article is waiting for approval.",
            author=self.journalist,
            publisher=self.publisher,
            approved=False,
        )

        self.other_publisher = Publisher.objects.create(
            name="Other Publisher",
            description="Another publisher",
        )

        self.unsubscribed_article = Article.objects.create(
            title="Unsubscribed Article",
            content="Reader should not receive this through subscribed endpoint.",
            author=self.journalist,
            publisher=self.other_publisher,
            approved=True,
        )

        self.newsletter = Newsletter.objects.create(
            title="Weekly Newsletter",
            description="Test newsletter",
            author=self.journalist,
        )
        self.newsletter.articles.add(self.approved_article)

        self.reader_token = Token.objects.create(user=self.reader)
        self.journalist_token = Token.objects.create(user=self.journalist)
        self.editor_token = Token.objects.create(user=self.editor)

    def authenticate_as_reader(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.reader_token.key}"
        )

    def authenticate_as_journalist(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.journalist_token.key}"
        )

    def authenticate_as_editor(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.editor_token.key}"
        )

    def test_api_returns_only_approved_articles(self):
        response = self.client.get("/api/articles/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Approved Article")
        self.assertContains(response, "Unsubscribed Article")
        self.assertNotContains(response, "Pending Article")

    def test_reader_gets_only_subscribed_articles(self):
        self.authenticate_as_reader()

        response = self.client.get("/api/articles/subscribed/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Approved Article")
        self.assertNotContains(response, "Unsubscribed Article")
        self.assertNotContains(response, "Pending Article")

    def test_reader_cannot_create_article(self):
        self.authenticate_as_reader()

        response = self.client.post(
            "/api/articles/",
            {
                "title": "Reader Article",
                "content": "Reader should not create this.",
                "publisher": self.publisher.id,
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_journalist_can_create_article(self):
        self.authenticate_as_journalist()

        response = self.client.post(
            "/api/articles/",
            {
                "title": "Journalist Article",
                "content": "Journalist can create this.",
                "publisher": self.publisher.id,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Article.objects.filter(title="Journalist Article").exists()
        )

    def test_reader_cannot_approve_article(self):
        self.authenticate_as_reader()

        response = self.client.post(
            f"/api/articles/{self.pending_article.id}/approve/"
        )

        self.assertEqual(response.status_code, 403)

    def test_editor_can_approve_article(self):
        self.authenticate_as_editor()

        response = self.client.post(
            f"/api/articles/{self.pending_article.id}/approve/"
        )

        self.assertEqual(response.status_code, 200)

        self.pending_article.refresh_from_db()
        self.assertTrue(self.pending_article.approved)

    def test_editor_can_delete_article(self):
        self.authenticate_as_editor()

        response = self.client.delete(
            f"/api/articles/{self.approved_article.id}/"
        )

        self.assertEqual(response.status_code, 204)

    def test_newsletters_are_returned(self):
        response = self.client.get("/api/newsletters/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Weekly Newsletter")

    def test_journalist_can_create_newsletter(self):
        self.authenticate_as_journalist()

        response = self.client.post(
            "/api/newsletters/",
            {
                "title": "New Newsletter",
                "description": "Created by journalist.",
                "articles": [self.approved_article.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Newsletter.objects.filter(title="New Newsletter").exists()
        )

    def test_editor_can_create_publisher(self):
        self.authenticate_as_editor()

        response = self.client.post(
            "/api/publishers/",
            {
                "name": "Editor Publisher",
                "description": "Created by editor.",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Publisher.objects.filter(name="Editor Publisher").exists()
        )