from datetime import datetime, timedelta, timezone

from django.urls import reverse
import pytest
from django.test.client import Client

from django.conf import settings
from news.models import News, Comment

COMMENT_TEXT = 'Текст комментария'


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def new():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(new, author):
    return Comment.objects.create(
        news=new,
        text=COMMENT_TEXT,
        author=author,
    )


@pytest.fixture
def pk_for_args(comment):
    return (comment.pk,)


@pytest.fixture
def t_new():
    today = datetime.today()
    News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def t_comment(new, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=new, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
