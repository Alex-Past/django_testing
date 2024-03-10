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

    def test_home_availability_for_anonymous_user(self):
        """Анонимному пользователю доступна главная страница."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_anonymous_user(self):
        """Доступ для анонимных пользователей."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Доступ страниц для авторизованного пользователя."""
        urls = (
            'notes:list',
            'notes:add',
            'notes:success'
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """Доступ разных страниц заметки для разных пользователей."""
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete'
        )
        clients_status = (
            (self.reader_client, HTTPStatus.NOT_FOUND),
            (self.author_client, HTTPStatus.OK)
        )
        for name in urls:
            with self.subTest(name=name, args=(self.note.slug,)):
                url = reverse(name, args=(self.note.slug,))
                for client, status in clients_status:
                    with self.subTest():
                        response = client.get(url)
                        self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """Тесты редиректов."""
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
        for name in ('notes:add', 'notes:success', 'notes:list'):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
