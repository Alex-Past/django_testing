from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Тесты контента."""

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            author=cls.author,
            slug='note_slug'
        )
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_notes_list_for_different_users(self):
        """Тесты доступа заметок для разных пользователей."""
        url = reverse('notes:list')
        clients_note_in_list = (
            (self.author_client, True),
            (self.reader_client, False)
        )
        for client, note_in_list in clients_note_in_list:
            response = client.get(url)
            object_list = response.context['object_list']
            self.assertIs((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        """Тест формы."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            url = reverse(name, args=args)
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
