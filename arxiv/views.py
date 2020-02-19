import datetime
from django.shortcuts import render
from django.views import generic

from .models import Article, Author

# Create your views here.
class IndexView(generic.ListView):
    template_name = "arxiv/index.html"
    context_object_name = "article_list"

    def get_queryset(self):
        # Get all articles published in last 6 months
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=180)
        article_list = Article.objects.filter(published__gt=cutoff)
        article_list = sorted(article_list, key=lambda x: x.published, reverse=True)
        print(f"Found {len(article_list)} articles")
        return article_list


def article_count(request):
    # Get all articles published in last 6 months, then group by author
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=180)
    authors = Author.objects.all()

    counts = {}
    for author in authors:
        article_count = len(author.articles.filter(published__gt=cutoff))
        if article_count > 0:
            counts[author] = article_count

    # Sort by count
    counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    return render(request, "arxiv/article_count.html", {"counts": counts})


class ArticleView(generic.DetailView):
    model = Article
    template_name = "arxiv/article.html"


class AuthorView(generic.DetailView):
    model = Author
    template_name = "arxiv/author.html"
