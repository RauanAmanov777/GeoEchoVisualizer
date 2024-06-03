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


FILTERS = [
    FILTER_TRACE,
    HORIZONTAL_FILTER,
    MEDIAN_FILTER,
    LOWPASS_FILTER,
    HIGHPASS_FILTER,
    REVERT_FILTER,
]

TRANSFORMS = [
    CHOOSE_DAUBECHIES,
    CHOOSE_HAAR,
    FOURIER_TRANSFORM,
    WINDOWED_FOURIER_TRANSFORM,
    HILBERT_TRANSFORM,
    HILBERT_ENVELOPE_SIGNAL,
]


def choose_db():
    global walet
    walet = "db4"
    print("db1")


def choose_haar():
    global walet
    walet = "haar"
    print("haar")


def show_radiogram():
    global signals, index, filter, walet

    signal = signals[index]

    cleared_signal = filter(signal, wavelet=walet)


class GeoTrack:
    def __init__(self, distance, signals):
        self.distance = distance
        self.signals = signals
        
    def to_csv_row(self):
        """Convert the object attributes to a CSV row."""
        return [self.distance] + [x for x in self.signals] + [0, 0]


class SignalFile:
    def __init__(self, name, path):
        self.name = name
        self.path = path


def save_file():
    name = simpledialog.askstring("Сохранение", "Введите название трассы:")
    if not name:
        messagebox.showinfo("Info", "No filename provided!")
        return

    # Create the full path for the file
    filepath = ".\\saved\\" + name + ".csv"

    # Check if the file already exists
    if os.path.exists(filepath):
        overwrite = messagebox.askyesno(
            "Подтверждение", "Файл существует. Перезаписать?"
        )
        if not overwrite:
            return

    # Write some content to the file
    try:
        with open(filepath, "w", newline="", encoding="utf-16-le") as file:
            writer = csv.writer(
                file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )

            # Write the data
            for row in my_data:
                writer.writerow(row.to_csv_row())
        messagebox.showinfo("Успешно", "Файл успешно сохранён!")
        
        with open("menu.txt", 'a', encoding="utf-8") as file:
            file.write(f"\n{name}\t{filepath}")
            
        create_gui_with_buttons()
        open_menu.delete(0, 'end')
        for sf in signal_files:
            open_menu.add_command(
                label=sf.name, command=lambda path=sf.path: import_csv_data(path)
            )
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")


