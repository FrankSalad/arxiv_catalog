import datetime
import django # just to make sure the environment is okay
import requests
from bs4 import BeautifulSoup

from arxiv.models import Article, Author


api_root = "http://export.arxiv.org/api/query"
date_format = "%Y-%m-%dT%H:%M:%SZ"


def get_articles(keywords=None, start=0, max_results=10):
    if keywords is None:
        keywords = ["data science", "psychiatry", "computing"]
    keyword_query = "+AND+".join(keywords)

    response = requests.get(
        api_root,
        params = {
            "search_query": f"all:{keyword_query}",
            "start": start,
            "max_results": max_results,
            "sortBy": "lastUpdatedDate",
            "sortOrder": "descending",
        }
    )

    soup = BeautifulSoup(response.content)

    results = []
    for entry in soup.find_all("entry"):
        data = {
            "id": entry.find("id").text,
            "title": entry.title.text,
            "subject": entry.find("arxiv:primary_category")["term"],
            "authors": [
                author.find("name").text
                for author in entry.find_all("author")
            ],
            "summary": entry.summary.text,
            "published": datetime.datetime.strptime(entry.find("published").text, date_format),
            "updated": datetime.datetime.strptime(entry.find("updated").text, date_format),
        }
        results.append(data)

    return results


def add_to_database(arxiv_data):
    for entry in arxiv_data:
        article = Article.objects.create(
            article_id=entry["id"],
            title=entry["title"],
            subject=entry["subject"],
            summary=entry["summary"],
            published=entry["published"],
            updated=entry["updated"],
        )

        authors = [Author.objects.create(name=author) for author in entry["authors"]]
        for author in authors:
            author.save()
            author.articles.add(article)
        article.save()


if __name__ == "__main__":
    print("Getting articles from arxiv")
    response = get_articles(max_results=1)

    print("Adding to database")
    add_to_database(response)

    print("Done")
