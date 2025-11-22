from ultralytics import YOLO
import cv2
import serial
import time
import pyttsx3 
import os
import threading 
import requests 
from datetime import datetime

SERIAL_PORT = 'COM6'  
BAUD_RATE = 115200

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN') 
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') 
ENABLE_TELEGRAM = True 

GAS_LIMIT = 1500  
TEMP_THRESHOLD_RISE = 2.0 

face_processing_lock = False 
last_buzzer_state = -1        

def speak_async(message):
    def _speak():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(message)
            engine.runAndWait()
        except: pass
    threading.Thread(target=_speak, daemon=True).start()

def send_telegram(message, photo_path=None):
    def _send():
        if not ENABLE_TELEGRAM: return
        try:
            if message:
                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                data = {"chat_id": TELEGRAM_CHAT_ID, "text": f"🚨 {message}"}
                requests.post(url, data=data, timeout=5)
            
            if photo_path and os.path.exists(photo_path):
                url_pic = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
                with open(photo_path, "rb") as image_file:
                    files = {"photo": image_file}
                    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": f"📸 EVIDENCE: {message}"}
                    requests.post(url_pic, data=data, files=files, timeout=10)
        except Exception as e:
            print(f"⚠ TELEGRAM ERROR: {e}")
    threading.Thread(target=_send, daemon=True).start()

try:
    esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print(f"SUCCESS: Connected to {SERIAL_PORT}")
except:
    print(f"ERROR: Check {SERIAL_PORT}. Running in NON-HARDWARE mode.")
    esp32 = None

print("Loading YOLO...")
model = YOLO('yolov8n.pt')

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

current_gas = 0
current_temp = 0.0
baseline_temp = None  

last_voice_time = 0
last_photo_time = 0
last_telegram_time = 0

VOICE_COOLDOWN = 4 
PHOTO_COOLDOWN = 3 
TELEGRAM_COOLDOWN = 10 

def snap_evidence(frame, cause):
    global last_photo_time
    if time.time() - last_photo_time > PHOTO_COOLDOWN:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Evidence/{cause}_{timestamp}.jpg"
        if not os.path.exists("Evidence"): os.makedirs("Evidence")
        cv2.imwrite(filename, frame)
        last_photo_time = time.time()
        return filename
    return None

def control_buzzer(state):
    global last_buzzer_state
    if esp32 and state != last_buzzer_state:
        esp32.write(str(state).encode())
        last_buzzer_state = state

print("SYSTEM ARMED. Press 'Q' to quit.")

while True:
    success, frame = cap.read()
    if not success: break
    height, width, _ = frame.shape
    
    if esp32 and esp32.in_waiting > 0:
        try:
            raw_line = esp32.readline().decode('utf-8', errors='ignore').strip()
            if "," in raw_line:
                parts = raw_line.split(',')
                current_gas = int(parts[0])
                current_temp = float(parts[1])
                if baseline_temp is None and current_temp > 0:
                    baseline_temp = current_temp
        except: pass

    danger_active = False
    critical_warning = ""
    buzzer_trigger = 0 
    person_detected_in_frame = False 
    
    results = model(frame, stream=True, verbose=False)
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls = int(box.cls[0])
            class_name = model.names[cls]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if class_name == "person":
                person_detected_in_frame = True
                
                if current_gas > GAS_LIMIT:
                    danger_active = True
                    critical_warning = f"DANGER! Gas Leak ({current_gas})"
                    buzzer_trigger = 1
                    cv2.rectangle(frame, (0,0), (width, height), (0,0,255), 5) 
                
                elif baseline_temp is not None and current_temp > (baseline_temp + TEMP_THRESHOLD_RISE):
                    danger_active = True
                    critical_warning = f"WARNING! Temp High ({current_temp}C)"
                    buzzer_trigger = 1
                
                color = (0, 255, 0) 
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, "WORKER PRESENT", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if class_name == "cell phone" and box.conf[0] > 0.5:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(frame, "PHONE DETECTED", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                buzzer_trigger = 1 
                
                if time.time() - last_voice_time > VOICE_COOLDOWN:
                    speak_async("Phone violation detected.")
                    last_voice_time = time.time()
                
                if time.time() - last_telegram_time > TELEGRAM_COOLDOWN:
                    path = snap_evidence(frame, "Phone_Violation")
                    send_telegram(f"Worker using phone!", path)
                    last_telegram_time = time.time()


    if not person_detected_in_frame:
        danger_active = True
        cv2.putText(frame, "NO WORKER DETECTED", (50, height//2), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        buzzer_trigger = 1 
        
        if time.time() - last_voice_time > VOICE_COOLDOWN:
            speak_async("Warning. No worker present.")
            last_voice_time = time.time()

    control_buzzer(buzzer_trigger)

    if critical_warning:
        if time.time() - last_voice_time > VOICE_COOLDOWN:
            speak_async(critical_warning)
            last_voice_time = time.time()
            
        if time.time() - last_telegram_time > TELEGRAM_COOLDOWN:
            send_telegram(critical_warning)
            last_telegram_time = time.time()

    gas_col = (0,0,255) if current_gas > GAS_LIMIT else (0,255,0)
    cv2.putText(frame, f"GAS: {current_gas}", (20, height-50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, gas_col, 2)

    temp_col = (0,0,255) if (baseline_temp and current_temp > baseline_temp + TEMP_THRESHOLD_RISE) else (0,255,255)
    cv2.putText(frame, f"TEMP: {current_temp} C", (20, height-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, temp_col, 2)

    cv2.imshow("Jalapeno Smart System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
control_buzzer(0) 
if esp32: esp32.close()
