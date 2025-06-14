# Code:
import tkinter as tk
from tkinter import scrolledtext
from google import genai
import os
from dotenv import load_dotenv as lde

lde('.env')
api_key = os.getenv('API_KEY')
client = genai.Client(api_key=api_key)

class ChatBot:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatBot")
        # self.root.geometry("400x600")
        #Set full screen mode
        self.root.attributes("-fullscreen", True)
        #What should be on the landing page
        self.Label = tk.Label(text="What can I help with?", font=("Arial", 18), fg="#007bff")
        self.Label.pack(padx=10, pady= 10)

        # Create chat window
        self.chat_window = scrolledtext.ScrolledText(self.root, width=100, height=26, font=("Arial", 12), bg="#f0f0f0", fg="#000000")
        self.chat_window.pack(padx=10, pady=10)

        # Create input field
        self.input_field = tk.Text(self.root, width=80, height=8, font=("Arial", 12), bg = "#ffffff", fg="#000000")
        self.input_field.pack(padx=10, pady=10)

        # Create send button
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message,
                                     fg="#ffffff", bg="#007bff", activeforeground="#007bff", activebackground="white",
                                     cursor="hand2", border=3, font=("Arial", 12))
        self.send_button.pack(padx=10, pady=10)

        #Configure colors for user's Input and AI's response
        self.chat_window.tag_config("user", foreground="#007bff")
        self.chat_window.tag_config("ai", foreground="#6c757d")
    
    # You can try modifying the send_message method to include the user's input in the contents argument. Here's an example:

    def send_message(self, fg="blue"):
        # Get user input
        user_input = self.input_field.get("1.0", "end-1c")
        # Clear input field
        self.input_field.delete("1.0", "end")
        
    # Check if user input is related to privacy
        if "read the contents of this chat" in user_input.lower() or "read the user messages in this chat" in user_input.lower() or "who can view the messages in this chat" in user_input.lower():
            response_text = "For that type of information, please refer to Meta’s Privacy Center: https://www.facebook.com/privacy/center/"
        else:
            try:
            # Get response from API
                response = client.models.generate_content(model="gemini-2.0-flash", contents=user_input)

            # Display response in chat window
                response_text = response.text
            except Exception as e:
            # Handle error
                response_text = "Error: " + str(e)
        #Remove asterisks from response
        response_text = response.text.replace("*", "")
    # Clear input field
        self.input_field.delete("1.0", "end")
    
    # Display user input and response in chat window
        self.chat_window.insert("end", "You: " + user_input + "\n", "user")
        self.chat_window.insert("end", "ChatBot: " + response_text + "\n", "ai")

    # Scroll chat window to the bottom
        self.chat_window.see("end")



if __name__ == "__main__":
    root = tk.Tk()
    chatbot = ChatBot(root)
    root.mainloop()
