from django.urls import reverse

from notes.forms import NoteForm
from .fixtures import BaseTestNote


class TestContent(BaseTestNote):
    """Тесты контента."""

    def test_notes_list_for_different_users(self):
        """Тесты доступа заметок для разных пользователей."""
        url = reverse('notes:list')
        clients_note_in_list = (
            (self.author_client, True),
            (self.reader_client, False)
        )
        for client, note_in_list in clients_note_in_list:
            with self.subTest():
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
            with self.subTest():
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
