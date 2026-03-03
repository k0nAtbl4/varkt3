import numpy as np
import matplotlib.pyplot as plt

# from ksp_module import times_ksp, speeds_ksp, altitudes_ksp

# параметры
G = 6.67408 * 10 ** (-11)
M = 5.29 * 10**22
r = 6 * 10**5
dt = 0.1
total_time = 300
p0 = 101325
H = 5000
drag_coef = 0.4
area = 10

# начальные условия
t = 0
h = 0
x = 0
v = 0
v_x = 0
v_y = 0
curr_angle = 90
M1 = 26200  # масса после полного расхода топлива
M2 = 5800
k = (M1 - M2) / total_time
m = M1


Pn_1 = 908000

Pn_2 = 215000

Sa_1 = 4 * 0.29
Sa_2 = 0.46


v_data = []
m_data = []
h_data = []
t_data = []


# массовый расход
def get_m(t):
    return M1 - k * t


# давление атмосферы
def p_a(h):
    return p0 * np.exp(-h / H)


# плотность воздуха
def get_density(h):
    return 1.1 * np.exp(-h / H)


# считаем как меняется g, от высоты
def get_g(h):
    return G*M / (r + h) ** 2


# программа управления
def get_angle(h, v):
    GM = 3.5316 * (10**12)
    h_ap = ((GM) / (GM / ((r + h)) - ((v**2) / 2))) - r
    if h_ap < 0:
        return 90
    if h_ap > 75000:
        return 0
    angl = 90 * ((1 - (h_ap / 75000)) ** 1.15)
    return max(0, min(90, angl))


def get_thrust(t, h):
    if t < 24:
        thrust = Pn_1 - Sa_1 * p_a(h)
    else:
        thrust = Pn_2 - Sa_2 * p_a(h)
    return max(0, thrust)


while t < total_time:
    thrust = get_thrust(t, h)
    v = np.sqrt(v_x**2 + v_y**2)
    angle = np.radians(get_angle(h, v))  # вертикальная

    # разложение тяги на X и Y
    thrust_x = thrust * np.cos(angle)
    thrust_y = thrust * np.sin(angle)

    # сопротивление воздуха
    density = get_density(h)
    drag = 0.5 * density * v**2 * drag_coef * area

    # разложение сопротивления
    drag_x = drag * np.cos(angle) if v > 0 else 0
    drag_y = drag * np.sin(angle) if v > 0 else 0

    # ускорение по осям
    a_x = (thrust_x - drag_x) / m
    a_y = (thrust_y - drag_y - m * get_g(h)) / m

    # общее ускорение
    a = np.sqrt(a_x**2 + a_y**2)

    # обновление скорости и высоты
    h += v_y * dt

    v_x += a_x * dt
    v_y += a_y * dt
    curr_angle = np.degrees(np.arctan2(v_y, v_x))
    curr_angle = max(0, min(90, curr_angle))

    t_data.append(t)
    h_data.append(h)
    v_data.append(v)
    m_data.append(a)
    t += dt

    m = get_m(t)
    # Добавь в отладку:
    # if h > 35000 and h < 45000:
        # print(
            # f"  drag_y={drag_y:.0f}Н, thrust_y={thrust_y:.0f}Н, отношение={drag_y/thrust_y:.2f}, pa={p_a(h):.0f}"
        # )
    # if 35000 < h < 45000:
        # print(f"КРИТИЧЕСКИ: h={h/1000:.1f}км, угол={curr_angle:.1f}°, v={v:.0f}м/с, v_y={v_y:.0f}м/с")

# График 1 Высота
def compare_graphics(times_ksp, mass_ksp, speed_ksp):

    plt.figure(figsize=(10, 6))
    plt.plot(times, heights, label="МАТ МОДЕЛЬ")
    plt.plot(times_ksp, mass_ksp, label="ДАННЫЕ KSP")
    plt.legend()
    plt.xlabel("Время (с)")
    plt.ylabel("Высота (м)")
    plt.title("Высота ракеты")
    plt.grid(True)
    # График 2 Скорость
    plt.figure(figsize=(10, 6))
    plt.plot(times, velocities, label="МАТ МОДЕЛЬ")
    plt.plot(times_ksp, speed_ksp, label="ДАННЫЕ KSP")
    plt.legend()
    plt.xlabel("Время (с)")
    plt.ylabel("Скорость (м/с)")
    plt.title("Скорость ракеты")
    plt.grid(True)

    plt.tight_layout()
    plt.show()


plt.figure(figsize=(10, 6))
plt.plot(t_data, h_data, label="МАТ МОДЕЛЬ")
plt.plot([], [], label="ДАННЫЕ KSP")
plt.legend()
plt.xlabel("Время (с)")
plt.ylabel("Высота (м)")
plt.title("Высота ракеты")
plt.grid(True)
# График 2 Скорость
plt.figure(figsize=(10, 6))
plt.plot(t_data, v_data, label="МАТ МОДЕЛЬ")
plt.plot([], [], label="ДАННЫЕ KSP")
plt.legend()
plt.xlabel("Время (с)")
plt.ylabel("Скорость (м/с)")
plt.title("Скорость ракеты")
plt.grid(True)
plt.tight_layout()
plt.show()
