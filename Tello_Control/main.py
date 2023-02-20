from TelloControl import Tello
import time

try:
    t = Tello("COM6", True)
    t.matrix_clear()
    """t.takeoff()
    while 1:
        bat = t.get_battery()
        print(bat)
        t.matrix_print(str(bat)+ "--", "r", 2.5)
        t.go_relative(0, 0, 100, 100)

        bat = t.get_battery()
        print(bat)
        t.matrix_print(str(bat)+"--", "r", 2.5)
        t.go_relative(0, 0, -100, 100)"""


except Exception as ex:
    del t
    raise ex
