import serial
import time


class Tello:
    """Klasse für die Steuerung eines Tello Talent Quadrokopters"""

    def __init__(self, port, expansion=False):
        """
        Verbindung mit dem Quadrokopter herstellen

        Parameters
        ----------
        port: str
            serieller Port, an den der Adapter angeschlossen ist
        expansion: bool
            True, wenn das Erweiterungsmodul verbaut ist
        """
        self.serial = serial.Serial(port=port, baudrate=115200)
        self.serial.flushInput()
        self.serial.flushOutput()
        wifi_id = 1
        if expansion:
            wifi_id = 2
        self.serial.write(bytearray('!connect_' + str(wifi_id), encoding="utf_8"))
        self._await_response('!connected')
        time.sleep(0.5)
        self.serial.flushInput()
        self.serial.flushOutput()

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

    def throwfly(self):
        """
        Werfe die Drohne innerhalb von 5 Sekunden, um sie in die Luft zu befördern
        """
        self.serial.write(b'throwfly')
        print("Werfe den Quadrokopter in die Luft!")
        self._await_response('ok')

    def land(self):
        """
        Lande den Quadrokopter
        """
        self.serial.write(b'land')
        self._await_response('ok')

    def go_relative(self, x, y, z, speed):
        """
        Fliege in relativen Koordinaten

        Parameters
        ----------
        x: int
            x-Koordinate (-500...500)
        y: int
            y-Koordinate (-500...500)
        z: int
            z-Koordinate (-500...500)
        speed: int
            Geschwindigkeit (10-100)
        """
        self.serial.write(bytearray(f"go {x} {y} {z} {speed}", encoding='utf-8'))
        self._await_response('ok')

    def rotate(self, angle):
        """
        Drehe den Quadrokopter um den spezifizierten Winkel im Uhrzeigersinn

        Parameters
        ----------
        angle: int
            Winkel in Grad
        """
        self.serial.write(bytearray(f'cw {angle}', encoding="utf-8"))
        self._await_response('ok')

    def stop(self):
        """
        Stoppe die Bewegung der Drone
        """
        self.serial.write(b'throwfly')
        msg = self.serial.readline()

    def flip(self, direction):
        """
        Führe ein Salto in die angegebene Richtung durch. Dazu muss der Akkustand mindestens bei 50 % sein.

        Parameters
        ----------
        direction: str
            'f', 'b', 'l' oder 'r' für vorwärts, rückwärts, links oder rechts
        """
        self.serial.write(bytearray('flip ' + direction, encoding="utf-8"))
        self._await_response('ok')

    def get_battery(self):
        """
        Frage den Batteriestand des Quadrokopters ab

        Returns
        -------
        battery: int
            Batteriestand (0-100)
        """
        self.serial.write(b'battery?')
        msg = self.serial.readline()
        return int(msg)

    def get_speed(self):
        """
        Frage die aktuelle Geschwindigkeit des Quadrokopters ab

        Returns
        -------
        speed: float
            aktuelle Geschwindigkeit in cm/s
        """
        self.serial.write(b'speed?')
        msg = self.serial.readline()
        return float(msg)

    def get_distance(self):
        """
        Frage den Messwert des Entfernungsmessers ab. Dies ist nur möglich, wenn das Erweiterungsmodul mit dem
        Entfernungsmesser verbaut ist.

        Returns
        -------
        distance: int
            Entfernung in mm
        """
        self.serial.write(b'EXT tof?')
        msg = self.serial.readline()
        if len(msg) <= 2:
            msg = self.serial.readline()
        return int(msg[4:])

    def led(self, r: int, g: int, b: int):
        """
        Setze die Farbe der LED

        Parameters
        ----------
        r: int
            Rot-Wert der LED (0-255)
        g: int
            Grün-Wert der LED (0-255)
        b: int
            Blau-Wert der LED (0-255)
        """
        self.serial.write(bytearray(f"EXT led {r} {g} {b}", encoding="utf-8"))
        self._await_response("led ok")

    def led_blink(self, r1, g1, b1, r2, g2, b2, frequency):
        """
        Blinke die LED in zwei Farben

        Parameters
        ----------
        r1: int
            Rot-Wert der ersten Farbe (0-255)
        g1: int
            Grün-Wert der ersten Farbe (0-255)
        b1: int
            Blau-Wert der ersten Farbe (0-255)
        r2: int
            Rot-Wert der zeiten Farbe (0-255)
        g2: int
            Grün-Wert der zeiten Farbe (0-255)
        b2: int
            Blau-Wert der zeiten Farbe (0-255)
        frequency: float
            Blinkfrequenz (0.1-10)
        """
        self.serial.write(bytearray(f"EXT led bl {frequency} {r1} {g1} {b1} {r2} {g2} {b2}", encoding="utf-8"))
        self._await_response("led ok")

    def matrix_clear(self):
        """
        Lösche die Anzeige der LED-Matrix
        """
        self.serial.write(b'EXT mled sc')
        self._await_response("matrix ok")

    def matrix_print(self, message, color, freq, direction='l'):
        """
        Zeige einen Text auf der LED-Matrix an

        Parameters
        ----------
        message: str
            der anzuzeigende Text
        color: str
            Farbe des Textes: 'r', 'b' oder 'p' für Rot, Blau oder Violett
        freq: float
            Scroll-Geschwindigkeit (0.1-2.5)
        direction: str
            Scroll-Richtung: 'l'/'r'/'u'/'d' für links/rechts/hoch/runter
        """
        self.serial.write(bytearray(f"EXT mled {direction} {color} {freq} {message}", encoding="utf-8"))
        self._await_response("matrix ok")

    def matrix_print_char(self, char, color):
        """
        Zeige ein einzelnes Zeichen statisch auf der LED-Matrix an

        Parameters
        ----------
        char: str
            das anzuzeigende Zeichen
        color: str
            Farbe des Zeichens: 'r', 'b' oder 'p' für Rot, Blau oder Violett
        """
        self.serial.write(bytearray(f"EXT mled s {color} {char}", encoding="utf-8"))
        self._await_response("matrix ok")

    def write_command(self, message):
        """
        Sende einen Befehl direkt an den Quadrokopter bzw. den Controller

        Parameters
        ----------
        message: str
            der Befehl
        """
        self.serial.write(bytearray(message, encoding='utf-8'))

    def _await_response(self, expected):
        msg = self.serial.readline()
        print("TELLO: " + str(msg[:-2])[1:])
        if len(msg) <= 2:
            msg = self.serial.readline()
            print("TELLO: " + str(msg[:-2])[1:])
        if expected not in str(msg):
            raise Exception(msg)
