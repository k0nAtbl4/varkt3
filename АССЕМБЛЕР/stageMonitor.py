import krpc
from time import sleep


def monitor(vessel):
    """
    Функция, предназначенная для запуска в отдельном потоке.
    Постоянно отслеживает количество топлива (жидкого и твердого) в текущей ступени.
    Когда топливо заканчивается, автоматически активирует следующую ступень.
    """

    # Небольшая задержка перед началом мониторинга,
    # чтобы дать основному скрипту время на инициализацию и старт.
    # sleep(3)
    fuels = [0, 1500, 720] 
    eng_id = 0
    delta1 = vessel.resources_in_decouple_stage(5, False).amount("SolidFuel")
    delta2 = vessel.resources_in_decouple_stage(-1, False).amount("LiquidFuel")
    flag = False

    start_altitude = vessel.flight().surface_altitude
    print(f"Стартовая высота: {start_altitude:.1f} м")
    # Бесконечный цикл мониторинга (поток работает всё время полёта)
    while True:
        print("ВЫСОТА: ", vessel.flight().surface_altitude - start_altitude)
        n1 = vessel.resources_in_decouple_stage(5, False).amount("SolidFuel")
        n2 = vessel.resources_in_decouple_stage(-1, False).amount("LiquidFuel")
        if eng_id == 1:
            fuels[1] -= abs(n1 - delta1)
        if eng_id > 1:
            fuels[eng_id] -= abs(n2 - delta2)
        delta1 = n1
        delta2 = n2

        if flag == False and fuels[2] < 180.0:
            flag = True
            vessel.control.activate_next_stage()
        if fuels[eng_id] < 0.05: 
            eng_id += 1
            vessel.control.activate_next_stage()
            if eng_id == 2:
                vessel.control.activate_next_stage()
            if eng_id == 3:
                vessel.control.activate_next_stage()
                vessel.control.activate_next_stage()
                vessel.control.activate_next_stage()
                break

        # Небольшая пауза, чтобы не нагружать процессор частыми проверками
        sleep(0.2)
