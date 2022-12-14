# include <Wire.h>
# ifdef ESP32
  # include <Wifi.h>
  # include <ESPAsyncWebServer.h>
  # include <SPIFFS.h>
 # else
  #include <Arduino.h>
  #include <ESP8266WiFi.h>
  #include <Hash.h>
  #include <ESPAsyncTCP.h>
  #include <ESPAsyncWebServer.h>
  #include <FS.h>
# endif

const char* ssid = "jj";
const char* password = "chocolatevaso";

AsyncWebServer server(80);
String ReadA0() {
  float analog_read = analogRead(A0);
  //float val = map(analog_read, 0, 1023, 0, 3.3);
  float val = analog_read;
  if (isnan(analog_read)) {
    Serial.println("Failed to read");
    return "";
  }
  else {
    Serial.println(val);
    return String(val);
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  // Inicializar SPIFFS
  if(!SPIFFS.begin()) {
    Serial.println("An error has occurred while, punting SPIFFS");
    return;
  }

  // Conexion WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  // Print ESP8266 IP
  Serial.println(WiFi.localIP());

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){ request->send(SPIFFS, "/index 2.html");});
  server.on("/ECG", HTTP_GET, [](AsyncWebServerRequest *request){
    AsyncWebServerResponse *response = request->beginResponse(200, "text/plain", ReadA0().c_str());
    response->addHeader("Access-Control-Allow-Origin","*");
    request->send(response);
    //request->send_P(200, "text/plain", ReadA0().c_str());
    });
  server.begin();
}

void loop() {
  // put your main code here, to run repeatedly:

}
