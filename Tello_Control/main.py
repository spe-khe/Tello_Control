from TelloControl import Tello
import time

try:
    t = Tello("COM6", True)
    t.clear_matrix()
    print(t.get_battery())
    t.led(0, 255, 255)
    time.sleep(3)
    t.blink_led(255, 0, 0, 0, 255, 0, 5.5)
    t.print_matrix("Hello World", "r", 2.5)
except Exception as ex:
    del t
    raise ex
