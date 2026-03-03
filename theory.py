import numpy as np
import matplotlib.pyplot as plt

# from ksp_module import times_ksp, speeds_ksp, altitudes_ksp

# параметры
G = 6.67408 * 10 ** (-11)
M = 5.29 * 10**22
r = 6 * 10**5
dt = 0.1
total_time = 250
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
M2 = 12200

k = (M1 - M2) / 24
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
    if t < 24:
        return M1 - k*t
    else:
        return 11000


# давление атмосферы
def p_a(h):
    return p0 * np.exp(-h / H)


# плотность воздуха
def get_density(h):
    return 1.1 * np.exp(-h / H)


# считаем как меняется g, от высоты
def get_g(h):
    return G * M / (r + h) ** 2


# программа управления
def get_angle(h):
    h1 = 1000  # начало поворота
    h2 = 15000  # середина поворота
    h3 = 40000  # начало плавного выхода на 0
    h4 = 75000  # полная горизонталь (было 71000)

    if h < h1:
        return 90
    elif h < h2:
        progress = (h - h1) / (h2 - h1)
        # Нелинейное уменьшение: быстро вниз, потом плавно
        return 90 - 60 * (progress**1.5)
    elif h < h3:
        progress = (h - h2) / (h3 - h2)
        # От 30° до 10° линейно
        return 30 - 20 * progress  # 30° → 10°
    elif h < h4:
        # ПЛАВНЫЙ ПЕРЕХОД от 10° до 0° с использованием косинуса
        progress = (h - h3) / (h4 - h3)
        # Косинус дает очень плавное начало и конец перехода
        # 10° * cos(progress * π/2)
        return 12 * np.cos(progress * np.pi / 2)
    else:
        return 0


def get_thrust(t, h):
    if t < 24:
        thrust = Pn_1 - Sa_1 * p_a(h)
    # elif t < 26:
    #     return 0
    elif h < 45000:
        thrust = Pn_2 - Sa_2 * p_a(h)
    elif h > 45000 and h < 72000:
        thrust = 0
    elif h > 72000:
        thrust = (Pn_2 - Sa_2 * p_a(h)) * 0.4
    return max(0, thrust)


while t < total_time:
    # получаем тягу и угол
    m = get_m(t)
    angle_deg = get_angle(h)
    thrust = get_thrust(t, h)
    angle = np.radians(angle_deg)

    # разложение тяги на X и Y
    thrust_x = thrust * np.cos(angle)
    thrust_y = thrust * np.sin(angle)

    # сопротивление воздуха
    density = get_density(h)
    drag = 0.5 * density * v**2 * drag_coef * area

    # разложение сопротивления
    v_x = v * np.cos(angle)  # горизонтальная скорость
    v_y = v * np.sin(angle)
    drag_x = drag * np.cos(angle)
    drag_y = drag * np.sin(angle)

    # ускорение по осям
    a_x = (thrust_x - drag_x) / m
    a_y = (thrust_y - drag_y - m * get_g(h)) / m

    # общее ускорение
    a = np.sqrt(a_x**2 + a_y**2)

    # обновление скорости и высоты
    v += a*dt

    h += v * dt * np.sin(angle)




    t_data.append(t)
    h_data.append(h)
    v_data.append(v)
    m_data.append(a)
    t += dt
    # a_y = (thrust_y - drag_y - m * get_g(h)) / m
    if t < 30:
        print( round(t,2), round(a_y,2), round(thrust_y,2), round(drag_y,2),  round(m,2), round(get_g(h),2), round(get_density(h),2))
    


# График 1 Высота
def compare_graphics(times_ksp, h_ksp, speed_ksp):

    plt.figure(figsize=(10, 6))
    plt.plot(t_data, h_data, label="МАТ МОДЕЛЬ")
    plt.plot(times_ksp, h_ksp, label="ДАННЫЕ KSP")
    plt.legend()
    plt.xlabel("Время (с)")
    plt.ylabel("Высота (м)")
    plt.title("Высота ракеты")
    plt.grid(True)
    # График 2 Скорость
    plt.figure(figsize=(10, 6))
    plt.plot(t_data, v_data, label="МАТ МОДЕЛЬ")
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
