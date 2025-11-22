Jalapeno: Intelligent Manufacturing Safety Ecosystem 🏭
Jalapeno is a comprehensive AIoT (Artificial Intelligence of Things) safety solution designed for manufacturing environments. It fuses real-time computer vision with robust environmental sensing to create a "Smart Guardian" that detects both behavioral violations (like phone usage) and environmental hazards (like gas leaks or fire) instantly.
This system is designed to be a cost-effective, scalable solution for Industry 4.0 safety compliance.
🌟 Key Features
🧠 AI-Powered Vision: Uses YOLOv8 to detect safety violations in real-time.
Distraction Detection: Identifies unauthorized Phone Usage in hazardous zones.
Worker Presence: Detects People to validate active work zones.
🔥 Environmental Sensing:
Gas/Smoke Detection: Monitors air quality for dangerous levels using an MQ-2 sensor.
Temperature Monitoring: Tracks ambient heat to detect overheating machinery using a DHT11 sensor.
🚨 Multi-Layered Alerts:
Visual: Red/Green dashboard indicators and bounding boxes on the live feed.
Auditory: Real-time Text-to-Speech voice warnings ("Danger! Gas Leak Detected").
Physical: Hardware buzzer and strobe LED activation via ESP32 microcontroller.
Remote: Instant Telegram notifications with photo evidence sent directly to supervisors' phones.
🛡️ Safety-First Logic: Prioritizes critical environmental threats (Gas/Fire) over minor behavioral infractions to ensure evacuation protocols are followed first.
📸 Smart Evidence: Automatically captures and timestamps photos of safety violations for compliance audits and accident investigation.
🛠️ Hardware Requirements
The system relies on a robust IoT node built on the ESP32 platform.
Microcontroller: ESP32 Development Board (Dev Kit V1)
Sensors:
MQ-2 Gas/Smoke Sensor Module
DHT11 Temperature & Humidity Sensor Module
Actuators:
Active Buzzer (5V)
Red LED (5mm)
Components:
NPN Transistor (2N2222 or BC547) - For driving the buzzer
Resistors: 330Ω (x1), 1kΩ (x1), 10kΩ (x2 - For voltage divider)
Electrolytic Capacitor (100µF) - For power stability
Breadboard & Jumper Wires
Connectivity: Micro-USB Data Cable
💻 Software Requirements
The "Brain" of the system runs on a laptop/PC, processing vision data and coordinating with the hardware.
Python Libraries
Install these using pip:
ultralytics
opencv-python
pyserial
pyttsx3
requests

Hardware Firmware
Arduino IDE: Used to upload C++ code to the ESP32.
Libraries: DHT sensor library (by Adafruit).
🚀 Installation & Setup
1.	Hardware Setup
Wire the Circuit: Connect sensors to the ESP32 following the pinout:
MQ-2 (A0): GPIO 34 (Use 10k/10k Voltage Divider to protect the pin!)
DHT11 (Data): GPIO 4 (Connect VCC to 3.3V, not 5V)
Buzzer (Base): GPIO 18 (via Transistor)
LED (+): GPIO 2
Upload Firmware: Flash the provided Jalapeno_Firmware.ino code to the ESP32 using Arduino IDE.
2.	Software Setup
Clone/Download this repository.
Configure main.py:
Update SERIAL_PORT to match your ESP32's COM port (e.g., COM3, COM6).
Add your Telegram Bot Token and Chat ID to the configuration section for remote alerts.
Run the System:
python main.py

📖 Usage Guide
Startup: The system will initialize the serial connection to the ESP32 and load the YOLOv8 model.
Monitoring: The dashboard shows a live video feed with overlay status.
Green Box: Safe / Authorized Worker.
Red Box: Violation (Phone Detected) / Danger.
Triggers:
Phone Violation: Hold up a phone to trigger "Distraction Alert" (Voice + Buzzer + Telegram Photo).
Gas Leak: Use a lighter (gas only, no flame) near the MQ-2 sensor to trigger "Gas Alert" (Voice + Siren + Telegram Text).
Overheating: Blow hot air on the DHT11 sensor to trigger "Temperature Alert".
Alerts: Check your Telegram app for real-time updates and photo evidence of any phone violations.
📂 File Structure
main.py: The core Python script handling AI, Logic, and Alerts.
Jalapeno_Firmware.ino: C++ code running on the ESP32 (handles sensors and physical alarms).
Evidence/: Auto-generated folder where violation photos are stored.
yolov8n.pt: Pre-trained YOLO model file (auto-downloaded on first run).
📚 References & Open Source Resources
YOLOv8 (Ultralytics): https://github.com/ultralytics/ultralytics - Real-time Object Detection.
ESP32 Arduino Core: https://github.com/espressif/arduino-esp32 - Hardware Support.
