import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, find_peaks


def read_data(filename, target_digit, stop_value=None):
    result = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split(';')  # Разделение строки на части по точке с запятой
            if parts and int(parts[0]) == target_digit:  # Проверка соответствия цифре в первом столбце
                result.append(float(parts[2].replace(',', '.')))  # Преобразование строки в число
                if stop_value is not None and float(parts[1].replace(',', '.')) >= stop_value:
                    break
    print(result)
    return result


def fourier_transform(signal):
    test = np.fft.fft(signal) # Убрать половину, изменить частотные значения
    test[0] = 0
    # return np.fft.fft(signal)
    return test


def windowed_fourier_transform(signal, window='hann'):
    """Выполняет оконное преобразование Фурье для заданного сигнала."""
    # Выбор оконной функции
    if window == 'hann':
        window_func = np.hanning(len(signal))
    elif window == 'hamming':
        window_func = np.hamming(len(signal))
    elif window == 'blackman':
        window_func = np.blackman(len(signal))
    else:
        raise ValueError("Неверно указана оконная функция. Доступные варианты: 'hann', 'hamming', 'blackman'.")

    # Умножение сигнала на выбранную оконную функцию
    windowed_signal = signal * window_func
    test = np.fft.fft(windowed_signal)
    test[0] = 0

    # Выполнение преобразования Фурье
    # return np.fft.fft(windowed_signal)
    return test


def hilbert_transform(signal):
    """Выполняет преобразование Гильберта для заданного сигнала."""
    return hilbert(signal)


def analytical_hilbert_signal(signal):
    """Возвращает аналитический сигнал Гильберта."""
    analytic_signal = hilbert(signal)
    return analytic_signal


def hilbert_envelope_signal(signal):
    """Возвращает огибающую сигнала Гильберта."""
    return np.abs(analytical_hilbert_signal(signal))


def calculate_speed_of_wave(signal, dt, dx):
    hilbert_env = np.abs(hilbert(signal))
    peaks, _ = find_peaks(hilbert_env, distance=int(0.1 / dt))
    speeds = []
    for i in range(len(peaks) - 1):
        time_diff = (peaks[i + 1] - peaks[i]) * dt
        speed = dx / time_diff
        speeds.append(speed)
    return np.mean(speeds)


def calculate_slope(signal, dt, dx):
    hilbert_env = np.abs(hilbert(signal))
    peaks, _ = find_peaks(hilbert_env, distance=int(0.1 / dt))
    return (peaks[-1] - peaks[0]) * dx / (len(signal) * dt)


def calculate_epsilon(signal, dx, c):
    hilbert_env = np.abs(hilbert(signal))
    peaks, _ = find_peaks(hilbert_env)
    return 2 * np.pi * dx / (c * (peaks[-1] - peaks[0]))


def calculate_speed_of_medium(signal, dt):
    hilbert_env = np.abs(hilbert(signal))
    peaks, _ = find_peaks(hilbert_env)
    return np.mean(np.diff(peaks)) * dt


def plot_waveform_and_hodograph(signal, dx, dt, c):
    hilbert_env = np.abs(hilbert(signal))
    peaks, _ = find_peaks(hilbert_env)
    speeds = np.diff(peaks) * dx / dt
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(np.arange(len(signal)) * dt, signal)
    plt.xlabel('Время (с)')
    plt.ylabel('Амплитуда')
    plt.title('Форма волны')
    plt.subplot(1, 2, 2)
    plt.plot(speeds[:-1], speeds[1:], 'o-')
    plt.xlabel('Скорость на t (м/нс)')
    plt.ylabel('Скорость на t + dt (м/нс)')
    plt.title('Годограф')
    plt.show()


def main():
    # Пример сигнала
    signal = read_data("data.txt", 10, 50)
    # t = np.linspace(0, len(signal) - 1, len(signal))
    t = np.arange(0, len(signal) * 0.5, 0.5)

    # Выполнение преобразования Фурье
    frequency_domain_signal = fourier_transform(signal)
    # Выполнение оконного преобразования Фурье
    windowed_domain_signal = windowed_fourier_transform(signal, "blackman")

    # Выполнение преобразования Гильберта
    hilbert_domain_signal = hilbert_transform(signal)
    # Огибающая сигнала Гильберта
    hilbert_envelope_values = hilbert_envelope_signal(signal)

    # Построение графиков
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 1, 1)
    plt.plot(t, signal)
    plt.title('Сигнал')
    plt.xlabel('Время')
    plt.ylabel('Амплитуда')
    plt.show()

    plt.subplot(1, 1, 1)
    plt.plot(t, np.abs(frequency_domain_signal))
    plt.title('Преобразование Фурье')
    plt.xlabel('Частота')
    plt.ylabel('Амплитуда')
    plt.show()

    plt.subplot(1, 1, 1)
    plt.plot(t, np.abs(windowed_domain_signal))
    plt.title('Оконное преобразование Фурье')
    plt.xlabel('Частота')
    plt.ylabel('Амплитуда')
    plt.show()

    plt.subplot(2, 2, 1)
    plt.plot(t, hilbert_domain_signal)
    plt.title('Преобразование Гильберта')
    plt.xlabel('Время')
    plt.ylabel('Амплитуда')

    plt.subplot(2, 2, 2)
    plt.plot(t, hilbert_envelope_values)
    plt.title('Огибающая')
    plt.xlabel('Время')
    plt.ylabel('Амплитуда')

    plt.subplot(2, 1, 2)
    plt.plot(t, hilbert_domain_signal)
    plt.title('Преобразование Гильберта / Огибающая')
    plt.xlabel('Время')
    plt.ylabel('Амплитуда')

    plt.subplot(2, 1, 2)
    plt.plot(t, hilbert_envelope_values)
    plt.title('Преобразование Гильберта / Огибающая')
    plt.xlabel('Время')
    plt.ylabel('Амплитуда')

    plt.tight_layout()
    plt.show()

    # plt.tight_layout()
    # plt.show()

    signal = read_data("data.txt", 0)
    dt = 0.1  # Time step (s)
    dx = 1.0  # Distance step (m)
    c = 343  # Speed of sound in air (m/s)

    speed_of_wave = calculate_speed_of_wave(signal, dt, dx)
    slope = calculate_slope(signal, dt, dx)
    epsilon = calculate_epsilon(signal, dx, c)
    speed_of_medium = calculate_speed_of_medium(signal, dt)

    print("Скорость волны:", speed_of_wave, "м/нс")
    print("Уклон:", slope)
    print("Эпсилон среды:", epsilon)
    print("Средняя скорость:", speed_of_medium, "м/нс")

    plot_waveform_and_hodograph(signal, dx, dt, c)


if __name__ == "__main__":
    main()
