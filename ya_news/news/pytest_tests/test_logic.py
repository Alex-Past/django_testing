import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from .conftest import COMMENT_TEXT


NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(new, client, form_data):
    """Анонимный пользователь не может создать коммент."""
    url = reverse('news:detail', args=(new.id,))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(new, author_client, form_data, author):
    """Авторизованный пользователь может создать коммент."""
    url = reverse('news:detail', args=(new.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == new
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, new):
    """Автор - культурный человек."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(new.id,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, new):
    """Автор может удалять коммент."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    url_to_comments = reverse('news:detail', args=(new.id,)) + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(comment, not_author_client):
    """Не автор не может удалять коммент."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, form_data, comment, new):
    """Автор может редактировать коммент."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=form_data)
    url_to_comments = reverse('news:detail', args=(new.id,)) + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(not_author_client,
                                                comment,
                                                form_data):
    """Автор не может редактировать чужой коммент."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
