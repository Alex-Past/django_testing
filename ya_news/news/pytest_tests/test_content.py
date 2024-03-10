import pytest

from django.urls import reverse

from news.forms import CommentForm
from yanews import settings


@pytest.mark.parametrize(
    'param_client, name',
    (
        (pytest.lazy_fixture('author_client'), 'news:detail'),
        (pytest.lazy_fixture('not_author_client'), 'news:detail'),
    )
)
@pytest.mark.django_db
def test_pages_contains_form(param_client, name, comment):
    """Тест формы."""
    url = reverse(name, args=(comment.pk,))
    response = param_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_news_order_count(client, t_new):
    """Тест сортировки новостей по дате и пагинация."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
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
