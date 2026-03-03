import krpc
import time
import _thread as thread

# import startLanding
import toLKO
import stageMonitor
from telemetry import DataRecorder


# =============================================================================
# 1. ПОДКЛЮЧЕНИЕ К ИГРЕ И ЗАПУСК МОНИТОРИНГА СТУПЕНЕЙ
# =============================================================================
connection = krpc.connect(name="Connection")
space_center = connection.space_center
vessel = space_center.active_vessel

print(f"ПОДКЛЮЧИЛСЯ: {vessel.name}")
print(f"МАССА: {vessel.mass:.1f} Т")

args = [vessel]

recorder = DataRecorder(vessel, space_center, interval=0.5)
recorder.start()

thread.start_new_thread(stageMonitor.monitor, tuple(args))


# =============================================================================
# 2. ВЗЛЁТ И ВЫХОД НА ОРБИТУ КЕРБИНА
# =============================================================================
print("Этап 1: Взлёт и выход на орбиту Кербина")
dv_lko = toLKO.engage(vessel, space_center, connection, 0.5)

recorder.stop()

ksp_times = [d["time"] - recorder.data[0]["time"] for d in recorder.data]
ksp_altitudes = [d["altitude"] for d in recorder.data]
ksp_speeds = [d["speed"] for d in recorder.data]
ksp_masses = [d["mass"] for d in recorder.data]
ksp_acc = [d["acceleration"] for d in recorder.data]

from theory import compare_graphics

compare_graphics(ksp_times, ksp_altitudes, ksp_speeds, ksp_masses,ksp_acc)


# сброс спутника
# if dv_lko != 0:
#     vessel.control.activate_next_stage()
#     vessel.control.activate_next_stage()
#     vessel.control.activate_next_stage()
#     vessel.control.activate_next_stage()
