from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from .conftest import COMMENT_TEXT


BAD_WORDS_DATA = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}

COMMENT_FORM_DATA = {'text': COMMENT_TEXT}

NEW_COMMENT_TEXT = 'Обновлённый комментарий'


def test_anonymous_user_cant_create_comment(client, url_detail):
    """Анонимный пользователь не может создать коммент."""
    client.post(url_detail, data=COMMENT_FORM_DATA)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(new, author_client, author, url_detail):
    """Авторизованный пользователь может создать коммент."""
    response = author_client.post(url_detail, data=COMMENT_FORM_DATA)
    assertRedirects(response, f'{url_detail}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == new
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, url_detail):
    """Автор - культурный человек."""
    response = author_client.post(url_detail, data=BAD_WORDS_DATA)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, url_delete, url_detail):
    """Автор может удалять коммент."""
    response = author_client.delete(url_delete)
    assertRedirects(response, url_detail + '#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_not_author_cant_delete_comment(not_author_client, url_delete):
    """Не автор не может удалять коммент."""
    response = not_author_client.delete(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, comment, url_edit, url_detail):
    """Автор может редактировать коммент."""
    response = author_client.post(url_edit, data=COMMENT_FORM_DATA)
    assertRedirects(response, url_detail + '#comments')
    comment.refresh_from_db()
    assert comment.text == COMMENT_FORM_DATA['text']


def test_not_author_cant_edit_comment(not_author_client, comment, url_edit):
    """Автор не может редактировать чужой коммент."""
    response = not_author_client.post(url_edit, data=COMMENT_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
