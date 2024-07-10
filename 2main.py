import tkinter as tk
from tkinter import messagebox, scrolledtext
import math
import logging
import json
import os
import cmath
import sympy as sp
import numpy as np

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
        self.root.title("Advanced Calculator")
        self.history_file = 'calculator_history.json'
        self.memory = 0
        self.create_widgets()
        self.bind_events()
        self.load_history()

    def create_widgets(self):
        self.result_var = tk.StringVar()
        self.entry = tk.Entry(self.root, width=40, font=('Arial', 18), borderwidth=2, relief="sunken")
        self.entry.grid(row=0, column=0, columnspan=8, padx=5, pady=5)
        
        result_label = tk.Label(self.root, textvariable=self.result_var, font=('Arial', 18))
        result_label.grid(row=1, column=0, columnspan=8, padx=5, pady=5)
        
        button_layout = [
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('/', 2, 3), ('sin', 2, 4), ('cos', 2, 5), ('tan', 2, 6), ('exp', 2, 7),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('*', 3, 3), ('log', 3, 4), ('ln', 3, 5), ('sqrt', 3, 6), ('^', 3, 7),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('-', 4, 3), ('(', 4, 4), (')', 4, 5), ('abs', 4, 6), ('%', 4, 7),
            ('0', 5, 0), ('.', 5, 1), ('+', 5, 2), ('=', 5, 3), ('pi', 5, 4), ('e', 5, 5), ('i', 5, 6), ('j', 5, 7),
            ('C', 6, 0), ('Del', 6, 1), ('MC', 6, 2), ('MR', 6, 3), ('M+', 6, 4), ('M-', 6, 5), ('History', 6, 6), ('Matrices', 6, 7)
        ]
        
        for (text, row, col) in button_layout:
            if text == '=':
                button = tk.Button(self.root, text=text, font=('Arial', 14), command=self.evaluate_expression)
            elif text == 'C':
                button = tk.Button(self.root, text=text, font=('Arial', 14), command=self.clear_all)
            elif text == 'Del':
                button = tk.Button(self.root, text=text, font=('Arial', 14), command=self.delete_last_char)
            elif text == 'History':
                button = tk.Button(self.root, text=text, font=('Arial', 14), command=self.show_history)
            elif text == 'Matrices':
                button = tk.Button(self.root, text=text, font=('Arial', 14), command=self.show_matrix_operations)
            elif text in ('MC', 'MR', 'M+', 'M-'):
                button = tk.Button(self.root, text=text, font=('Arial', 14), command=lambda t=text: self.memory_operation(t))
            else:
                button = tk.Button(self.root, text=text, font=('Arial', 14), command=lambda t=text: self.entry.insert(tk.END, t))
            button.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

        for i in range(8):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(7):
            self.root.grid_rowconfigure(i, weight=1)

        self.root.geometry("600x500")  # Adjusted size for better fit

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
        expression = expression.replace('ln', 'math.log')
        expression = expression.replace('sin', 'math.sin')
        expression = expression.replace('cos', 'math.cos')
        expression = expression.replace('tan', 'math.tan')
        expression = expression.replace('abs', 'abs')
        expression = expression.replace('i', 'j')
        expression = expression.replace('^', '**')
        return expression

    def math_functions(self):
        return {
            'math': math,
            'cmath': cmath,
            'sp': sp,
            'np': np,
            'abs': abs,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'exp': math.exp,
            'log10': math.log10,
            'ln': math.log,
            'pi': math.pi,
            'e': math.e,
            'j': 1j
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

    def memory_operation(self, operation):
        if operation == 'MC':  # Clear Memory
            self.memory = 0
        elif operation == 'MR':  # Recall Memory
            self.entry.insert(tk.END, str(self.memory))
        elif operation == 'M+':  # Add to Memory
            try:
                value = float(self.entry.get())
                self.memory += value
            except ValueError:
                logging.error("Invalid value for memory addition")
        elif operation == 'M-':  # Subtract from Memory
            try:
                value = float(self.entry.get())
                self.memory -= value
            except ValueError:
                logging.error("Invalid value for memory subtraction")

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
        
        # Using a scrolled text box for large history
        history_window = tk.Toplevel(self.root)
        history_window.title("Calculation History")
        history_textbox = scrolledtext.ScrolledText(history_window, width=50, height=20, wrap=tk.WORD)
        history_textbox.insert(tk.END, history_text)
        history_textbox.configure(state='disabled')
        history_textbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        logging.info("Displayed history")

    def show_matrix_operations(self):
        matrix_window = tk.Toplevel(self.root)
        matrix_window.title("Matrix Operations")
        label = tk.Label(matrix_window, text="Matrix Operations (Addition, Subtraction, Multiplication, Inversion)")
        label.pack(pady=10)
        
        entry1 = tk.Entry(matrix_window, width=40)
        entry2 = tk.Entry(matrix_window, width=40)
        entry1.pack(pady=5)
        entry2.pack(pady=5)
        
        def evaluate_matrix_operation(operation):
            try:
                matrix1 = eval(entry1.get())
                matrix2 = eval(entry2.get())
                if operation == 'add':
                    result = np.add(matrix1, matrix2)
                elif operation == 'subtract':
                    result = np.subtract(matrix1, matrix2)
                elif operation == 'multiply':
                    result = np.dot(matrix1, matrix2)
                elif operation == 'invert':
                    result = np.linalg.inv(matrix1)
                messagebox.showinfo("Result", str(result))
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        add_button = tk.Button(matrix_window, text="Add", command=lambda: evaluate_matrix_operation('add'))
        subtract_button = tk.Button(matrix_window, text="Subtract", command=lambda: evaluate_matrix_operation('subtract'))
        multiply_button = tk.Button(matrix_window, text="Multiply", command=lambda: evaluate_matrix_operation('multiply'))
        invert_button = tk.Button(matrix_window, text="Invert", command=lambda: evaluate_matrix_operation('invert'))
        
        add_button.pack(side=tk.LEFT, padx=10, pady=10)
        subtract_button.pack(side=tk.LEFT, padx=10, pady=10)
        multiply_button.pack(side=tk.LEFT, padx=10, pady=10)
        invert_button.pack(side=tk.LEFT, padx=10, pady=10)

def main():
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
