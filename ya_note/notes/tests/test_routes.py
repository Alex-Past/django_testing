from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тесты путей."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Иван Иваныч')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author,
                                       slug='slug')
        cls.url = reverse('notes:home')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.URL_LOGIN = reverse('users:login')
        cls.URL_LOGOUT = reverse('users:logout')
        cls.URL_SINGUP = reverse('users:signup')
        cls.URL_HOME = reverse('notes:home')
        cls.URL_LIST = reverse('notes:list')
        cls.URL_ADD = reverse('notes:add')
        cls.URL_SUCCESS = reverse('notes:success')
        cls.URL_DETAIL = reverse('notes:detail', args=(cls.note.slug,))
        cls.URL_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.URL_DELETE = reverse('notes:delete', args=(cls.note.slug,))

    def test_home_availability_for_anonymous_user(self):
        """Анонимному пользователю доступна главная страница."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_anonymous_user(self):
        """Доступ для анонимных пользователей."""
        urls = (
            self.URL_HOME,
            self.URL_LOGIN,
            self.URL_LOGOUT,
            self.URL_SINGUP,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Доступ страниц для авторизованного пользователя."""
        urls = (
            self.URL_LIST,
            self.URL_ADD,
            self.URL_SUCCESS
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """Доступ разных страниц заметки для разных пользователей."""
        urls = (
            self.URL_DETAIL,
            self.URL_EDIT,
            self.URL_DELETE
        )
        clients_status = (
            (self.reader_client, HTTPStatus.NOT_FOUND),
            (self.author_client, HTTPStatus.OK)
        )
        for url in urls:
            for client, status in clients_status:
                with self.subTest(name=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """Тесты редиректов."""
        urls = (
            self.URL_LIST,
            self.URL_ADD,
            self.URL_SUCCESS,
            self.URL_EDIT,
            self.URL_DELETE
        )
        for url in urls:
            with self.subTest(name=url):
                redirect_url = f'{self.URL_LOGIN}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
