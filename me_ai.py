# Here's a simplified example of how you can create a basic chatbot using Tkinter and OpenAI's API:

# Prerequisites:
# - Install the required libraries: tkinter and openai
# - Replace YOUR_OPENAI_API_KEY with your actual OpenAI API key

# Code:
import tkinter as tk
from tkinter import scrolledtext
# import openai
# from openai import OpenAI
from google import genai
# import ttkthemes

import os
from dotenv import load_dotenv as lde
# client = genai.Client(api_key="YOUR_API_KEY")

# response = client.models.generate_content(
#     model="gemini-2.0-flash", contents="Explain how AI works in a few words"
# )
# print(response.text)

# https://ai.google.dev/gemini-api/docs/quickstart?lang=python
# https://apistudio.google.com/app/apikey
        # AIzaSyA3GFYlzmaIg-xrWyylr_-rHe4aoLa6WYk
# Set up OpenAI API
# api_key = "AIzaSyA3GFYlzmaIg-xrWyylr_-rHe4aoLa6WYk"
lde('.env')
api_key: str = os.getenv('API_KEY')
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

        # style = ttkthemes.ThemedStyle(self.root)
        # style.set_theme("equilux")  # Use the equilux theme for dark mode

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
    
    # def send_message(self):
    #     # Get user input
    #     user_input = self.input_field.get("1.0", "end-1c")

        # # Clear input field
        # self.input_field.delete("1.0", "end")

        # # Display user input in chat window
        # self.chat_window.insert("end", "You: " + user_input + "\n")

#         Content Argument Issue
# The contents argument in the generate_content method is used to specify the input text for the model to generate a response. If the chatbot is not giving you the desired reply, it's possible that the contents argument is not being set correctly.

# Solution
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


# How it works:
# 1. The user types a message in the input field and clicks the "Send" button.
# 2. The send_message method gets the user's input, clears the input field, and displays the user's input in the chat window.
# 3. The method then sends the user's input to the OpenAI API using the openai.Completion.create method.
# 4. The API responds with a completion, which is then displayed in the chat window.

# # Note:
# - This is a very basic example, and you may want to add more features, such as error handling, input validation, and more.
# - Make sure to replace YOUR_OPENAI_API_KEY with your actual OpenAI API key.
# - This code uses the davinci engine, which is a general-purpose engine. You may want to experiment with other engines, such as curie or babbage, depending on your specific use case.

