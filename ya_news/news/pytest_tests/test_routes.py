import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    """Анонимному пользователю доступна главная страница."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name):
    """Доступные страницы для анонимных пользователей."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
        ('news:home', None),
    ),
)
def test_pages_availability_for_auth_user(not_author_client, name, args):
    """Доступные страницы для авторизованного пользователя."""
    url = reverse(name, args=args)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    """Удаление и редактирование для разных пользователей."""
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_for_args')),
        ('news:delete', pytest.lazy_fixture('pk_for_args')),
    ),
)
@pytest.mark.django_db
def test_redirects(client, name, args):
    """Тесты редиректов."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
