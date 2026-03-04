import krpc
from time import sleep

def engage(vessel, space_center, connection, ascentProfileConstant=1.15):
    vessel.control.rcs = True
    vessel.control.throttle = 1

    # Запоминаем начальную скорость (до манёвра)
    initial_speed = vessel.flight(vessel.orbit.body.reference_frame).speed

    apoapsisStream = connection.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')

    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_heading = 90
    # ЭТАП 1: Гравитационный разворот
    target_apoapsis = 75000
    shutdown_margin = 1500  
    while apoapsisStream() < target_apoapsis - shutdown_margin:
        # Расчёт целевого тангажа 
        k = 90 / (target_apoapsis ** ascentProfileConstant)
        targetPitch = 90 - k * (apoapsisStream() ** ascentProfileConstant)
        targetPitch = max(0, min(90, targetPitch))
        print(targetPitch)
        # print("Текущий целевой тангаж:", targetPitch, "при апогее", apoapsisStream())

        vessel.auto_pilot.target_pitch = targetPitch
        sleep(0.1)

    vessel.control.throttle = 0
    print("Двигатель выключен. Текущий апогей:", apoapsisStream())

    # ЭТАП 2: Ожидание подлёта к апогею
    timeToApoapsisStream = connection.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
    periapsisStream = connection.add_stream(getattr, vessel.orbit, 'periapsis_altitude')

    while timeToApoapsisStream() > 22:
        if timeToApoapsisStream() > 60:
            space_center.rails_warp_factor = 4
        else:
            space_center.rails_warp_factor = 0
        sleep(0.5)
    space_center.rails_warp_factor = 0
    
    # ЭТАП 3: Циркуляризация
    vessel.control.throttle = 0.5
    lastUT = space_center.ut
    lastTimeToAp = timeToApoapsisStream()
    delta_history = []

    while periapsisStream() < 70500:
        sleep(0.5)
        timeToAp = timeToApoapsisStream()
        UT = space_center.ut
        dt = UT - lastUT
        if dt < 0.001:
            continue
        delta = (timeToAp - lastTimeToAp) / dt

        delta_history.append(delta)
        if len(delta_history) > 5:
            delta_history.pop(0)
        smoothed_delta = sum(delta_history) / len(delta_history)

        print(f"Сглаженная оценка: {smoothed_delta:.3f}")

        if smoothed_delta < -0.3:
            vessel.control.throttle = min(1.0, vessel.control.throttle + 0.03)
        elif smoothed_delta < -0.1:
            vessel.control.throttle = min(1.0, vessel.control.throttle + 0.01)
        if smoothed_delta > 0.2:
            vessel.control.throttle = max(0.0, vessel.control.throttle - 0.03)
        elif smoothed_delta > 0:
            vessel.control.throttle = max(0.0, vessel.control.throttle - 0.01)

        vessel.control.throttle = max(0.05, min(1.0, vessel.control.throttle))

        lastTimeToAp = timeToAp
        lastUT = UT

    vessel.control.throttle = 0

    # Запись потраченного dv
    final_speed = vessel.flight(vessel.orbit.body.reference_frame).speed
    print("Апогей: ", apoapsisStream())
    print("Перигей: ", periapsisStream())
    print("Орбита достигнута!")
    print()
    vessel.control.activate_next_stage()
    sleep(2.1)
    vessel.control.activate_next_stage()
    sleep(2.1)
    vessel.control.activate_next_stage()
    sleep(2.1)
