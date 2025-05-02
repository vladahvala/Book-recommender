import sys
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QHBoxLayout, QMenu, QMenuBar, QFrame, QScrollArea
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image
from io import BytesIO

class BookRecommender(QWidget):
    def __init__(self):
        super().__init__()

        self.inc = 0

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Book Recommender System")
        self.setGeometry(200, 100, 1250, 700)

        self.layout = QVBoxLayout(self)

        # Заголовок
        self.heading = QLabel("BOOK RECOMMENDATION", self)
        self.heading.setStyleSheet("font: 30px bold; color: white;")
        self.heading.setAlignment(Qt.AlignCenter)

        # Поле для пошуку
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Enter book name")
        self.search_box.setStyleSheet("font: 20px; background-color: white;")
        
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.search)

        # Чекбокси
        self.check_var = QCheckBox("Publish Date", self)
        self.check_var.setChecked(True)

        self.check_var2 = QCheckBox("Rating", self)
        self.check_var2.setChecked(True)

        # Розміщуємо елементи на екран
        self.layout.addWidget(self.heading)
        self.layout.addWidget(self.search_box)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.check_var)
        self.layout.addWidget(self.check_var2)

        # Секція для відображення результатів
        self.results_layout = QVBoxLayout()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_widget.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.results_widget)
        self.layout.addWidget(self.scroll_area)

    def fetch_information(self, title, poster, date, rating):
        self.inc += 1

        frame = QFrame(self)
        frame.setStyleSheet("background-color: white;")
        frame_layout = QVBoxLayout(frame)

        # Книга
        title_label = QLabel(title, self)
        frame_layout.addWidget(title_label)

        # Завантажуємо зображення з URL
        response = requests.get(poster)
        img_data = response.content
        img = Image.open(BytesIO(img_data))

        # Змінимо розмір зображення
        resized_image = img.resize((140, 200))

        # Конвертуємо зображення в QImage
        qimage = self.pil_image_to_qimage(resized_image)

        # Створюємо QPixmap з QImage
        photo = QPixmap.fromImage(qimage)
        image_label = QLabel(self)
        image_label.setPixmap(photo)
        frame_layout.addWidget(image_label)

        # Дата публікації
        if self.check_var.isChecked():
            date_label = QLabel(date, self)
            frame_layout.addWidget(date_label)

        # Рейтинг
        if self.check_var2.isChecked():
            rating_label = QLabel(f"Rating: {rating}", self)
            frame_layout.addWidget(rating_label)

        self.results_layout.addWidget(frame)

    def pil_image_to_qimage(self, pil_image):
        """Перетворення PIL.Image в QImage"""
        rgb_image = pil_image.convert("RGB")
        data = rgb_image.tobytes("raw", "RGB")
        qimage = QImage(data, rgb_image.width, rgb_image.height, QImage.Format_RGB888)
        return qimage

    def clear_results(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def search(self):
        self.clear_results()  # ОЧИЩАЄМО ПОПЕРЕДНІ РЕЗУЛЬТАТИ
        self.inc = 0
        query = self.search_box.text()
        if query:
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=5"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    volume_info = item.get('volumeInfo', {})
                    title = volume_info.get('title', 'N/A')
                    publisher = volume_info.get('publisher', 'N/A')
                    published_date = volume_info.get('publishedDate', 'N/A')
                    author = volume_info.get('authors', ['N/A'])[0]
                    rating = volume_info.get('averageRating', 'N/A')
                    image_links = volume_info.get('imageLinks', {})
                    image = image_links.get('thumbnail', 'N/A')

                    self.fetch_information(title, image, published_date, rating)
            else:
                print("Failed to fetch data from Google Books API")
        else:
            print("Please enter a search query.")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = BookRecommender()
    window.show()

    sys.exit(app.exec_())
