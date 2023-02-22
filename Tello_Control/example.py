from TelloControl import Tello
import time

# t = Tello("COM6")  # Der Port muss ggf. angepasst werden.
t = Tello("COM6", True)  # Falls das Erweiterungsmodul benutzt wird, muss diese Zeile stattdessen verwendet werden
while 1:
    dist = t.get_distance()
    if dist <= 300:
        t.led(255, 0, 0)
    elif dist >= 500:
        t.led(0, 255, 0)
    else:
        t.led(0, 0, 255)
