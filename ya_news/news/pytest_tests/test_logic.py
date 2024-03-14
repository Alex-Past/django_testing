from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from .conftest import COMMENT_TEXT


BAD_WORDS_DATA = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}

COMMENT_FORM_DATA = {'text': COMMENT_TEXT}

NEW_COMMENT_TEXT = 'Обновлённый комментарий'


def test_anonymous_user_cant_create_comment(new, client):
    """Анонимный пользователь не может создать коммент."""
    url = reverse('news:detail', args=(new.id,))
    client.post(url, data=COMMENT_FORM_DATA)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(new, author_client, author):
    """Авторизованный пользователь может создать коммент."""
    url = reverse('news:detail', args=(new.id,))
    response = author_client.post(url, data=COMMENT_FORM_DATA)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == new
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, new):
    """Автор - культурный человек."""
    url = reverse('news:detail', args=(new.id,))
    response = author_client.post(url, data=BAD_WORDS_DATA)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment, new):
    """Автор может удалять коммент."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    url_to_comments = reverse('news:detail', args=(new.id,)) + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(comment, not_author_client):
    """Не автор не может удалять коммент."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, comment, new):
    """Автор может редактировать коммент."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=COMMENT_FORM_DATA)
    url_to_comments = reverse('news:detail', args=(new.id,)) + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == COMMENT_FORM_DATA['text']


def test_user_cant_edit_comment_of_another_user(not_author_client, comment):
    """Автор не может редактировать чужой коммент."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data=COMMENT_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
