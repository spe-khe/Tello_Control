from TelloControl import Tello
import time

# t = Tello("COM6")  # Der Port muss ggf. angepasst werden.
t = Tello("COM3")  # Falls das Erweiterungsmodul benutzt wird, muss diese Zeile stattdessen verwendet werden
t.throwfly()
while 1:
    t.go_relative(200, 0, 0, 100)
    t.rotate(180)
    print(t.get_battery())
