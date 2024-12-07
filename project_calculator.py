from tkinter import *
import re
import math
import os

class ScientificCalculator:
    def __init__(self, master):
        self.master = master
        self.master.title('Jntu-gv Calculator')
        self.master.state("zoomed")
        self.master.config(bg="#ffffff")  # Light background for the window

        # Track degree/radian mode
        self.is_degree_mode = True  
        self.is_inverse_mode = False  
        self.data = ""
        self.temp = ""
        self.sample = ""
        self.is_scientific_mode = False
        self.history = []

        # Main Frame for the whole UI
        self.Main_frame = Frame(self.master, bg="#1a252f")
        self.Main_frame.pack(fill=BOTH, expand=True)

        # Create a frame for buttons
        self.display_frame = Frame(self.Main_frame, bg="#1a252f", bd=10)
        self.display_frame.grid(row=0, column=0, sticky="nsew")

        # History Frame
        self.history_frame = Frame(self.Main_frame, bg="#1a252f", bd=10)
        self.history_frame.grid(row=0, column=1, sticky="nsew")

        # Text Widget for input/output
        self.text_box = Text(self.display_frame, width=20, height=2, font=("Arial", 35), bg="#f2f2f2", fg="#333333", padx=5, pady=15, bd=0, relief=FLAT)
        self.text_box.grid(row=0, columnspan=5, column=0, padx=5, pady=5, sticky="ew")

        self.history_canvas = Canvas(self.history_frame, bg="#1a252f")
        self.history_canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.scrollbar = Scrollbar(self.history_frame, orient=VERTICAL, command=self.history_canvas.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.history_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.history_canvas.bind('<Configure>', lambda e: self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all")))

        self.history_canvas_frame = Frame(self.history_canvas, bg="#1a252f")
        self.history_canvas.create_window((0, 0), window=self.history_canvas_frame, anchor='nw')

        label1 = Label(self.history_canvas_frame,bg="#1a252f",fg="#fff", text="History Pannel", padx=0, pady=5, font=("Arial", 18), anchor='w', wraplength=500)
        label1.grid(row=0, column=0, sticky='w', padx=15, pady=5)
        self.history_labels = []
        for i in range(100):
            label = Label(self.history_canvas_frame,bg="#1a252f",fg="#fff", text="", padx=0, pady=5, font=("Arial", 18), anchor='w', wraplength=500)
            label.grid(row=i+1, column=0, sticky='w', padx=15, pady=5)
            self.history_labels.append(label)

        # Define buttons layout for both basic and scientific calculators
        self.basic_buttons = [
            ['AC', 'C', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['e', '0', '.', '=']
        ]

        # Buttons Layout
        self.scientific_buttons = [  
            ['2nd', 'deg', 'sin', 'cos', 'tan'],
            ['√', 'log', 'ln', '(', ')'],
            ['!', 'AC', 'C', '%', '÷'],
            ['^', '7', '8', '9', '*'],
            ['π', '4', '5', '6', '-'],
            ['2√', '1', '2', '3', '+'],
            ['1/x', 'e', '0', '.', '=']
        ]

        self.btn()
        self.create_buttons()

        self.master.bind('<Key>', self.key_input)
        self.master.bind('<Return>', lambda event: self.button_click('=')) 

        # Ensure the rows and columns in Main_frame are expandable
        self.Main_frame.grid_rowconfigure(0, weight=1)
        self.Main_frame.grid_columnconfigure(0, weight=2)  # Equal weight for display_frame
        self.Main_frame.grid_columnconfigure(1, weight=3)  # Equal weight for history_frame

    def btn(self):
        self.toggle_button = Button(self.display_frame, 
                                    text="Scientific", 
                                    command=self.toggle, 
                                    bg="#1a252f", 
                                    fg="#fff",
                                    font=("Arial", 14),
                                    bd=0,  # No border
                                    highlightthickness=0,  # No highlight border
                                    relief=FLAT,  # No relief effect (flat button)
                                    padx=10,  # No padding on x-axis
                                    pady=5,  # No padding on y-axis
                                    anchor='w',  # Align text to the left
                                    activebackground="#1a252f",  # Active background color
                                    activeforeground="#333333")  # Active text color
        self.toggle_button.grid(row=1, column=0, sticky="ew")

        # Adjust grid configuration to make sure buttons fit
        self.display_frame.grid_rowconfigure(1, weight=0)
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_columnconfigure(1, weight=1)
        self.display_frame.grid_columnconfigure(2, weight=1)
        self.display_frame.grid_columnconfigure(3, weight=1)
        self.display_frame.grid_columnconfigure(4, weight=1)  # Add this line to ensure the last column expands

    def key_input(self, event):
        allowed_keys = set("0123456789+-*/%^().!")
        key = event.char
        current_text = self.text_box.get("1.0", END).strip()

        # Check if the text box contains "Error"
        if current_text == "Error":
            # Clear the text box and reset it before processing new input
            self.text_box.delete(1.0, END)

        # Check for operators and prevent consecutive operators
        if key in "+-*/%^":
            if current_text and current_text[-1] in "+-*/%^":
                return "break"  # Don't allow another operator

        # Check if the key is allowed
        if key in allowed_keys:
            self.enable_cursor()
            self.text_box.insert(END, key)
        elif key == '\r':  # Enter key
            self.button_click('=')
        elif event.keysym == 'BackSpace':
            self.enable_cursor()
            self.button_click('C')
        elif event.keysym == 'Delete':
            self.enable_cursor()
            self.button_click('AC')
        else:
            return "break"


    def clear(self):
        self.text_box.delete(1.0, END)

        # Reset the history list
        self.history = []  # Clear the history data

        # Reset the history labels
        for label in self.history_labels:
            label.config(text="")

        # Update the history canvas scroll region to reflect the cleared content
        self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))

    def toggle(self):
        # Toggle the mode
        if self.is_scientific_mode:
            self.is_scientific_mode = False
            self.toggle_button.config(text="Scientific")  # Change button text to "Scientific"
        else:
            self.is_scientific_mode = True
            self.toggle_button.config(text="Basic")  # Change button text to "Basic"

        # Recreate buttons for the current mode (Basic or Scientific)
        self.create_buttons()

    def disable_cursor(self):
        self.text_box.config(state=DISABLED)

    def enable_cursor(self):
        self.text_box.config(state=NORMAL)
    def create_buttons(self):
        # Remove any old buttons before recreating them

        for widget in self.display_frame.winfo_children():
            if isinstance(widget, Button) and widget not in [self.toggle_button]:
                widget.destroy()

        for r in range(10):  # Adjust based on your maximum row count
            self.display_frame.grid_rowconfigure(r, weight=0)
        for c in range(5):  # Adjust based on your maximum column count
            self.display_frame.grid_columnconfigure(c, weight=0)
        buttons_layout = self.scientific_buttons if self.is_scientific_mode else self.basic_buttons

        buttons_layout = self.scientific_buttons if self.is_scientific_mode else self.basic_buttons
        for r, row in enumerate(buttons_layout):
            for c, text in enumerate(row):
                if text == 'deg' or text == 'rad':
                    if self.is_inverse_mode:
                        state = 'disabled'
                    else:
                        state = 'normal'
                else:
                    state = 'normal'

                # Create buttons based on conditions
                if text == '=':
                    btn = Button(self.display_frame, text=text, width=10, font=("Arial", 12, 'bold'), state=state, height=3, 
                                 bg="#4da6ff", fg="#ffffff", relief=FLAT, activebackground="#fff", activeforeground="#ffffff", 
                                 bd=0, padx=5, pady=5, highlightthickness=0, command=lambda t=text: self.button_click(t))
                    btn.grid(row=r+2, column=c, padx=5, pady=5, sticky='nsew')  # Spanning across 5 columns
                elif text == 'AC':
                    btn = Button(self.display_frame, text=text, width=10, font=("Arial", 12, 'bold'), state=state, height=3, 
                                 bg="#ff1a1a", fg="#ffffff", relief=FLAT, activebackground="#fff", activeforeground="#ffffff", 
                                 bd=0, padx=5, pady=5, highlightthickness=0, command=lambda t=text: self.button_click(t))
                    btn.grid(row=r+2, column=c, padx=5, pady=5, sticky='nsew')  # Spanning across 5 columns
                elif text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    btn = Button(self.display_frame, text=text, width=10, font=("Arial", 12, 'bold'), state=state, height=3, 
                                 bg="#fff", fg="#333333", relief=FLAT, activebackground="#e0e0e0", activeforeground="#333333", 
                                 bd=0, padx=5, pady=5, highlightthickness=0, command=lambda t=text: self.button_click(t))
                    btn.grid(row=r+2, column=c, padx=5, pady=5, sticky='nsew')
                else:
                    btn = Button(self.display_frame, text=text, width=10, font=("Arial", 12, 'bold'), state=state, height=3, 
                                 bg="#b3b3b3", fg="#333333", relief=FLAT, activebackground="#fff", activeforeground="#333333", 
                                 bd=0, padx=5, pady=5, highlightthickness=0, command=lambda t=text: self.button_click(t))
                    btn.grid(row=r+2, column=c, padx=5, pady=5, sticky='nsew')

                # Make buttons expand to fill space
                self.display_frame.grid_rowconfigure(r+2, weight=1)
                self.display_frame.grid_columnconfigure(c, weight=1)

        # Place the clear button at the right end of the first row of buttons
        if self.is_scientific_mode:
            clear_column = 4
        else:
            clear_column = 3
        self.clear_history = Button(self.display_frame, 
                                    text='Clear',
                                    bg="#1a252f", 
                                    fg="#fff",
                                    font=("Arial", 14),
                                    bd=0,  # No border
                                    highlightthickness=0,  # No highlight border
                                    relief=FLAT,  # No relief effect (flat button)
                                    anchor='w',  # Align text to the left
                                    activebackground="#1a252f",  # Active background color
                                    activeforeground="#333333", command=self.clear)
        self.clear_history.grid(row=1, column=clear_column, padx=0, pady=0, sticky="e")
        self.display_frame.grid_columnconfigure(clear_column, weight=1)

    def button_click(self, text):
        self.enable_cursor()
        self.sample = self.text_box.get(1.0, END).strip()

        if self.sample == 'Error':
            self.text_box.delete(1.0, END)

        if text in "+-*/%^":
        # Prevent consecutive operators
            if self.sample and self.sample[-1] in "+-*/%^":
                return  # Don't allow consecutive operators

            self.text_box.insert(END, text) 
        elif text == 'C':
            current_text = self.text_box.get(1.0, END)
            new_text = current_text[:-2]
            self.text_box.delete(1.0, END)
            self.text_box.insert(END, new_text, "right")
        elif text == 'AC':
            self.text_box.delete(1.0, END)
        elif text == '1/x':
            self.text_box.insert('end', '1 / ')
        elif text == 'deg' or text == 'rad':
            self.toggle_mode()
        elif text == '2nd':
            self.toggle_inverse_mode()
        elif text == '=':
            self.calculate_expression()
            self.disable_cursor() 
        elif text == 'Scientific':
            self.is_scientific_mode = True 
            self.create_buttons()
        elif text == 'Basic':
            self.is_scientific_mode = False
            self.create_buttons()
        else:

            self.text_box.insert(END, text, "right")

    def toggle_inverse_mode(self):
        self.is_inverse_mode = not self.is_inverse_mode
        if self.is_inverse_mode:
            self.scientific_buttons[0][2] = 'sin⁻¹'
            self.scientific_buttons[0][3] = 'cos⁻¹'
            self.scientific_buttons[0][4] = 'tan⁻¹'
        else:
            self.scientific_buttons[0][2] = 'sin'
            self.scientific_buttons[0][3] = 'cos'
            self.scientific_buttons[0][4] = 'tan'
        self.create_buttons()

    def toggle_mode(self):
        self.is_degree_mode = not self.is_degree_mode
        mode_text = 'deg' if self.is_degree_mode else 'rad'
        self.scientific_buttons[0][1] = mode_text
        self.create_buttons()

    def calculate_expression(self):
        expression = self.text_box.get(1.0, END).strip()
        expression = expression.replace('×', '*').replace('÷', '/')
        try:
                if 'log' in expression:
                    expression = expression.replace('log', 'math.log10(') + ')'
                if 'sin⁻¹' in expression:
                    expression = expression.replace('sin⁻¹', 'math.asin(') + ')'
                elif 'sin' in expression:
                    if self.is_degree_mode:
                        expression = expression.replace('sin', 'math.sin(math.radians(') + '))'
                    else:
                        expression = expression.replace('sin', 'math.sin(') + ')'

                if 'cos' in expression:
                    if self.is_degree_mode:
                        expression = expression.replace('cos', 'math.cos(math.radians(') + '))'
                    else:
                        expression = expression.replace('cos', 'math.cos(')+')'

                if 'tan' in expression:
                    if self.is_degree_mode:
                        expression = expression.replace('tan', 'math.tan(math.radians(') + '))'
                    else:
                        expression = expression.replace('tan', 'math.tan(')+')'
                if '√' in expression:
                    expression = expression.replace('√', 'math.sqrt(') + ')'
                if 'π' in expression:
                    expression = expression.replace('π', str(math.pi))
                if 'e' in expression:
                    expression = expression.replace('e', str(math.e))
                if '^' in expression:
                    expression = expression.replace('^', '**') 
                if '!' in expression:
                    factorial_matches = re.finditer(r'(\d+)!', expression)
                    for match in factorial_matches:
                        number = int(match.group(1))
                        factorial_value = math.factorial(number)
                        expression = expression.replace(f"{number}!", str(factorial_value))

                if '2√' in expression:
                    expression = expression.replace('2√', 'math.pow(') + ', 0.5)'  # square root is power 0.5

                result = eval(expression)
                self.data = self.text_box.get(1.0, END).strip()  # Remove extra newlines
                self.history.insert(0,self.data + ' = ' + str(result))
                for index, label in enumerate(self.history_labels):
                    if index < len(self.history):
                        label.config(text=self.history[index])
                    else:
                        label.config(text="")
                self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))

                # Update the text box with the result
                self.text_box.delete(1.0, END)
                self.text_box.insert(END, result)
                self.text_box.delete(1.0, END)
                self.text_box.insert(END, result)
        except Exception as e:
                self.text_box.delete("1.0", END)
                self.text_box.insert(END, "Error")
                self.disable_cursor()

if __name__ == "__main__":
    root = Tk()

    # Ensure the path points to the specific image file
    # "C:\Users\salac\OneDrive\Desktop\jntu.png"
    icon_path = icon_path = r"C:\Users\salac\OneDrive\Desktop\jntu.png"

    if os.path.exists(icon_path):
        try:
            icon_image = PhotoImage(file=icon_path)
            root.iconphoto(False, icon_image)
            print("Icon set successfully.")
        except Exception as e:
            print(f"Failed to set icon: {e}")
    else:
        print(f"Icon file not found: {icon_path}")

    calculator = ScientificCalculator(root)
    root.mainloop()