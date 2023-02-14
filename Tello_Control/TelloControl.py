import serial


class Tello:
    """Klasse für die Steuerung eines Tello Talent Quadrokopters"""

    def __init__(self, port: str):
        """
        Verbindung mit dem Quadrokopter herstellen
        :param port: Serieller Port, an den der Adapter angeschlossen ist
        """
        self.serial = serial.Serial(port=port, baudrate=115200)
        self.serial.flushInput()
        self.serial.flushOutput()
        self.serial.write(b'!connect')
        self._await_response('!connected')

    def writeCommand(self, message: str):
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
        self.serial.write(bytearray(f'cw {angle}',  encoding="utf-8"))
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
