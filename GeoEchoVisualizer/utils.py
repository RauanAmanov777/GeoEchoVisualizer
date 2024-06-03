import numpy as np
import pywt

from scipy.signal import hilbert, find_peaks

def hilbert_transform(signal):
    """Выполняет преобразование Гильберта для заданного сигнала."""
    return hilbert(signal)

def filter_trace(trace, wavelet="db1", level=1):
    # Применяем вейвлет-преобразование
    coeffs = pywt.wavedec(trace, wavelet, level=level)

    # Получаем детали (coffs[1:]) и прибавляем среднее
    filtered_coeffs = [c - np.mean(c) for c in coeffs[1:]]

    # Обратное вейвлет-преобразование
    filtered_trace = pywt.waverec(filtered_coeffs, wavelet)

    return filtered_trace


def horizontal_filter(signal, wavelet="db1"):
    # Применяем прямое вейвлет-преобразование
    cA, cD = pywt.dwt(signal, wavelet)

    # Обнуляем детальные коэффициенты (горизонтальные)
    cD_filtered = [0] * len(
        cD
    )  # Здесь происходит обнуление всех детальных (горизонтальных) коэффициентов

    # Обратное вейвлет-преобразование с отфильтрованными коэффициентами
    reconstructed_signal = pywt.idwt(cA, cD_filtered, wavelet)

    return reconstructed_signal


def revert_filter(signal, wavelet="haar"):
    # Применение прямого вейвлет-преобразования
    cA, cD = pywt.dwt(signal, wavelet)

    # Фильтрация детальных коэффициентов (например, выбор низкочастотных)
    cD_filtered = [0] * len(
        cD
    )  # Здесь происходит обнуление всех детальных коэффициентов

    # Обратное вейвлет-преобразование с отфильтрованными коэффициентами
    reconstructed_signal = pywt.idwt(cA, cD_filtered, wavelet)

    return reconstructed_signal


# Полосовая фильтрация (выбор высокочастотных коэффициентов)
def highpass_filter(signal, wavelet="haar", level=8):
    # Применяем дискретное вейвлет-преобразование
    coeffs = pywt.wavedec(signal, wavelet, level=level)

    # Обнуляем коэффициенты в низкочастотных составляющих
    coeffs[0] *= 0

    # Обратное вейвлет-преобразование
    filtered_signal = pywt.waverec(coeffs, wavelet)

    return filtered_signal


def lowpass_filter(signal, wavelet="db1", level=8):
    # Применяем дискретное вейвлет-преобразование
    coeffs = pywt.wavedec(signal, wavelet, level=level)

    # Обнуляем коэффициенты в высокочастотных составляющих
    for i in range(1, len(coeffs)):
        coeffs[i] *= 0

    # Обратное вейвлет-преобразование
    filtered_signal = pywt.waverec(coeffs, wavelet)

    return filtered_signal


# Применение медианной фильтрации с помощью pywt
def median_filter(signal, level=8, wavelet="db1"):
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    coeffs_filt = list(coeffs)
    for i in range(1, len(coeffs)):
        magnitude = np.abs(coeffs[i])
        threshold = np.median(magnitude)
        if threshold == 0:
            coeffs_filt[i] = np.zeros_like(coeffs[i])  # Заменяем все значения на нули
        else:
            coeffs_filt[i] = pywt.threshold(coeffs[i], threshold, mode="soft")
    reconstructed_signal = pywt.waverec(coeffs_filt, wavelet)
    return reconstructed_signal


def haar(signals: [], level=8, wavelet="haar"):
    coeffs = pywt.wavedec(signals, wavelet, level=level)

    # Удаление шумовых коэффициентов
    threshold = 0.03  # Порог отсечения

    coeffs_thresholded = [pywt.threshold(c, threshold, mode="soft") for c in coeffs]

    # Вейвлет-обратное преобразование
    return pywt.waverec(coeffs_thresholded, wavelet)


def dobeshi(signals: [], level=8, wavelet="db1"):
    coeffs = pywt.wavedec(signals, wavelet, level=level)

    # Удаление шумовых коэффициентов
    threshold = 0.03  # Порог отсечения

    coeffs_thresholded = [pywt.threshold(c, threshold, mode="soft") for c in coeffs]

    # Вейвлет-обратное преобразование
    return pywt.waverec(coeffs_thresholded, wavelet)


def resize(signal):
    values_array = np.array(signal)

    return (values_array - np.min(values_array)) / (
        np.max(values_array) - np.min(values_array)
    )


def fourier_transform(signal):
    fft = np.fft.fft(signal)[:len(signal) // 2 + 1]
    fft[0] = 0
    amplitude_spectrum = 2.0 / len(signal) * np.abs(fft[:len(signal) // 2])
    
    return amplitude_spectrum 


def windowed_fourier_transform(signal, window="hann"):
    """Выполняет оконное преобразование Фурье для заданного сигнала."""
    # Выбор оконной функции
    if window == "hann":
        window_func = np.hanning(len(signal))
    elif window == "hamming":
        window_func = np.hamming(len(signal))
    elif window == "blackman":
        window_func = np.blackman(len(signal))
    else:
        raise ValueError(
            "Неверно указана оконная функция. Доступные варианты: 'hann', 'hamming', 'blackman'."
        )

    # Умножение сигнала на выбранную оконную функцию
    windowed_signal = signal * window_func
    wfft = np.fft.fft(windowed_signal)
    wfft[0] = 0
    
    amplitude_spectrum = 2.0 / len(signal) * np.abs(wfft[:len(signal) // 2])

    # Выполнение преобразования Фурье
    # return np.fft.fft(windowed_signal)
    return amplitude_spectrum

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