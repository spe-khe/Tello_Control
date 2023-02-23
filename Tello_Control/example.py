from TelloControl import Tello
import time

# t = Tello("COM6")  # Der Port muss ggf. angepasst werden.
t = Tello("COM3", True)  # Falls das Erweiterungsmodul benutzt wird, muss diese Zeile stattdessen verwendet werden
t.led(0,0,0)
t.takeoff()
dist = t.get_distance()
while dist >= 500:
    t.go_relative(40, 0, 0, 100)
    dist = t.get_distance()
    t.matrix_print(str(dist), "b", 2.5)
t.led_blink(255, 0, 0, 0, 0, 255, 10)
t.land()
