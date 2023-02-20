from TelloControl import Tello
import time

t = Tello("COM6")  # Der Port muss ggfs. angepasst werden.
# t = Tello("COM6", True)  # Falls das Erweiterungsmodul benutzt wird, muss diese Zeile stattdessen verwendet werden
t.takeoff()  # Abheben
t.go_relative(100, 0, 0, 100)  # 100 cm mit Geschwindigkeit 100 nach vorne fliegen
bat = t.get_battery()  # Batteriestand abfragen
print(bat)
t.land()  # Landen
