# IoT Project – Parcel Box Documentation

[![Build](https://github.com/mblees/Paketbox/actions/workflows/build.yml/badge.svg)](https://github.com/mblees/Paketbox/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![The finished parcel box](https://github.com/mblees/IOT_Paketbox/assets/104490472/336fe2ea-0bf8-496e-8120-b985baa9306d)

## Overview

### 0. About the project
This project was part of an IOT class during my bachelors degree. Even though i was unexperienced at the time, the project features some technologies i still work with today (lora, mqtt, homeassistant, 3d-printing). It would be interesting to revive the idea with better materials and actually use it.

### 1. Hardware
   #### 1.1 Box
   The frame of the parcel box is built from MiniTec aluminium profiles that hold 4 mm chipboard panels. The lid is connected to the body of the box with 2 hinges.

   #### 1.2 Sensors / other hardware
   - Ultrasonic sensor: HC-SR04
       - The sensor runs on 5 V, but the ESP32's GPIO pins only tolerate 3.3 V, so a voltage divider made of two 10 kΩ resistors is required. It does not bring the voltage down to exactly 3.3 V, so the software has to account for that.
   - Reed module: KY-021
       - Powered with 3.3 V, so nothing special has to be considered here.
   - Stepper motor: 28BYJ-48
       - Powered with 5 V through its matching motor driver.
   - Matrix keypad: [link to the keypad](https://www.az-delivery.de/products/4x4-matrix-keypad)
       - Due to a lack of pins, I only use the 4x4 matrix as a 2x2 matrix with the keys 1, 2, 4 and 5.
   - Power is supplied by a power bank with a 5 V output.

   #### 1.3 Microcontroller
   The microcontroller is the WiFi LoRa 32 V2 by Heltec Automation with a built-in LoRa module, display and integrated LED. To save energy, neither the display nor the integrated LED is used.

   #### 1.4 Locking mechanism
   The locking mechanism consists of a stepper motor with a gear that pushes a bolt through 2 eyelets. One eyelet is attached to the lid and one to the body of the box; when the bolt is extended, they prevent the lid from being opened.

  ![Locking mechanism: stepper motor with gear and bolt](https://github.com/mblees/IOT_Paketbox/assets/104490472/fe967090-578b-4d9d-857b-74d28b1b5561)

   Note: Because of the budget, these are 3D-printed parts, which would not be secure enough in a real application to protect a valuable parcel.

### 2. Software
   #### 2.1 C++ part / microcontroller programming
   The controller firmware is based on the framework/example LMIC-node by lnlp ([GitHub link](https://github.com/lnlp/LMIC-node)). I added the control logic in the `main()` function as well as libraries for all peripheral components:
   - `matrix.h`/`matrix.cpp`: reads the matrix keypad using the library `chris--a/Keypad@^3.1.1`.
   - `reed_sensor.h`/`reed_sensor.cpp`: reads the reed sensor via `digitalRead()`.
   - `rfid.h`/`rfid.cpp`: contains functions for using an RFID sensor. This feature was not used in the end because the microcontroller does not have enough pins left.
   - `stepper.h`/`stepper.cpp`: drives the stepper motor driver using the library `waspinator/AccelStepper@^1.64`.
   - `supersonic_sensor.h`/`supersonic_sensor.cpp`: evaluates the ultrasonic sensor and includes a function that averages several readings, since the sensor occasionally returns wrong values.

   #### 2.2 Python service
   The service uses the Home Assistant API to send push notifications to phones and the `paho-mqtt` library to process the LoRa data received from TTN and then trigger a `notify` service in Home Assistant.

   The credentials (TTN API key, Home Assistant token) are not in the repository: copy `Python Service/.env.example` to `Python Service/.env` and fill it in, or set the variables `TTN_API_KEY`, `HA_URL` and `HA_TOKEN` in the environment. The firmware's LoRaWAN keys belong in `PlatformIO Project/keyfiles/lorawan-keys.h` (template: `lorawan-keys_example.h`).

   <img src="https://github.com/mblees/IOT_Paketbox/assets/104490472/f75a16c0-de0b-48ad-9c84-602454432d41" alt="Push notification on the phone" width="800" height="800">

   #### 2.3 Home Assistant
   In my case, the Home Assistant server runs in an Oracle VM VirtualBox on the same PC that also runs the Python service. The two programs only depend on each other in that they have to run in the same Wi-Fi network.

   ![Home Assistant dashboard](https://github.com/mblees/IOT_Paketbox/assets/104490472/3eea11d3-cd80-485e-a917-ccd353d0eec2)

### 3. Data transmission
   The data recorded by the sensors is sent by the microcontroller via LoRa and The Things Network (TTN) when the box is opened and closed. TTN provides the data through an MQTT server; a Python service picks it up and triggers a service in Home Assistant. That service in turn causes a push notification to appear on the box owner's phone.

   Sensors -> ESP32 -> LoRa -> TTN -> MQTT -> Python service -> Home Assistant -> mobile phone

### 4. Pin assignment
![Pinout of the Heltec WiFi LoRa 32 V2](https://github.com/mblees/IOT_Paketbox/assets/104490472/6597162c-f7ba-4976-bddb-5b58aae3a955)

| Device               | Pins                    |
|----------------------|-------------------------|
| Matrix keypad        | 0, 2, 23, 25            |
| Stepper motor        | 12, 13, 17, 21          |
| Reed sensor          | 36                      |
| Ultrasonic sensor    | 22, 37                  |
| LoRa module (on-board) | 19, 18, 5, 15, 4, 16, 26, 27, 14 |

### 5. Notes
To add further features such as an RFID sensor, the ESP32 used here lacks additional pins. A possible alternative in this case was the STM32WL55JC with a LoRa antenna. However, there are no public LoRa libraries for this microcontroller that would have been suitable for this project. I tried to write a library for this controller myself, but was unable to get results after several hours of work.

## License

My own code and documentation are released under the [MIT license](LICENSE). The firmware in
`PlatformIO Project/` is based on [LMIC-node](https://github.com/lnlp/LMIC-node) and keeps its
original MIT license ([`PlatformIO Project/LICENSE`](PlatformIO%20Project/LICENSE)).
