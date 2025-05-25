import sys
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QScrollArea, QComboBox
)

from book_components import BookComposite, BookLeaf  # переконайся, що ці класи коректні

class BookRecommender(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Book Recommender System")
        self.setGeometry(200, 100, 1250, 700)

        self.layout = QVBoxLayout(self)

        self.heading = QLabel("BOOK RECOMMENDATION", self)
        self.heading.setStyleSheet("font: 30px bold; color: white;")
        self.heading.setAlignment(Qt.AlignCenter)

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Enter book name")
        self.search_box.setStyleSheet("font: 20px; background-color: white;")

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.search)

        self.check_var = QCheckBox("Publish Date", self)
        self.check_var.setChecked(True)

        self.check_var2 = QCheckBox("Rating", self)
        self.check_var2.setChecked(True)

        self.grouping_box = QComboBox(self)
        self.grouping_box.addItem("No Grouping")
        self.grouping_box.addItem("Group by Year")
        self.grouping_box.addItem("Group by Rating")
        self.grouping_box.addItem("Group by First Letter")
        self.grouping_box.addItem("Group by Author")
        self.grouping_box.currentIndexChanged.connect(self.search)

        self.layout.addWidget(self.heading)
        self.layout.addWidget(self.search_box)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.check_var)
        self.layout.addWidget(self.check_var2)
        self.layout.addWidget(QLabel("Group by:", self))
        self.layout.addWidget(self.grouping_box)

        self.results_layout = QVBoxLayout()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_widget.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.results_widget)
        self.layout.addWidget(self.scroll_area)

    def clear_results(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def search(self):
        self.clear_results()
        query = self.search_box.text().strip()
        if not query:
            return

        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=20"
        response = requests.get(url)
        if response.status_code != 200:
            print("Error fetching data")
            return

        data = response.json()
        group_mode = self.grouping_box.currentText()
        grouped = {}
        ungrouped = []

        for item in data.get('items', []):
            info = item.get('volumeInfo', {})
            title = info.get('title', 'N/A')
            published_date = info.get('publishedDate', 'N/A')
            rating = info.get('averageRating', 'N/A')
            image = info.get('imageLinks', {}).get('thumbnail', '')
            authors = info.get('authors', [])

            leaf = BookLeaf(title, image, published_date, rating, authors)

            if group_mode == "Group by Year":
                key = published_date.split('-')[0] if published_date != 'N/A' else "Unknown"
            elif group_mode == "Group by Rating":
                key = str(rating) if rating != 'N/A' else "No Rating"
            elif group_mode == "Group by First Letter":
                key = title[0].upper() if title and title[0].isalpha() else "#"
            elif group_mode == "Group by Author":
                # Якщо авторів кілька, можна брати першого або створити групу для кожного, 
                # але зазвичай беруть першого автора
                key = authors[0] if authors else "Unknown Author"
            else:
                key = None

            if key is None:
                ungrouped.append(leaf)
            else:
                if key not in grouped:
                    grouped[key] = BookComposite(key)
                grouped[key].add(leaf)

        if group_mode == "No Grouping":
            for leaf in ungrouped:
                leaf.display(
                    self.results_layout,
                    show_date=self.check_var.isChecked(),
                    show_rating=self.check_var2.isChecked()
                )
        else:
            for key in sorted(grouped.keys()):
                grouped[key].display(
                    self.results_layout,
                    show_date=self.check_var.isChecked(),
                    show_rating=self.check_var2.isChecked()
                )



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BookRecommender()
    window.show()
    sys.exit(app.exec_())
