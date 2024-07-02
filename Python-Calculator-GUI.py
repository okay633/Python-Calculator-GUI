import tkinter as tk
from tkinter import messagebox
import math
import logging
import json
import os

# Author: Zedric | Github @Okay633
# Advanced Calculator with custom functions and error handling.
# This calculator supports trigonometric functions, logarithms, and advanced mathematical operations.
# It also includes error handling, clipboard functionality, and expression history.

# Configure logging
logging.basicConfig(filename='calculator_debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom Exceptions
class InvalidExpressionError(Exception):
    pass

class CalculationError(Exception):
    pass

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Complex Calculator")
        self.history_file = 'calculator_history.json'
        self.create_widgets()
        self.bind_events()
        self.load_history()

    def create_widgets(self):
        self.result_var = tk.StringVar()
        self.entry = tk.Entry(self.root, width=20, font=('Arial', 18), borderwidth=2, relief="sunken")
        self.entry.grid(row=0, column=0, columnspan=5, padx=5, pady=5)
        
        result_label = tk.Label(self.root, textvariable=self.result_var, font=('Arial', 18))
        result_label.grid(row=1, column=0, columnspan=5, padx=5, pady=5)
        
        button_layout = [
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('/', 2, 3), ('sin', 2, 4),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('*', 3, 3), ('cos', 3, 4),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('-', 4, 3), ('tan', 4, 4),
            ('0', 5, 0), ('.', 5, 1), ('+', 5, 2), ('=', 5, 3), ('sqrt', 5, 4),
            ('C', 6, 0), ('Del', 6, 1), ('pi', 6, 2), ('e', 6, 3), ('log', 6, 4)
        ]
        
        for (text, row, col) in button_layout:
            if text == '=':
                button = tk.Button(self.root, text=text, font=('Arial', 14), command=self.evaluate_expression)
            elif text == 'C':
                button = tk.Button(self.root, text=text, font=('Arial', 14), command=self.clear_all)
            elif text == 'Del':
                button = tk.Button(self.root, text=text, font=('Arial', 14), command=self.delete_last_char)
            else:
                button = tk.Button(self.root, text=text, font=('Arial', 14), command=lambda t=text: self.entry.insert(tk.END, t))
            button.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

        for i in range(5):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(7):
            self.root.grid_rowconfigure(i, weight=1)

        self.root.geometry("400x600")  # Adjusted size for better fit on mobile screens

    def bind_events(self):
        self.root.bind('<Return>', lambda event: self.evaluate_expression())
        self.root.bind('<BackSpace>', lambda event: self.delete_last_char())
        self.root.bind('<Control-c>', lambda event: self.copy_to_clipboard())
        self.root.bind('<Control-v>', lambda event: self.paste_from_clipboard())

    def evaluate_expression(self):
        expression = self.entry.get()
        logging.info(f"Evaluating expression: {expression}")
        try:
            expression = self.parse_expression(expression)
            if expression == "1+1":
                result = "C'mon Bruh"
            else:
                result = eval(expression, {"__builtins__": None}, self.math_functions())
            self.result_var.set(result)
            self.save_history(expression, result)
            logging.info(f"Expression evaluated: {expression} = {result}")
        except InvalidExpressionError as e:
            self.result_var.set(f"Invalid Expression: {e}")
            logging.error(f"Invalid Expression: {e}")
        except CalculationError as e:
            self.result_var.set(f"Calculation Error: {e}")
            logging.error(f"Calculation Error: {e}")
        except (SyntaxError, NameError, ZeroDivisionError, TypeError, ValueError) as e:
            self.result_var.set(f"Error: {e}")
            logging.error(f"Error evaluating expression '{expression}': {e}")
        except Exception as e:
            self.result_var.set(f"Unexpected Error: {e}")
            logging.critical(f"Unexpected Error: {e}")

    def parse_expression(self, expression):
        expression = expression.replace('pi', str(math.pi))
        expression = expression.replace('e', str(math.e))
        expression = expression.replace('sqrt', 'math.sqrt')
        expression = expression.replace('exp', 'math.exp')
        expression = expression.replace('log', 'math.log10')
        expression = expression.replace('^', '**')
        return expression

    def math_functions(self):
        return {
            'math': math,
            'sqrt': math.sqrt,
            'exp': math.exp,
            'log10': math.log10,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan
        }

    def delete_last_char(self):
        current_text = self.entry.get()
        if current_text:
            self.entry.delete(len(current_text) - 1, tk.END)

    def clear_all(self):
        self.entry.delete(0, tk.END)
        self.result_var.set("")

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.entry.get())
        logging.info("Copied to clipboard")

    def paste_from_clipboard(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.entry.insert(tk.END, clipboard_text)
            logging.info("Pasted from clipboard")
        except tk.TclError:
            logging.error("Clipboard is empty or contains invalid text")

    def save_history(self, expression, result):
        history = self.load_history() or []
        history.append({"expression": expression, "result": result})
        with open(self.history_file, 'w') as file:
            json.dump(history, file)
        logging.info("History saved")

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as file:
                history = json.load(file)
                logging.info("History loaded")
                return history
        return []

    def show_history(self):
        history = self.load_history()
        if not history:
            messagebox.showinfo("History", "No history found.")
            return
        history_text = "\n".join([f"{entry['expression']} = {entry['result']}" for entry in history])
        messagebox.showinfo("History", history_text)
        logging.info("Displayed history")

def main():
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()