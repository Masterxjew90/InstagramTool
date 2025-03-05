from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFileDialog, QDateTimeEdit, QMessageBox, QListWidget, QDialog, QMenu)
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtCore import Qt, QDateTime
from instagrapi import Client
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import sys
import requests

class InstagramBot(QWidget):
    def __init__(self):
        super().__init__()
        self.client = Client()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.scheduled_posts = []
        self.scheduled_window = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Instagram Scheduler")
        self.setGeometry(100, 100, 400, 500)
        self.layout = QVBoxLayout()

        self.setStyleSheet("""
            background-color: #fafafa;
            border-radius: 10px;
            padding: 20px;
        """)

        self.title_label = QLabel(self)
        pixmap = QPixmap()
        pixmap.loadFromData(requests.get("https://www.cdata.com/ui/img/logo-instagram.png").content) 
        self.title_label.setPixmap(pixmap)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)

        self.create_input_field("Enter Username", self.username_input)
        self.create_input_field("Enter Password", self.password_input, echo_mode=QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Login", self)
        self.login_button.setStyleSheet("""
            background-color: #3b5998;
            color: white;
            border-radius: 20px;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
        """)
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

    def create_input_field(self, placeholder_text, input_field, echo_mode=None):
        input_field.setPlaceholderText(placeholder_text)
        input_field.setStyleSheet("""
            border: 2px solid #ccc;
            border-radius: 20px;
            padding: 10px;
            font-size: 14px;
            background-color: #fff;
        """)
        if echo_mode:
            input_field.setEchoMode(echo_mode)
        self.layout.addWidget(input_field)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            self.client.login(username, password)
            QMessageBox.information(self, "Success", "Logged in successfully!")
            self.setup_post_ui()
            self.start_auto_message_checker()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {e}")

    def setup_post_ui(self):
        for widget in [self.title_label, self.username_input, self.password_input, self.login_button]:
            widget.setParent(None)

        self.file_label = QLabel(self)
        self.layout.addWidget(self.file_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.file_button = QPushButton("Select Image/Video", self)
        self.file_button.setStyleSheet("""
            background-color: #3b5998;
            color: white;
            border-radius: 20px;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
        """)
        self.file_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.file_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Enter Post Title")
        self.title_input.setStyleSheet("""
            border: 2px solid #ccc;
            border-radius: 20px;
            padding: 10px;
            font-size: 14px;
            background-color: #fff;
        """)
        self.layout.addWidget(self.title_input, alignment=Qt.AlignmentFlag.AlignCenter)

        self.datetime_edit = QDateTimeEdit(self)
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit.setStyleSheet("""
            QDateTimeEdit::down-button, QDateTimeEdit::up-button {
                border: none;
                width: 0px;
                height: 0px;
                background: transparent;
            }
        """)
        self.layout.addWidget(self.datetime_edit, alignment=Qt.AlignmentFlag.AlignCenter)

        self.schedule_button = QPushButton("Schedule Post", self)
        self.schedule_button.setStyleSheet("""
            background-color: #3b5998;
            color: white;
            border-radius: 20px;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
        """)
        self.schedule_button.clicked.connect(self.schedule_post)
        self.layout.addWidget(self.schedule_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.scheduled_button = QPushButton("Scheduled Posts", self)
        self.scheduled_button.setStyleSheet("""
            background-color: #3b5998;
            color: white;
            border-radius: 20px;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
        """)
        self.scheduled_button.clicked.connect(self.view_scheduled_posts)
        self.layout.addWidget(self.scheduled_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Media File", "", "Images/Video Files (*.png *.jpg *.mp4)")
        if file_path:
            self.selected_file = file_path
            pixmap = QPixmap(file_path)
            self.file_label.setPixmap(pixmap.scaled(200, 200))

    def schedule_post(self):
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, "Warning", "No file selected!")
            return

        post_time = self.datetime_edit.dateTime().toPyDateTime()
        post_title = self.title_input.text()

        existing_post = next((p for p in self.scheduled_posts if p[0] == self.selected_file and p[1] == post_title), None)
        
        if existing_post:
            QMessageBox.warning(self, "Warning", "This post is already scheduled!")
            return

        job = self.scheduler.add_job(self.post_media, 'date', run_date=post_time, args=[self.selected_file, post_title])
        self.scheduled_posts.append((self.selected_file, post_title, post_time, job))
        QMessageBox.information(self, "Scheduled", "Post scheduled successfully!")

    def view_scheduled_posts(self):
        if self.scheduled_window:
            return

        self.scheduled_window = QDialog(self)
        self.scheduled_window.setWindowTitle("Scheduled Posts")
        self.scheduled_window.setGeometry(200, 200, 300, 300)
        layout = QVBoxLayout()

        list_widget = QListWidget()
        for file, title, time, _ in self.scheduled_posts:
            list_widget.addItem(f"{title} - {file} - {time}")

        list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(list_widget)

        self.scheduled_window.setLayout(layout)
        self.scheduled_window.show()
        self.scheduled_window.finished.connect(self.clear_scheduled_window)

    def show_context_menu(self, pos):
        list_widget = self.sender()
        item = list_widget.itemAt(pos)
        if item:
            context_menu = QMenu()
            remove_action = QAction("Remove", self)
            remove_action.triggered.connect(lambda: self.remove_scheduled_post(item))
            context_menu.addAction(remove_action)
            context_menu.exec(list_widget.mapToGlobal(pos))

    def remove_scheduled_post(self, item):
        index = item.listWidget().row(item)
        post_file, post_title, post_time, job = self.scheduled_posts.pop(index)

        try:
            job.remove()
        except JobLookupError:
            print(f"Job for post '{post_title}' has already been executed or does not exist.")
    
        item.listWidget().takeItem(index)
        print(f"Post '{post_title}' removed from scheduler.")

    def clear_scheduled_window(self):
        self.scheduled_window = None

    def post_media(self, file_path, title):
        try:
            post = self.client.photo_upload(file_path, title)
            print("Post uploaded successfully!")
        except Exception as e:
            print(f"Failed to upload post: {e}")

    def start_auto_message_checker(self):
        self.scheduler.add_job(self.check_likes_and_comments, 'interval', minutes=5)

    def check_likes_and_comments(self):
        try:
            if not self.client.user_id:
                print("Session expired, logging in again...")
                self.client.relogin()

            user_posts = self.client.user_medias(self.client.user_id, 10)

            for post in user_posts:
                try:
                    likers = self.client.media_likers(post.id)
                    for liker in likers:
                        self.client.direct_send("Thank you for liking my post!", [liker.pk])

                    comments = self.client.media_comments(post.id)
                    for comment in comments:
                        if not comment.user.is_self:
                            self.client.comment_like(comment.id)
                            self.client.comment_reply(post.id, comment.id, "Thank you for your comment!")
                except Exception as inner_e:
                    print(f"Error processing post: {inner_e}")
        except Exception as e:
            print(f"Error checking likes/comments: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InstagramBot()
    window.show()
    sys.exit(app.exec())
