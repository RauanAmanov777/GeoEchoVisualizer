import copy
import tkinter as tk
from tkinter import Menu
from tkinter import simpledialog, Menu
from tkinter import messagebox
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from utils import *

FILTER_TRACE = "Вычитание среднего"
HORIZONTAL_FILTER = "Горизонтальный фильтр"
MEDIAN_FILTER = "Медианный фильтр"
LOWPASS_FILTER = "Режекторная фильтрация"
HIGHPASS_FILTER = "Полосовая фильтрация"
REVERT_FILTER = "Обратная фильтрация"
CHOOSE_DAUBECHIES = "Вейвлет Добеши"
CHOOSE_HAAR = "Вейвлет Хаара"
FOURIER_TRANSFORM = "Преобразование Фурье"
WINDOWED_FOURIER_TRANSFORM = "Оконное преобразование Фурье"
HILBERT_TRANSFORM = "Преобразование Гильберта"
HILBERT_ENVELOPE_SIGNAL = "Огибающая сигнала Гильберта"

# Фильтры
FILTERS = [
    FILTER_TRACE,
    HORIZONTAL_FILTER,
    MEDIAN_FILTER,
    LOWPASS_FILTER,
    HIGHPASS_FILTER,
    REVERT_FILTER,
    CHOOSE_DAUBECHIES,
    CHOOSE_HAAR,
]

# Преобразования
TRANSFORMS = [
    FOURIER_TRANSFORM,
    WINDOWED_FOURIER_TRANSFORM,
    HILBERT_TRANSFORM,
    HILBERT_ENVELOPE_SIGNAL,
]

# Выбран вейвлет Добеши
def choose_db():
    global walet
    walet = "db4"
    print("db1")

# Выбран вейвлет Хаара
def choose_haar():
    global walet
    walet = "haar"
    print("haar")

# Класс трасса радарограммы
class GeoTrack:
    # Конструктор класса
    def __init__(self, distance, signals):
        self.distance = distance # Дистанция
        self.signals = signals # Сигналы
        
    def to_csv_row(self): # Преобразование атрибутов объекта в строку CSV
        """Convert the object attributes to a CSV row."""
        return [self.distance] + [x for x in self.signals] + [0, 0]


# Класс файла радарограммы
class SignalFile:
    def __init__(self, name, path):
        self.name = name # Название
        self.path = path # Путь к файлу

