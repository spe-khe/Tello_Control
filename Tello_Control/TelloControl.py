import math

import serial
import time

_ANGULAR_SPEED = 360 / 15  # Grad pro Sekunde


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
        self.serial = serial.Serial(port=port, baudrate=115200, timeout=10)
        self.serial.flushInput()
        self.serial.flushOutput()
        wifi_id = 1
        if expansion:
            wifi_id = 2

        while True:
            self.serial.write(bytearray('!connect_' + str(wifi_id), encoding="utf_8"))
            try:
                self._await_response('!connected')
                break
            except TimeoutError:
                continue
            except ValueError as ex:
                if "Error" in str(ex.args[0]):
                    self.serial.flushInput()
                    continue
                else:
                    raise ValueError from ex

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
        self.serial.timeout = 10
        self._await_response('ok')

    def throwfly(self):
        """
        Werfe die Drohne innerhalb von 5 Sekunden, um sie in die Luft zu befördern
        """
        self.serial.write(b'throwfly')
        self.serial.timeout = 10
        print("Werfe den Quadrokopter in die Luft!")
        self._await_response('ok')

    def land(self):
        """
        Lande den Quadrokopter
        """
        self.serial.write(b'land')
        self.serial.timeout = 10
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
        self.serial.timeout = 2 + (math.sqrt(x ** 2 + y ** 2 + z ** 2) / speed * 4)
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

        self.serial.timeout = abs(angle) / _ANGULAR_SPEED * 2

        self._await_response('ok')

    def stop(self):
        """
        Stoppe die Bewegung der Drone
        """
        self.serial.write(b'throwfly')
        self.serial.timeout = 5
        msg = self._get_response()

    def flip(self, direction):
        """
        Führe ein Salto in die angegebene Richtung durch. Dazu muss der Akkustand mindestens bei 50 % sein.

        Parameters
        ----------
        direction: str
            'f', 'b', 'l' oder 'r' für vorwärts, rückwärts, links oder rechts
        """
        self.serial.write(bytearray('flip ' + direction, encoding="utf-8"))
        self.serial.timeout = 5
        self._await_response('ok')

    def get_battery(self):
        """
        Frage den Batteriestand des Quadrokopters ab

        Returns
        -------
        battery: int
            Batteriestand (0-100)
        """
        self.serial.timeout = 3
        for i in range(3):
            self.serial.write(b'battery?')
            try:
                msg = self._get_response()
                return int(msg)
            except TimeoutError:
                continue
        raise TimeoutError

    def get_speed(self):
        """
        Frage die aktuelle Geschwindigkeit des Quadrokopters ab

        Returns
        -------
        speed: float
            aktuelle Geschwindigkeit in cm/s
        """
        self.serial.timeout = 3
        for i in range(3):
            self.serial.write(b'speed?')
            try:
                msg = self._get_response()
                return float(msg)
            except TimeoutError:
                continue
        raise TimeoutError

    def get_distance(self):
        """
        Frage den Messwert des Entfernungsmessers ab. Dies ist nur möglich, wenn das Erweiterungsmodul mit dem
        Entfernungsmesser verbaut ist.

        Returns
        -------
        distance: int
            Entfernung in mm
        """
        self.serial.timeout = 3
        for i in range(3):
            self.serial.write(b'EXT tof?')
            try:
                msg = self._get_response()
                return int(msg[4:])
            except TimeoutError:
                continue
        raise TimeoutError

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
        self.serial.timeout = 1
        try:
            self._await_response("led ok")
        except TimeoutError:
            time.sleep(1)
            self.serial.reset_input_buffer()

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
        self.serial.timeout = 1
        try:
            self._await_response("led ok")
        except TimeoutError:
            time.sleep(1)
            self.serial.reset_input_buffer()

    def matrix_clear(self):
        """
        Lösche die Anzeige der LED-Matrix
        """
        self.serial.write(b'EXT mled sc')
        self.serial.timeout = 1
        try:
            self._await_response("matrix ok")
        except TimeoutError:
            time.sleep(1)
            self.serial.reset_input_buffer()

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
        self.serial.timeout = 1
        try:
            self._await_response("matrix ok")
        except TimeoutError:
            time.sleep(1)
            self.serial.reset_input_buffer()

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
        self.serial.timeout = 1
        try:
            self._await_response("matrix ok")
        except TimeoutError:
            time.sleep(1)
            self.serial.reset_input_buffer()

    def mp_go_absolute(self, x, y, z, speed, mission_pad_id):
        """
        Fliege zu der angegebenen Position im Koordinatensystem des angegebenen Mission-Pads.
        Dazu muss das Mission-Pad im erkennbaren Bereich unter der Drohne liegen oder bereits erkannt worden sein.

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
        mission_pad_id: int
            Nummer des Mission-Pads
        """
        self.serial.write(bytearray(f"go {x} {y} {z} {speed} m{mission_pad_id}", encoding='utf-8'))
        self.serial.timeout = 2 + (math.sqrt(x ** 2 + y ** 2 + z ** 2) / speed * 4)
        self._await_response('ok')

    def mp_jump(self, x, y, z, speed, yaw, mission_pad_id_1, mission_pad_id_2):
        """
        Fliege zum angegebenen Punkt relativ zum ersten Mission-Pad, dann suche dort das zweite Mission-Pad und
        bleibe 1 m darüber mit der angegebenen Rotation stehen.

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
        yaw: int
            Rotation relativ zum zweiten Mission-Pad
        mission_pad_id_1: int
            Nummer des ersten Mission-Pads
        mission_pad_id_2: int
            Nummer des zweiten Mission-Pads
        """
        self.serial.write(bytearray(f"jump {x} {y} {z} {speed} {yaw} m{mission_pad_id_1} m{mission_pad_id_2}", encoding='utf-8'))
        self.serial.timeout = 2 + (math.sqrt(x ** 2 + y ** 2 + z ** 2) / speed * 4)
        self._await_response('ok')

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
        msg = self._get_response()
        if expected not in str(msg):
            raise ValueError(msg)

    def _get_response(self):
        msg = self.serial.readline()
        print("TELLO: " + str(msg[:-2])[1:])
        if len(msg) <= 2:
            msg = self.serial.readline()
            print("TELLO: " + str(msg)[1:])
        if len(msg) <= 0 or msg[-1] != 10:
            raise TimeoutError
        return msg
