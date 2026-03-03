import time
import matplotlib.pyplot as plt
from threading import Thread, Event


class DataRecorder:
    def __init__(self, vessel, space_center, interval=0.5):
        self.vessel = vessel
        self.space_center = space_center
        self.interval = interval
        self.data = []
        self.running = False
        self.thread = None
        self.stop_event = Event()
        self.start_time = None


    def start(self):
        self.running = True
        self.stop_event.clear()
        self.thread = Thread(target=self._record)
        self.thread.start()
        print("Запись телеметрии начата")

    def stop(self):
        self.running = False
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        print("Запись телеметрии остановлена")

    def _record(self):
        while not self.stop_event.is_set():
            try:
                current_time = self.space_center.ut
                
                # Если start_time не задан, используем первое полученное время
                if self.start_time is None:
                    self.start_time = current_time
                
                elapsed_time = current_time - self.start_time
                
                # Высота
                altitude = self.vessel.flight().mean_altitude
                
                # СКОРОСТЬ - используем орбитальную скорость
                orbit_frame = self.vessel.orbit.body.reference_frame
                speed = self.vessel.flight(orbit_frame).speed
                
                # Масса
                mass = self.vessel.mass
                # print('d',elapsed_time, altitude,speed, mass)

                self.data.append({
                    "time": elapsed_time,
                    "altitude": altitude,
                    "speed": speed,
                    "mass": mass
                })
                
                # Отладка - каждые 10 секунд
                if len(self.data) % 20 == 0:
                    print(f"Данные: t={elapsed_time:.1f}с, h={altitude/1000:.1f}км, v={speed:.1f}м/с, m={mass/1000:.1f}т")
                    
            except Exception as e:
                print(f"Ошибка при записи телеметрии: {e}")
                
            time.sleep(self.interval)