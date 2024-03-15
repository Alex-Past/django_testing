from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

URL_DELETE = pytest.lazy_fixture('url_delete')
URL_DETAIL = pytest.lazy_fixture('url_detail')
URL_EDIT = pytest.lazy_fixture('url_edit')
URL_HOME = pytest.lazy_fixture('url_home')
URL_LOGIN = pytest.lazy_fixture('url_login')
URL_LOGOUT = pytest.lazy_fixture('url_logout')
URL_SIGNUP = pytest.lazy_fixture('url_signup')


def test_home_availability_for_anonymous_user(client, url_home):
    """Анонимному пользователю доступна главная страница."""
    response = client.get(url_home)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (URL_HOME, URL_LOGIN, URL_LOGOUT, URL_SIGNUP)
)
def test_pages_availability_for_anonymous_user(client, url):
    """Доступные страницы для анонимных пользователей."""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (URL_DETAIL, URL_HOME),
)
def test_pages_availability_for_auth_user(not_author_client, url):
    """Доступные страницы для авторизованного пользователя."""
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
    'url',
    (URL_EDIT, URL_DELETE),
)
def test_pages_availability_for_different_users(
        parametrized_client, url, expected_status
):
    """Удаление и редактирование для разных пользователей."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (URL_EDIT, URL_DELETE),
)
def test_redirects(client, url, url_login):
    """Тесты редиректов."""
    expected_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
