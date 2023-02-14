#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <string.h>

// Set WiFi credentials
#define WIFI_SSID "TELLO-638AB9"
#define WIFI_PASS ""
#define UDP_RX_PORT 8890
#define UDP_TX_PORT 8889
IPAddress ip(192, 168, 10, 1);

// Error Codes
#define CONN_ERR 1
#define E_LAND 2
#define E_STOP 3

// UDP
WiFiUDP UDP;
char packet[255];
char message[255];
bool emergency = false;
bool land = false;

bool heartbeat = false;


unsigned long int lastMillis = 0;

void IntCallbackEmergency() {
	emergency = true;
}
void IntCallbackLand() {
	land = true;
}

void sendUPD(const char* message) {
	if (WiFi.status() != WL_CONNECTED)
	{
		throw CONN_ERR;
	}
	UDP.beginPacket(ip, UDP_TX_PORT);
	UDP.write(message);
	UDP.endPacket();
}

void setup() {
	// Setup serial port
	Serial.begin(115200);
	Serial.println();
	delay(500);

	// Begin WiFi
	
	pinMode(D2, INPUT_PULLUP);
	attachInterrupt(digitalPinToInterrupt(D2), IntCallbackEmergency, FALLING);
	pinMode(D3, INPUT_PULLUP);
	attachInterrupt(digitalPinToInterrupt(D3), IntCallbackLand, FALLING);

}

void loop() {
	try
	{
		if (emergency) {
			for (int i = 0; i <= 3; i++) {
				sendUPD("emergency");
			}
			emergency = false;
			throw E_STOP;
		}
		else if (land)
		{
			for (int i = 0; i <= 3; i++) {
				sendUPD("stop");
			}
			for (int i = 0; i <= 3; i++) {
				sendUPD("land");
			}

			land = false;
			throw E_LAND;
		}

		// If packet received...
		int packetSize = UDP.parsePacket();
		if (packetSize) {
			int len = UDP.read(packet, 255);
			if (len > 0)
			{
				packet[len] = '\0';
			}
			if (len == 2 && heartbeat)
			{
				heartbeat = false;
				lastMillis = millis();
			}
			else
			{
				Serial.println(packet);
				lastMillis = millis();
			}

		}

		if (Serial.available()) {
			strcpy(message, Serial.readString().c_str());
			if (message[0] != '!')
			{
				sendUPD(message);
				lastMillis = millis();
			}
			else
			{
				if (!strcmp(message, "!connect"))
				{
					WiFi.begin(WIFI_SSID, WIFI_PASS);
					// Connecting to WiFi...
					//Serial.print("Connecting to ");
					//Serial.println(WIFI_SSID);
					// Loop continuously while WiFi is not connected
					while (WiFi.status() != WL_CONNECTED)
					{
						delay(100);
					}
					UDP.begin(UDP_TX_PORT);
					// Connected to WiFi
					delay(500);
					Serial.println("!connected");
					//Serial.println();
					lastMillis = 0;
					emergency = false;
					land = false;
					heartbeat = false;
				}
				else if (!strcmp(message, "!reset"))
				{
					ESP.restart();
				}
				else Serial.println("invalid command");
			}
		}

		if (millis() - lastMillis > 10000) {
			sendUPD("command");
			lastMillis = millis();
			heartbeat = true;
		}
		
	}
	catch (int errCode)
	{
		switch (errCode)
		{
		case CONN_ERR:
			Serial.println("!ConnectionError");
			break;

		case E_LAND:
			Serial.println("!ELand");
			break;

		case E_STOP:
			Serial.println("!EStop");
			break;


		default:
			break;
		}
		
	}

}
