from django.urls import reverse
import pytest

from news.forms import CommentForm
from django.conf import settings


@pytest.mark.parametrize(
    'param_client, expected_value',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False),
    )
)
def test_pages_contains_form(param_client, expected_value, comment):
    """Тест формы."""
    url = reverse('news:detail', args=(comment.pk,))
    response = param_client.get(url)
    assert isinstance(response.context.get('form'), CommentForm)


def test_news_order(client, t_new):
    """Тест сортировки новостей по дате."""
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_news_count(client, t_new):
    """Тест пагинация на домашней странице."""
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_comments_order(new, client):
    """тест сортировки комментариев."""
    url = reverse('news:detail', args=(new.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