def import_csv_data(filename):
    global my_data
    my_data.clear()
    with open(filename, encoding="utf-16-le", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        data = list(reader)
        for row in data[:-1]:
            distance = int(row[0])
            signals = list(map(float, row[1:-2]))
            obj = GeoTrack(distance, signals)
            my_data.append(obj)

        draw_charts(my_data)


def create_gui_with_buttons():
    global signal_files
    signal_files.clear()
    # Read lines from the file
    with open("menu.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    for index, line in enumerate(lines):
        tokens = line.strip().split("\t")
        signal_file_name = tokens[0]
        signal_file_path = tokens[1]
        obj = SignalFile(signal_file_name, signal_file_path)
        signal_files.append(obj)


def draw_charts(data):
    # Clear previous data
    for widget in frame_unified.winfo_children():
        widget.destroy()

    lists_of_numbers = [obj.signals for obj in data]
    matrix_data = np.rot90(np.array(lists_of_numbers), k=-1)

    # Create heatmap
    fig1 = Figure(figsize=(5, 4), dpi=100)
    subplot1 = fig1.add_subplot(111)
    subplot1.imshow(
        matrix_data,
        cmap="gray_r",
        aspect="auto",
        interpolation="none",
    )

    # Create a frame for the charts
    frame_charts = tk.Frame(frame_unified)
    frame_charts.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    chart1 = FigureCanvasTkAgg(fig1, master=frame_charts)
    chart1.draw()
    chart1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create line chart
    fig2 = Figure(figsize=(5, 4), dpi=100)
    subplot2 = fig2.add_subplot(111)
    chart2 = FigureCanvasTkAgg(fig2, master=frame_charts)
    chart2.draw()
    chart2.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Frame for Listbox and Scrollbar
    frame_list_scroll = tk.Frame(root)
    frame_list_scroll.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

    # Frame for Listbox and Scrollbar, within the unified frame
    frame_list_scroll = tk.Frame(frame_unified)
    frame_list_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

    # Creating and placing the Listbox
    listbox = tk.Listbox(frame_list_scroll, height=20, width=20)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Creating Scrollbar
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


# This function is called whenever any checkbutton is toggled.
def checkbutton_handler(item, var):
    global walet, index
    if var.get():
        if item == CHOOSE_DAUBECHIES:
            choose_db()
        elif item == CHOOSE_HAAR:
            choose_haar()
        elif item == FILTER_TRACE:
            for trace in my_data:
                trace.signals = filter_trace(trace.signals, wavelet=walet)
        elif item == HORIZONTAL_FILTER:
            for trace in my_data:
                trace.signals = horizontal_filter(trace.signals, wavelet=walet)
        elif item == MEDIAN_FILTER:
            for trace in my_data:
                trace.signals = median_filter(trace.signals, wavelet=walet)
        elif item == LOWPASS_FILTER:
            for trace in my_data:
                trace.signals = lowpass_filter(trace.signals, wavelet=walet)
        elif item == HIGHPASS_FILTER:
            for trace in my_data:
                trace.signals = highpass_filter(trace.signals, wavelet=walet)
        elif item == REVERT_FILTER:
            for trace in my_data:
                trace.signals = revert_filter(trace.signals, wavelet=walet)
        elif item == FOURIER_TRANSFORM:
            for trace in my_data:
                trace.signals = np.abs(fourier_transform(trace.signals))
        elif item == WINDOWED_FOURIER_TRANSFORM:
            for trace in my_data:
                trace.signals = np.abs(
                    windowed_fourier_transform(trace.signals, "blackman")
                )
        elif item == HILBERT_TRANSFORM:
            for trace in my_data:
                trace.signals = np.abs(hilbert_transform(trace.signals))
        elif item == HILBERT_ENVELOPE_SIGNAL:
            for trace in my_data:
                trace.signals = np.abs(hilbert_envelope_signal(trace.signals))
        draw_charts(my_data)

    # Example action: Show a message box with checked items
    # if checked_items:
    #     messagebox.showinfo(
    #         "Checkout", "Checked out items: " + ", ".join(checked_items)
    #     )
    # else:
    #     messagebox.showinfo("Checkout", "No items were checked out.")


global walet
walet = "db4"
my_data = []

signal_files = []
create_gui_with_buttons()

# Set up the main window
root = tk.Tk()
root.title("GeoEcho Visualizer")
root.state("zoomed")

frame_unified = tk.Frame(root)
frame_unified.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a menu
menu_bar = Menu(root)
root.config(menu=menu_bar)

filters_menu = tk.Menu(menu_bar, tearoff=0)
transforms_menu = tk.Menu(menu_bar, tearoff=0)

# Add options to the menu
file_menu = Menu(filters_menu, tearoff=0)
open_menu = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Открыть", menu=open_menu)

for sf in signal_files:
    open_menu.add_command(
        label=sf.name, command=lambda path=sf.path: import_csv_data(path)
    )

file_menu.add_command(label="Сохранить", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Выход", command=root.quit)
menu_bar.add_cascade(label="Файл", menu=file_menu)

# Add the navigation menu to the main menu bar
menu_bar.add_cascade(label="Фильтры", menu=filters_menu)
menu_bar.add_cascade(label="Преобразования", menu=transforms_menu)

# create_gui_with_buttons()

# Initialize BooleanVars for each set of checkbuttons
check_vars_1 = [tk.IntVar() for _ in FILTERS]
check_vars_2 = [tk.IntVar() for _ in TRANSFORMS]

# Add checkable items to the first navigation menu
for item, var in zip(FILTERS, check_vars_1):
    filters_menu.add_checkbutton(
        label=item,
        variable=var,
        onvalue=1,
        offvalue=0,
        command=lambda item=item, var=var: checkbutton_handler(item, var),
    )

# Add checkable items to the second navigation menu
for item, var in zip(TRANSFORMS, check_vars_2):
    transforms_menu.add_checkbutton(
        label=item,
        variable=var,
        onvalue=1,
        offvalue=0,
        command=lambda item=item, var=var: checkbutton_handler(item, var),
    )

root.mainloop()