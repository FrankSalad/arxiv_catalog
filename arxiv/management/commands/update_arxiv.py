import datetime
import requests
import pytz
import traceback
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from arxiv.models import Article, Author


api_root = "http://export.arxiv.org/api/query"
date_format = "%Y-%m-%dT%H:%M:%SZ"


def make_datetime(date_str):
    dt = datetime.datetime.strptime(date_str, date_format)
    return pytz.utc.localize(dt)


def get_articles(keywords=None, start=0, max_results=10):
    if keywords is None:
        keywords = ["data science", "psychiatry", "computing"]
    keyword_query = "+AND+".join(keywords)

    response = requests.get(
        api_root,
        params={
            "search_query": f"all:{keyword_query}",
            "start": start,
            "max_results": max_results,
            "sortBy": "lastUpdatedDate",
            "sortOrder": "descending",
        },
    )

    soup = BeautifulSoup(response.content)

    results = []
    for entry in soup.find_all("entry"):
        data = {
            "id": entry.find("id").text,
            "title": entry.title.text,
            "subject": entry.find("arxiv:primary_category")["term"],
            "authors": [author.find("name").text for author in entry.find_all("author")],
            "summary": entry.summary.text,
            "published": make_datetime(entry.find("published").text),
            "updated": make_datetime(entry.find("updated").text),
        }
        results.append(data)

    return results


class Command(BaseCommand):
    help = "Update database with latest data from arxiv"

    def add_to_database(self, arxiv_data):
        for entry in arxiv_data:
            try:
                article, created = Article.objects.get_or_create(
                    article_id=entry["id"],
                    title=entry["title"],
                    subject=entry["subject"],
                    summary=entry["summary"],
                    published=entry["published"],
                    updated=entry["updated"],
                )

                # TODO: This currently assumes that articles cannot change, which is untrue in reality
                if created:
                    authors = [
                        Author.objects.get_or_create(name=author)[0] for author in entry["authors"]
                    ]
                    for author in authors:
                        author.save()
                        author.articles.add(article)
                    article.save()
            except IntegrityError as e:
                # If we fail on one article, log the error but keep trying
                self.stderr.write(f"Failed to add article {entry['id']}: {e}")

    def update_articles_since(
        self, date, keywords=None, batch_size=10, max_results=None, max_retries=3
    ):
        date = pytz.utc.localize(date)
        start = 0
        n_articles = 0
        n_retries = 0
        last_date = pytz.utc.localize(datetime.datetime.utcnow())

        self.stdout.write("Beginning batch requests")
        while (
            last_date >= date
            and (max_results is None or n_articles < max_results)
            and (n_retries < max_retries)
        ):
            self.stdout.write(f"Requesting batch {start // batch_size}, from date {last_date}")
            batch = get_articles(keywords=keywords, start=start, max_results=batch_size)

            # If we get zero, do a retry
            if len(batch) == 0:
                self.stdout.write("Didn't get any results, retrying...")
                n_retries += 1
                continue

            # Otherwise If we get less than expected, break because likely something is not as expected
            if len(batch) < batch_size:
                self.stderr.write(
                    f"Something is fishy! We only got {len(batch)} articles in a batch, expected {batch_size}"
                )
                break

            last_date = batch[-1]["updated"]

            self.add_to_database(batch)

            start += len(batch)
            n_articles += len(batch)
            n_retries = 0

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--date",
            required=True,
            type=lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"),
            help="UTC Date from which to look for new articles",
        )
        parser.add_argument(
            "-k",
            "--keywords",
            default=None,
            type=lambda x: x.split(","),
            help="Optional list of specific keywords to search for",
        )
        parser.add_argument(
            "-m",
            "--max-results",
            default=None,
            type=int,
            help="Optional maximum number of articles to search for",
        )
        parser.add_argument(
            "-b", "--batch-size", default=10, type=int, help="Batch size to use for requests"
        )

    def handle(self, *args, **options):
        self.stdout.write("Getting articles from arxiv")
        try:
            self.update_articles_since(
                options["date"],
                keywords=options["keywords"],
                batch_size=options["batch_size"],
                max_results=options["max_results"],
            )
        except Exception as e:
            traceback.print_exc()
            raise CommandError(f"Failed to update data: {e}")
