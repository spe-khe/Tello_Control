from TelloControl import Tello
import time

# t = Tello("COM6")  # Der Port muss ggf. angepasst werden.
t = Tello("COM3")  # Falls das Erweiterungsmodul benutzt wird, muss diese Zeile stattdessen verwendet werden
while 1:
    print(t.get_battery())
