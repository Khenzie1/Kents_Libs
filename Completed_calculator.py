#fetches the Module (Tkinter)
import tkinter as tk
from tkinter import messagebox
from PIL import Image
#This function restricts the input of letters
def validate_input(P):
    allowed_chars = '0,1,2,3,4,5,6,7,8,9,.,+,-,%,/,*'#, error'
    if '//' in P or '/0' in P:
        messagebox.showerror("Error", "Division by zero is not allowed")
        return False
    return all(char in allowed_chars for char in P)
#Creates the Window
window = tk.Tk()
window.geometry("350x499")
window.title("Kent Calculator_App")
image = Image.open("calculate.png")
image.save("calculate.ico", format="ICO")
window.iconbitmap("calculate.ico")
# Sets the widgets (i.e Display screen and Button frames in place more like being responsive
#more like by setting how many columns as well as rows the window should have)
window.columnconfigure(0, weight =1)
window.rowconfigure(0, weight=1)
# Creates the Display screen
Display = tk.Entry(window, width=20, font=('Arial', 20), validate="key")
Display.config(validatecommand=(window.register(validate_input), '%P'))
Display.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
# Display.focus()
#Creates the frame in which the Buttons are meant to be placed on
buttonframe = tk.Frame(window, cursor="hand2")
# Ensures the buttons in the key frame are arranged without having an overflow
#but to fit the size of the window
buttonframe.columnconfigure(0, weight = 1)
buttonframe.columnconfigure(1, weight = 1)
buttonframe.columnconfigure(2, weight = 1)
buttonframe.columnconfigure(3, weight = 1)
#The buttons in the keyframe
btnclr = tk.Button(buttonframe, text="C", font="Arial, 18",
                   command=lambda:Display.delete(0, tk.END))
btnclr.grid(row=0, column=0, sticky=tk.W+tk.E)
btndivide = tk.Button(buttonframe, text="/", font="Arial, 18",
                 command=lambda:Display.insert(tk.END, "/"))
btndivide.grid(row=0, column=1, sticky=tk.W+tk.E)
btntimes = tk.Button(buttonframe, text="*", font="Arial, 18",
                     command=lambda:Display.insert(tk.END, "*"))
btntimes.grid(row=0, column=2, sticky=tk.W+tk.E)
btndel = tk.Button(buttonframe, text="DEL", font="Arial, 18",
                   fg="red", activeforeground="red",
                 command=lambda:Display.delete(Display.index(tk.END)-1, tk.END))
btndel.grid(row=0, column=3, sticky=tk.W+tk.E) 
btn7 = tk.Button(buttonframe, text="7", font="Arial, 18",
                 fg="blue", activeforeground="blue",
                 command=lambda:Display.insert(tk.END, "7"))
btn7.grid(row=1, column=0, sticky=tk.W+tk.E)
btn8 = tk.Button(buttonframe, text="8", font="Arial, 18",
                 fg="blue", activeforeground="blue",
                 command=lambda:Display.insert(tk.END, "8"))
btn8.grid(row=1, column=1, sticky=tk.W+tk.E)
btn9 = tk.Button(buttonframe, text="9", font="Arial, 18",
                 fg="blue", activeforeground="blue",
                 command=lambda:Display.insert(tk.END, "9"))
btn9.grid(row=1, column=2, sticky=tk.W+tk.E)
btnminus = tk.Button(buttonframe, text="-", font="Arial, 18",
                     command=lambda:Display.insert(tk.END, "-"))
btnminus.grid(row=1, column=3, sticky=tk.W+tk.E)
btn4 = tk.Button(buttonframe, text="4", font="Arial, 18",
                 fg="blue", activeforeground="blue",
                 command=lambda:Display.insert(tk.END, "4"))
btn4.grid(row=2, column=0, sticky=tk.W+tk.E)
btn5 = tk.Button(buttonframe, text="5", font="Arial, 18",
                 fg="blue", activeforeground="blue",
                 command=lambda:Display.insert(tk.END, "5"))
btn5.grid(row=2, column=1, sticky=tk.W+tk.E)
btn6 = tk.Button(buttonframe, text="6", font="Arial, 18",
                 fg="blue", activeforeground="blue",
                 command=lambda:Display.insert(tk.END, "6"))
btn6.grid(row=2, column=2, sticky=tk.W+tk.E)
btnplus = tk.Button(buttonframe, text="+", font="Arial, 18",
                    command=lambda:Display.insert(tk.END, "+"), fg="black")
btnplus.grid(row=2, column=3, sticky=tk.W+tk.E)
btn1 = tk.Button(buttonframe, text="1", font="Arial, 18",
                 fg="blue", activeforeground="blue",
                 command=lambda:Display.insert(tk.END, "1"))
btn1.grid(row=3, column=0, sticky=tk.W+tk.E)
btn2 = tk.Button(buttonframe, text="2", font="Arial, 18",
                 fg="blue", activeforeground="blue", 
                 command=lambda:Display.insert(tk.END, "2"))
btn2.grid(row=3, column=1, sticky=tk.W+tk.E)
btn3 = tk.Button(buttonframe, text="3", font="Arial, 18",
                 fg="blue", activeforeground="blue",
                 command=lambda:Display.insert(tk.END, "3"))
btn3.grid(row=3, column=2, sticky=tk.W+tk.E)
btnper = tk.Button(buttonframe, text="%", font="Arial, 18",
                 command=lambda:Display.insert(tk.END, "%"))
btnper.grid(row=3, column=3, sticky=tk.W+tk.E)
btn00 = tk.Button(buttonframe, text="00", font="Arial, 18",
                 fg="blue", activeforeground="blue",
                 command=lambda:Display.insert(tk.END, str("0")+ str("0")))
btn00.grid(row=4, column=0, sticky=tk.W+tk.E)
btn0 = tk.Button(buttonframe, text="0", font="Arial, 18",
                 fg="blue", activeforeground="blue",
                 command=lambda:Display.insert(tk.END, "0"))
btn0.grid(row=4, column=1, sticky=tk.W+tk.E)
btndot = tk.Button(buttonframe, text=".", font="Arial, 18",
                 fg="blue", activeforeground="blue",
                 command=lambda:Display.insert(tk.END, "."))
btndot.grid(row=4, column=2, sticky=tk.W+tk.E)
expression = ""
btneq = tk.Button(buttonframe, text="=", font="Arial, 18",
                  fg="white", bg = "blue", activeforeground="blue", activebackground="white",
                command=lambda:[result := str(eval(expression)), Display.delete(0, tk.END), Display.insert(tk.END, result), expression := ""])
btneq.grid(row=4, column=3, sticky=tk.W+tk.E)
buttonframe.grid(row= 1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
#This function ensures parameters can be deleted
def clear_display():
    Display.delete(0, tk.END)
#This function ensures that parameters are calculated
def calculate():
    try:
        result = eval(Display.get())
        Display.delete(0, tk.END)
        Display.insert(0, result)
    except Exception as e:
        Display.delete(0,tk.END)
        Display.insert(0, "error")
btneq.config(command=calculate)
btnclr.config(command=clear_display)
window.mainloop()


#classes, inheritance, polymorphism, abstraction, Encapsulation, OOP(Object Oriented Programming), 
#Javatpoint and W3schools, Geeksforgeeks  