# Функция для сохранения файла с обработанной радарограммой
def save_file():
    name = simpledialog.askstring("Сохранение", "Введите название трассы:")
    if not name:
        messagebox.showinfo("Info", "No filename provided!")
        return

    # Формирование полного пути к файлу
    filepath = ".\\saved\\" + name + ".csv"

    # Проверка существует ли файл
    if os.path.exists(filepath):
        overwrite = messagebox.askyesno(
            "Подтверждение", "Файл существует. Перезаписать?"
        )
        if not overwrite:
            return

    # Запись данных радарограммы в файл
    try:
        with open(filepath, "w", newline="", encoding="utf-16-le") as file:
            writer = csv.writer(
                file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
                        
            for row in copy_list:
                writer.writerow(row.to_csv_row())
        messagebox.showinfo("Успешно", "Файл успешно сохранён!")
        
        with open("menu.txt", 'a', encoding="utf-8") as file:
            file.write(f"\n{name}\t{filepath}")
            
        read_menu_radarogram_file_paths()
        open_menu.delete(0, 'end')
        for sf in signal_files:
            open_menu.add_command(
                label=sf.name, command=lambda path=sf.path: import_csv_data(path)
            )
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

#  Функция для импорта данных из CSV файла
def import_csv_data(filename):
    global my_data, copy_list
    copy_list.clear()
    my_data.clear()
    with open(filename, encoding="utf-16-le", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        data = list(reader)
        for row in data[:-1]:
            distance = int(row[0])
            signals = list(map(float, row[1:-2]))
            obj = GeoTrack(distance, signals)
            my_data.append(obj)
            copy_list.append(obj)

        draw_charts(my_data)


def read_menu_radarogram_file_paths():
    global signal_files
    signal_files.clear()
    # Чтение путей к файлам радарограмм
    with open("menu.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    for index, line in enumerate(lines):
        tokens = line.strip().split("\t")
        signal_file_name = tokens[0]
        signal_file_path = tokens[1]
        obj = SignalFile(signal_file_name, signal_file_path)
        signal_files.append(obj)


# Рисование графиков
def draw_charts(data):
    # Удаление предыдущих данных
    for widget in frame_unified.winfo_children():
        widget.destroy()

    lists_of_numbers = [obj.signals for obj in data]
    matrix_data = np.rot90(np.array(lists_of_numbers), k=-1)

    # Создание графика профиля радарограммы
    fig1 = Figure(figsize=(5, 4), dpi=100)
    subplot1 = fig1.add_subplot(111)
    subplot1.imshow(
        matrix_data,
        cmap="gray_r",
        aspect="auto",
        interpolation="none",
    )

    # Создание frame для графиков
    frame_charts = tk.Frame(frame_unified)
    frame_charts.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    chart1 = FigureCanvasTkAgg(fig1, master=frame_charts)
    chart1.draw()
    chart1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Создание графика прямой
    fig2 = Figure(figsize=(5, 4), dpi=100)
    subplot2 = fig2.add_subplot(111)
    chart2 = FigureCanvasTkAgg(fig2, master=frame_charts)
    chart2.draw()
    chart2.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Frame для Listbox и Scrollbar
    frame_list_scroll = tk.Frame(root)
    frame_list_scroll.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

    # Frame для Listbox и Scrollbar, внутри объединённого frame
    frame_list_scroll = tk.Frame(frame_unified)
    frame_list_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

    # Создание и размещение Listbox
    listbox = tk.Listbox(frame_list_scroll, height=20, width=20)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Создание scrollbar
    scrollbar = tk.Scrollbar(frame_list_scroll, orient="vertical")
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    listbox.config(yscrollcommand=scrollbar.set)

    # Привязка события выбора элемента к функции обновления графика

    # Добавление элементов в listbox
    for index, _ in enumerate(data):
        listbox.insert(tk.END, index)

    # Функция для обновления графика
    def update_graph(event):
        global index
        subplot2.clear()
        # Move the left and bottom spines to x = 0 and y = 0, respectively.
        subplot2.spines["left"].set_position(("data", 0))
        subplot2.spines["bottom"].set_position(("data", 0))
        # Hide the top and right spines.
        subplot2.spines["top"].set_visible(False)
        subplot2.spines["right"].set_visible(False)

        # Draw arrows (as black triangles: ">k"/"^k") at the end of the axes.  In each
        # case, one of the coordinates (0) is a data coordinate (i.e., y = 0 or x = 0,
        # respectively) and the other one (1) is an axes coordinate (i.e., at the very
        # right/top of the axes).  Also, disable clipping (clip_on=False) as the marker
        # actually spills out of the axes.
        subplot2.plot(
            1, 0, ">k", transform=subplot2.get_yaxis_transform(), clip_on=False
        )
        subplot2.plot(
            0, 1, "^k", transform=subplot2.get_xaxis_transform(), clip_on=False
        )
        selection = listbox.curselection()
        if selection:
            index = selection[0]
            numbers = data[index].signals
            subplot2.plot(numbers)
            fig2.canvas.draw_idle()

    listbox.bind("<<ListboxSelect>>", update_graph)

# Эта функция будет вызываться при нажатии кнопки "Применить".
# Проверка состояния применённых фильтров и преобразований, и выполнение соответствующих действий.
def checkout():
    global walet, index, copy_list

    checked_items = []
    copy_list = copy.deepcopy(my_data)
    for item, var in zip(FILTERS, check_vars_1):
        if var.get() == 1:  # Если элемент отмечен
            if item == CHOOSE_DAUBECHIES:
                choose_db() # Выбран вейвлет Добеши
            elif item == CHOOSE_HAAR:
                choose_haar() # Выбран вейвлет Хаара
            elif item == FILTER_TRACE: # Вычитание среднего
                for trace in copy_list:
                    trace.signals = filter_trace(trace.signals, wavelet=walet)
            elif item == HORIZONTAL_FILTER: # Горизонтальный фильтр
                for trace in copy_list:
                    trace.signals = horizontal_filter(trace.signals, wavelet=walet)
            elif item == MEDIAN_FILTER: # Медианный фильтр
                for trace in copy_list:
                    trace.signals = median_filter(trace.signals, wavelet=walet)
            elif item == LOWPASS_FILTER: # Режекторная фильтрация
                for trace in copy_list:
                    trace.signals = lowpass_filter(trace.signals, wavelet=walet)
            elif item == HIGHPASS_FILTER: # Полосовая фильтрация
                for trace in copy_list:
                    trace.signals = highpass_filter(trace.signals, wavelet=walet)
            elif item == REVERT_FILTER: # Обратная фильтрация
                for trace in copy_list:
                    trace.signals = revert_filter(trace.signals, wavelet=walet)
                    
    for item, var in zip(TRANSFORMS, check_vars_2):
        if var.get() == 1:  # Если элемент отмечен
            if item == FOURIER_TRANSFORM: # Преобразование Фурье
                for trace in copy_list:
                    trace.signals = np.abs(fourier_transform(trace.signals))
            elif item == WINDOWED_FOURIER_TRANSFORM: # Оконное преобразование Фурье
                for trace in copy_list:
                    trace.signals = np.abs(
                        windowed_fourier_transform(trace.signals, "blackman")
                    )
            elif item == HILBERT_TRANSFORM: # Преобразование Гильберта
                for trace in copy_list:
                    trace.signals = np.abs(hilbert_transform(trace.signals))
            elif item == HILBERT_ENVELOPE_SIGNAL: # Огибающая сигнала Гильберта
                for trace in copy_list:
                    trace.signals = np.abs(hilbert_envelope_signal(trace.signals))

    draw_charts(copy_list) # Рисование графиков

global walet # Глобальная переменная для хранения выбранного вейвлета
walet = "db4"
my_data = [] # Список трасс радарограммы
copy_list = [] # Список преобразованнных трасс радарограммы

signal_files = [] # Список файлов радарограмм
read_menu_radarogram_file_paths() # Чтение путей к файлам радарограмм

# Настройка главного окна
root = tk.Tk()
root.title("GeoEcho Visualizer")
root.state("zoomed")

frame_unified = tk.Frame(root)
frame_unified.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Создание меню
menu_bar = Menu(root)
root.config(menu=menu_bar)

filters_menu = tk.Menu(menu_bar, tearoff=0)
transforms_menu = tk.Menu(menu_bar, tearoff=0)

# Добавление опций в меню
file_menu = Menu(filters_menu, tearoff=0)
open_menu = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Открыть", menu=open_menu)

for sf in signal_files: # Добавление файлов радарограмм в меню
    open_menu.add_command(
        label=sf.name, command=lambda path=sf.path: import_csv_data(path)
    )

file_menu.add_command(label="Сохранить", command=save_file) # Сохранение файла
file_menu.add_separator()
file_menu.add_command(label="Выход", command=root.quit) # Выход
menu_bar.add_cascade(label="Файл", menu=file_menu)

# Добавление навигационного меню в главное меню
menu_bar.add_cascade(label="Фильтры", menu=filters_menu)
menu_bar.add_cascade(label="Преобразования", menu=transforms_menu)
menu_bar.add_command(label="Применить", command=checkout)

# Инициализация BooleanVars для каждого элемента из списков фильтров и преобразований
check_vars_1 = [tk.IntVar() for _ in FILTERS]
check_vars_2 = [tk.IntVar() for _ in TRANSFORMS]

# Добавление отмечаемых элементов для навигационного меню с фильтрами
for item, var in zip(FILTERS, check_vars_1):
    filters_menu.add_checkbutton(label=item, variable=var, onvalue=1, offvalue=0)    

# Добавление отмечаемых элементов для навигационного с преобразованиями
for item, var in zip(TRANSFORMS, check_vars_2):
    transforms_menu.add_checkbutton(label=item, variable=var, onvalue=1, offvalue=0)
    
root.mainloop()