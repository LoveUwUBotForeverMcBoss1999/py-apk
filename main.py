from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.lang import Builder

import json
import os
from datetime import datetime
import time

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from plyer import gps


class MainScreen(Screen):
    def go_to_new_book(self):
        self.manager.current = 'new_book'

    def go_to_open_book(self):
        app = App.get_running_app()
        app.load_books_list()
        self.manager.current = 'open_book'


class NewBookScreen(Screen):
    def go_back(self):
        self.manager.current = 'main'

    def create_book(self):
        name = self.book_name.text.strip()
        start = self.start_place.text.strip()
        destination = self.destination.text.strip()

        if not name or not start or not destination:
            popup = Popup(title='Error', content=Label(text='Please fill all fields'),
                          size_hint=(0.8, 0.3))
            popup.open()
            return

        # Create new place book
        book_data = {
            'name': name,
            'start_place': start,
            'destination': destination,
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'places': []
        }

        app = App.get_running_app()
        app.current_book = book_data
        app.save_current_book()

        # Reset inputs
        self.book_name.text = ''
        self.start_place.text = ''
        self.destination.text = ''

        # Show success message
        popup = Popup(title='Success', content=Label(text=f'Created place book: {name}'),
                      size_hint=(0.8, 0.3))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

        # Go to book view
        self.manager.current = 'view_book'


class OpenBookScreen(Screen):
    def go_back(self):
        self.manager.current = 'main'

    def update_books_list(self, books):
        books_layout = self.ids.books_layout
        books_layout.clear_widgets()

        if not books:
            books_layout.add_widget(Label(text='No books found', size_hint_y=None, height=50))
            return

        for book in books:
            book_btn = Button(text=f"{book['name']}: {book['start_place']} → {book['destination']}",
                              size_hint_y=None, height=60)
            book_btn.book_data = book
            book_btn.bind(on_press=self.open_book)
            books_layout.add_widget(book_btn)

    def open_book(self, instance):
        app = App.get_running_app()
        app.current_book = instance.book_data
        self.manager.current = 'view_book'


class ViewBookScreen(Screen):
    def __init__(self, **kwargs):
        super(ViewBookScreen, self).__init__(**kwargs)

        # Add GPS button if on Android
        if platform == 'android':
            gps_btn = Button(text='Add Current Location', size_hint_y=None, height=50)
            gps_btn.bind(on_press=self.use_current_location)
            self.add_widget(gps_btn)

    def on_enter(self):
        app = App.get_running_app()
        if app.current_book:
            self.update_book_view()

    def update_book_view(self):
        app = App.get_running_app()
        book = app.current_book

        self.book_title.text = book['name']
        self.start_label.text = f"Start: {book['start_place']}"
        self.dest_label.text = f"Destination: {book['destination']}"
        self.date_label.text = f"Created: {book['created_date']}"

        self.places_layout.clear_widgets()
        if not book['places']:
            self.places_layout.add_widget(Label(text='No places added yet', size_hint_y=None, height=40))
        else:
            for place in book['places']:
                place_box = BoxLayout(size_hint_y=None, height=60)
                place_info = Label(text=f"{place['name']}\n{place['timestamp']}", size_hint_x=0.8)

                del_btn = Button(text='Delete', size_hint_x=0.2)
                del_btn.place_name = place['name']
                del_btn.bind(on_press=self.delete_place)

                place_box.add_widget(place_info)
                place_box.add_widget(del_btn)
                self.places_layout.add_widget(place_box)

    def go_back(self):
        self.manager.current = 'open_book'

    def add_place(self):
        place_name = self.place_input.text.strip()
        if not place_name:
            return

        app = App.get_running_app()

        new_place = {
            'name': place_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'location': {'lat': 0.0, 'lon': 0.0}  # Placeholder coordinates
        }

        app.current_book['places'].append(new_place)
        app.save_current_book()
        self.place_input.text = ''
        self.update_book_view()

    def delete_place(self, instance):
        place_name = instance.place_name
        app = App.get_running_app()

        # Find and remove the place
        app.current_book['places'] = [p for p in app.current_book['places'] if p['name'] != place_name]
        app.save_current_book()
        self.update_book_view()

    def use_current_location(self, instance=None):
        if platform == 'android':
            try:
                gps.configure(on_location=self.got_location)
                gps.start(minTime=1000, minDistance=0)
            except:
                popup = Popup(title='Error', content=Label(text='GPS not available'),
                              size_hint=(0.8, 0.3))
                popup.open()

    def got_location(self, **kwargs):
        lat = kwargs.get('lat', 0)
        lon = kwargs.get('lon', 0)

        # Use reverse geocoding service to get place name (simplified)
        place_name = f"Location ({lat:.4f}, {lon:.4f})"

        # Add place to book
        app = App.get_running_app()
        new_place = {
            'name': place_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'location': {'lat': lat, 'lon': lon}
        }

        app.current_book['places'].append(new_place)
        app.save_current_book()
        self.update_book_view()

        # Stop GPS after getting location
        if platform == 'android':
            gps.stop()


class PlaceBookApp(App):
    def build(self):
        # Load KV file
        Builder.load_file('project.kv')

        # Check and request permissions on Android
        if platform == 'android':
            request_permissions([
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])

        # Create data directory if it doesn't exist
        self.data_dir = self.get_data_dir()
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Initialize book data
        self.books = []
        self.current_book = None

        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(NewBookScreen(name='new_book'))
        sm.add_widget(OpenBookScreen(name='open_book'))
        sm.add_widget(ViewBookScreen(name='view_book'))

        return sm

    def get_data_dir(self):
        if platform == 'android':
            from android.storage import app_storage_path
            return os.path.join(app_storage_path(), 'placebooks')
        else:
            return os.path.join(os.path.expanduser('~'), '.placebooks')

    def load_books_list(self):
        self.books = []

        try:
            # List all JSON files in the data directory
            if os.path.exists(self.data_dir):
                for filename in os.listdir(self.data_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.data_dir, filename)
                        with open(filepath, 'r') as f:
                            book_data = json.load(f)
                            self.books.append(book_data)
        except Exception as e:
            print(f"Error loading books: {e}")

        # Update the open book screen
        open_screen = self.root.get_screen('open_book')
        open_screen.update_books_list(self.books)

    def save_current_book(self):
        if not self.current_book:
            return

        try:
            book_name = self.current_book['name']
            # Create a filename from the book name (with simple sanitization)
            filename = ''.join(c if c.isalnum() else '_' for c in book_name) + '.json'
            filepath = os.path.join(self.data_dir, filename)

            with open(filepath, 'w') as f:
                json.dump(self.current_book, f, indent=4)
        except Exception as e:
            print(f"Error saving book: {e}")


if __name__ == '__main__':
    PlaceBookApp().run()