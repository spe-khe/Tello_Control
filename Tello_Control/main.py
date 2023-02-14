from TelloControl import Tello
import time

try:
    t = Tello("COM6")
    print(t.get_battery())
    t.takeoff()
    t.goRelative(50, 50, 50, 50)
    t.goRelative(-50, -50, -50, 50)
    t.rotate(90)
    t.flip("f")
    t.land()
    time.sleep(5)
    t.throwfly()
    t.land()
except Exception as ex:
    del t
    raise ex
