import serial


class Tello:
    """Klasse für die Steuerung eines Tello Talent Quadrokopters"""

    def __init__(self, port: str, expansion: bool = False):
        """
        Verbindung mit dem Quadrokopter herstellen
        :param port: serieller Port, an den der Adapter angeschlossen ist
        :param expansion: True, wenn das Erweiterungsmodul verbaut ist
        """
        self.serial = serial.Serial(port=port, baudrate=115200)
        self.serial.flushInput()
        self.serial.flushOutput()
        wifi_id = 1
        if expansion:
            wifi_id = 2
        self.serial.write(bytearray('!connect_' + str(wifi_id), encoding="utf_8"))
        self._await_response('!connected')

    def writeCommand(self, message: str):
        """
        Sende einen Befehl direkt an den Quadrokopter bzw. de Controller
        :param message: der Befehl
        """
        self.serial.write(bytearray(message, encoding='utf-8'))

    def goRelative(self, x: int, y: int, z: int, speed: int):
        """
        Fliege in relativen Koordinaten
        :param x: x-Koordinate (-500...500)
        :param y: y-Koordinate (-500...500)
        :param z: z-Koordinate (-500...500)
        :param speed: Geschwindigkeit (10-100)
        """
        self.serial.write(bytearray(f"go {x} {y} {z} {speed}", encoding='utf-8'))
        self._await_response('ok')

    def __del__(self):
        """
        Destruktor-Methode, schließt der seriellen Port
        """
        self.serial.close()

    def takeoff(self):
        """
        Hebe ab
        """
        self.serial.write(b'takeoff')
        self._await_response('ok')

    def rotate(self, angle: int):
        """
        Drehe den Quadrokopter um den spezifizierten Winkel im Uhrzeigersinn
        :param angle: Winkel in Grad
        """
        self.serial.write(bytearray(f'cw {angle}', encoding="utf-8"))
        self._await_response('ok')

    def flip(self, direction: str):
        """
        Führe ein Salto in die angegebene Richtung durch
        :param direction: 'f', 'b', 'l' oder 'r' für vorwärts, rückwärts, links oder rechts
        """
        self.serial.write(bytearray('flip ' + direction, encoding="utf-8"))
        self._await_response('ok')

    def land(self):
        """
        Lande den Quadrokopter
        """
        self.serial.write(b'land')
        self._await_response('ok')

    def throwfly(self):
        """
        Werfe die Drohne innerhalb von 5 Sekunden, um sie in die Luft zu befördern
        """
        self.serial.write(b'throwfly')
        print("Werfe den Quadrokopter in die Luft!")
        self._await_response('ok')

    def _await_response(self, expected: str):
        msg = self.serial.readline()
        print(msg)
        if len(msg) <= 2:
            msg = self.serial.readline()
        if expected not in str(msg):
            raise Exception(msg)

    def stop(self):
        """
        Stoppe die Bewegung der Drone
        """
        self.serial.write(b'throwfly')
        msg = self.serial.readline()

    def get_speed(self):
        """
        Frage die aktuelle Geschwindigkeit des Quadrokopters an
        :return: aktuelle Geschwindigkeit in cm/s
        """
        self.serial.write(b'speed?')
        msg = self.serial.readline()
        return float(msg)

    def get_battery(self):
        """
        Frage den Batteriestand des Quadrokopters an
        :return: Batteriestand (0-100)
        """
        self.serial.write(b'battery?')
        msg = self.serial.readline()
        return int(msg)

    def get_distance(self):
        """
        Frage den Messwert des Entfernungsmessers ab. Dies ist nur möglich, wenn das Erweiterungsmodul mit dem
        Entfernungsmesser verbaut ist.
        :return: Entfernung in mm
        """
        self.serial.write(b'EXT tof?')
        msg = self.serial.readline()
        if len(msg) <= 2:
            msg = self.serial.readline()
        return int(msg[4:])

    def led(self, r: int, g: int, b: int):
        """
        Setze die Farbe der LED
        :param r: Rot-Wert der LED (0-255)
        :param g: Grün-Wert der LED (0-255)
        :param b: Blau-Wert der LED (0-255)
        """
        self.serial.write(bytearray(f"EXT led {r} {g} {b}", encoding="utf-8"))
        self._await_response("led ok")

    def blink_led(self, r1: int, g1: int, b1: int, r2: int, g2: int, b2: int, frequency: float):
        """
        Blinke die LED in zwei Farben
        :param r1: Rot-Wert der ersten Farbe (0-255)
        :param g1: Grün-Wert der ersten Farbe (0-255)
        :param b1: Blau-Wert der ersten Farbe (0-255)
        :param r2: Rot-Wert der zeiten Farbe (0-255)
        :param g2: Grün-Wert der zeiten Farbe (0-255)
        :param b2: Blau-Wert der zeiten Farbe (0-255)
        :param frequency: Blinkfrequenz (0.1-10)
        """
        self.serial.write(bytearray(f"EXT led bl {frequency} {r1} {g1} {b1} {r2} {g2} {b2}", encoding="utf-8"))
        self._await_response("led ok")

    def print_matrix(self, message: str, color: str, freq: float, direction: str = 'l'):
        """
        Zeige einen Text auf der LED-Matrix an
        :param message: der anzuzeigende Text
        :param color: Farbe des Textes: 'r', 'b' oder 'p' für Rot, Blau oder Violett
        :param freq: Scroll-Geschwindigkeit (0.1-2.5)
        :param direction: Scroll-Richtung: 'l'/'r'/'u'/'d' für links/rechts/hoch/runter
        """
        self.serial.write(bytearray(f"EXT mled {direction} {color} {freq} {message}", encoding="utf-8"))
        self._await_response("matrix ok")

    def clear_matrix(self):
        """
        Lösche die Anzeige der LED-Matrix
        """
        self.serial.write(b'EXT mled sc')
        self._await_response("matrix ok")

    def print_char(self, char: str, color: str):
        """
        Zeige ein einzelnes Zeichen statisch auf der LED-Matrix an
        :param char: das anzuzeigende Zeichen
        :param color: Farbe des Zeichens: 'r', 'b' oder 'p' für Rot, Blau oder Violett
        """
        self.serial.write(bytearray(f"EXT mled s {color} {char}", encoding="utf-8"))
        self._await_response("matrix ok")
