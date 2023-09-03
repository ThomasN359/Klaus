import os
from dotenv import load_dotenv
import pickle
import openai
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox, QVBoxLayout, QWidget, QLineEdit, QTextEdit, QHBoxLayout, \
    QScrollBar, QScrollArea
from PyQt5.QtGui import QKeyEvent, QIcon
from KlausSrc.Utilities.config import pickleDirectory
from KlausSrc.Utilities.HelperFunctions import makePath
from KlausSrc.Utilities.config import selfAwareness, initialPrompt, commandPrompt

load_dotenv()
if "OPENAI_KEY" in os.environ:
    openai.api_key = os.environ['OPENAI_KEY']
else:
    openai.api_key = ""



class MessageLabel(QLabel):
    def __init__(self, text, color):
        super().__init__()
        self.setText(text)
        self.setWordWrap(True)
        self.setStyleSheet(f"background-color: {color}; border-radius: 5px; padding: 5px;")
        self.setContentsMargins(5, 5, 5, 5)


class ChatWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, parent=None):
        super().__init__(parent)
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.initUI()
        self.conversation = [{"role": "system", "content": initialPrompt}]
        print(initialPrompt)
        self.conversation2 = None

    def initUI(self):
        layout = QVBoxLayout()

        label = QLabel("Klaus", self)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        self.chat_display_widget = QWidget()
        self.scroll_area.setWidget(self.chat_display_widget)

        self.chat_display_widget.setStyleSheet("border: 2px solid black")

        self.chat_display_layout = QVBoxLayout()
        self.chat_display_layout.setAlignment(Qt.AlignTop)
        self.chat_display_widget.setLayout(self.chat_display_layout)

        self.chat_input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Chat Here")
        self.chat_input.setStyleSheet("background-color: rgba(255, 255, 255, 228);")
        self.chat_input.keyPressEvent = self.on_key_press
        self.chat_input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon('arrow.png'))
        self.send_button.clicked.connect(self.send_message)
        self.chat_input_layout.addWidget(self.send_button)

        layout.addLayout(self.chat_input_layout)

        self.setLayout(layout)

        self.setStyleSheet("border: 2px solid black")

    def on_key_press(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.send_message()
        else:
            QLineEdit.keyPressEvent(self.chat_input, event)

    def send_message(self):
        message = self.chat_input.text()
        if message:
            self.display_message("You: " + message, "white")
            self.chat_input.clear()

            # Add the user's message to the conversation
            self.conversation.append({"role": "user", "content": message})

            self.conversation2 = [{"role": "user", "content": message}]

            try:
                namespace = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=self.conversation,
                    temperature = 0
                )
                if namespace:
                    assistant_reply = namespace['choices'][0]['message']['content']

                    message_color = ""
                    # Decide on the response based on the assistant's reply
                    if assistant_reply == "userstats":
                        conversation = {"role": "system", "content": "Tell the user that userstats haven't been implemented yet"}
                        message_color = "purple"
                    elif assistant_reply == "command":
                        conversation = {"role": "system", "content": commandPrompt}
                        message_color = "red"
                    elif assistant_reply == "selfawareness":
                        conversation = {"role": "system", "content": selfAwareness}
                        message_color = "yellow"
                    elif assistant_reply == "question":
                        conversation = {"role": "system", "content": "Respond normally but avoid saying you are an AI model"}
                        message_color = "green"
                    self.conversation2.append(conversation)

                    # Now get the assistant's real response
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages = self.conversation2,
                        temperature = 0
                    )

                    if response:
                        final_reply = response['choices'][0]['message']['content']
                        self.display_message("Klaus: " + final_reply, message_color)
                        print(assistant_reply)
                        print(response)

                        # Only add the final reply to the conversation
                        #self.conversation.append({"role": "assistant", "content": final_reply})
            except Exception as e:
                self.display_message("Error: " + str(e))

    def display_message(self, message: str, color: str):
        message_label = MessageLabel(message, color)
        self.chat_display_layout.addWidget(message_label)
