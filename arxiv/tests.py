from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Article, Author

# Create your tests here.
class ArticleCountTestCase(TestCase):
    fixtures = ['arxiv/fixtures/small_dump.json']

    def test_only_published_authors(self):
        response = self.client.get(reverse('arxiv:article_count'))
        self.assertEqual(response.status_code, 200)

        counts = {author.name: count for author, count in response.context['counts']}
        self.assertEqual(min(counts.values()), 1)

    def test_biggest_authors(self):
        response = self.client.get(reverse('arxiv:article_count'))
        self.assertEqual(response.status_code, 200)

        counts = {author.name: count for author, count in response.context['counts']}
        self.assertEqual(max(counts.values()), 3)

        biggest_authors = [k for k, v in counts.items() if v == 3]
        self.assertEqual(len(biggest_authors), 1)
        self.assertEqual(set(biggest_authors), {"Fedor V. Fomin"})
