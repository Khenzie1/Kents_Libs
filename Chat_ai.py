import tkinter as tk
from tkinter import scrolledtext
import google.generativeai as genai
from pathlib import Path
from decouple import config

# Load API Key
BASE_DIR = Path(__file__).resolve().parent
api_key = config('API_KEY')

# Configure Gemini API
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

class ChatBot:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatBot")
        self.root.attributes("-fullscreen", True)

        self.Label = tk.Label(text="What can I help with?", font=("Arial", 18), fg="#007bff")
        self.Label.pack(padx=10, pady=10)

        self.chat_window = scrolledtext.ScrolledText(self.root, width=100, height=26, font=("Arial", 12), bg="#f0f0f0", fg="#000000")
        self.chat_window.pack(padx=10, pady=10)

        self.input_field = tk.Text(self.root, width=80, height=8, font=("Arial", 12), bg="#ffffff", fg="#000000")
        self.input_field.pack(padx=10, pady=10)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message,
                                     fg="#ffffff", bg="#007bff", activeforeground="#007bff", activebackground="white",
                                     cursor="hand2", border=3, font=("Arial", 12))
        self.send_button.pack(padx=10, pady=10)

        self.chat_window.tag_config("user", foreground="#007bff")
        self.chat_window.tag_config("ai", foreground="#6c757d")

    def send_message(self):
        user_input = self.input_field.get("1.0", "end-1c").strip()
        self.input_field.delete("1.0", "end")

        if not user_input:
            return

        if "read the contents of this chat" in user_input.lower():
            response_text = "For that type of information, please refer to Meta’s Privacy Center: https://www.facebook.com/privacy/center/"
        else:
            try:
                response = model.generate_content(user_input)
                response_text = response.text.replace("*", "")
            except Exception as e:
                response_text = "Error: " + str(e)

        self.chat_window.insert("end", "You: " + user_input + "\n", "user")
        self.chat_window.insert("end", "ChatBot: " + response_text + "\n", "ai")
        self.chat_window.see("end")


if __name__ == "__main__":
    root = tk.Tk()
    chatbot = ChatBot(root)
    root.mainloop()
