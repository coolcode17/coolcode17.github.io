import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox


class NonlinearEquation:
    def __init__(self, function_str: str):
        self.function_str = function_str
        try:
            self.function = lambda x: eval(function_str, {"x": x, "np": np})
        except Exception as e:
            raise ValueError(f"Ошибка в уравнении: {e}")

    def evaluate(self, x: np.ndarray) -> np.ndarray:
        try:
            return self.function(x)
        except Exception as e:
            raise ValueError(f"Ошибка вычисления для x = {x}: {e}")


class OneStepSecantMethod:
    def __init__(self, equation: NonlinearEquation):
        self.equation = equation

    def find_root(self, x0: float, x1: float, tolerance: float = 1e-15, max_iterations: int = 100):
        f_x0, f_x1 = self.equation.evaluate(x0), self.equation.evaluate(x1)
        iteration = 0
        while abs(f_x1) > tolerance and iteration < max_iterations:
            if f_x1 == f_x0:
                raise ValueError("Начальные значения функции совпадают.")
            x2 = x1 - f_x1 * (x1 - x0) / (f_x1 - f_x0)
            x0, x1, f_x0, f_x1 = x1, x2, f_x1, self.equation.evaluate(x2)
            iteration += 1
        if iteration == max_iterations:
            raise ValueError("Превышено максимальное количество итераций.")
        return x1, iteration, f_x1


def plot_function(equation: NonlinearEquation, a: float, b: float, roots=None, num_points: int = 1000):
    x = np.linspace(a, b, num_points)
    try:
        y = equation.evaluate(x)
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))
        return

    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='f(x)')
    plt.axhline(0, color='black', linewidth=0.5)
    if roots:
        for root, _, f_root in roots:
            plt.scatter(root, 0, color='red', zorder=5)
            plt.annotate(f"{f_root:.1e}", (root, 0), textcoords="offset points", xytext=(0, 10), ha='center')
    plt.grid(True)
    plt.legend()
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.title('График функции и корни')
    plt.show()


def check_log_conditions(function_str: str, a: float, b: float):
    if any(log in function_str for log in ['log', 'ln']) and (a <= 0 or b <= 0):
        raise ValueError("Для логарифмических функций a и b должны быть положительными.")


def find_all_roots(equation: NonlinearEquation, a: float, b: float, subintervals: int = 100, tolerance: float = 1e-15):
    roots = []
    x_vals = np.linspace(a, b, subintervals)
    secant = OneStepSecantMethod(equation)
    for i in range(len(x_vals) - 1):
        x0, x1 = x_vals[i], x_vals[i + 1]
        if equation.evaluate(x0) * equation.evaluate(x1) < 0:
            try:
                root, iterations, f_root = secant.find_root(x0, x1, tolerance)
                if abs(f_root) < tolerance:
                    if not any(abs(root - r[0]) < tolerance for r in roots):
                        roots.append((root, iterations, f_root))
            except ValueError:
                continue
    return roots


def calculate_roots():
    try:
        a, b = float(entry_a.get()), float(entry_b.get())
        function_str = entry_function.get()
        check_log_conditions(function_str, a, b)
        equation = NonlinearEquation(function_str)
        roots = find_all_roots(equation, a, b)
        result_text = "Корни:\n"
        for root, iterations, f_root in roots:
            result_text += f"x = {root:.15f}, итерации = {iterations}, f(x) ≈ {f_root:.15e}\n"
        result_label.config(text=result_text)
        plot_function(equation, a, b, roots)
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))


def plot_only_function():
    try:
        a, b = float(entry_a.get()), float(entry_b.get())
        function_str = entry_function.get()
        check_log_conditions(function_str, a, b)
        equation = NonlinearEquation(function_str)
        plot_function(equation, a, b)
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))


root_window = tk.Tk()
root_window.title("Метод секущих")

tk.Label(root_window, text="Введите уравнение f(x):").pack()
entry_function = tk.Entry(root_window)
entry_function.pack()

tk.Label(root_window, text="Введите a:").pack()
entry_a = tk.Entry(root_window)
entry_a.pack()

tk.Label(root_window, text="Введите b:").pack()
entry_b = tk.Entry(root_window)
entry_b.pack()

tk.Button(root_window, text="Найти корни", command=calculate_roots).pack()
tk.Button(root_window, text="Показать график функции", command=plot_only_function).pack()

result_label = tk.Label(root_window, text="")
result_label.pack()

root_window.mainloop()