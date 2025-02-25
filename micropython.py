from machine import Pin
import time
import dht
import ujson
import utime as time
import urequests as requests

DEVICE_ID = "esp32-sic6" # ID device yang ada di Ubidots
TOKEN = "BBUS-viO3xTkR9WcTV3f4r0aMTY9x05xwJw" # Token dari DEVICE_ID

# Inisialisasi sensor dan komponen
led = Pin(4, Pin.OUT) # Letak LED di pin 4
buzzer = Pin(19, Pin.OUT) # Letak Buzzer Active di pin 19
pir = Pin(18, Pin.IN) # Letak sensor PIR di pin 18
dht = dht.DHT11(Pin(5)) # Letak sensor DHT di pin 5

# Fungsi untuk koneksi ESP32 ke WiFi
def do_connect():
    # Impor modul network dan inisialisasi mode station
    import network
    sta_if = network.WLAN(network.STA_IF)
    
    # Periksa apakah sudah terhubung ke jaringan WiFi
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect('2029gantipresiden', '987654321') # SSID dan password dari jaringan WiFi
        while not sta_if.isconnected():
            pass
    
    # Tunggu sampai koneksi berhasil
    print('Network config:', sta_if.ifconfig()[0])

# Fungsi untuk format timestamp DD-MM-YYYY HH:MM:SS pada MongoDB
def get_formatted_timestamp():
    # Mengambil waktu lokal dari sistem ESP32
    timestamp = time.localtime()
    
    # Format waktu menjadi string dengan format DD-MM-YYYY HH:MM:SS
    return "{:02d}-{:02d}-{:04d} {:02d}:{:02d}:{:02d}".format(
        timestamp[2],
        timestamp[1],
        timestamp[0],
        timestamp[3],
        timestamp[4],
        timestamp[5]
    )

# Fungsi untuk menerima data sensor dan mengirimkannya ke Ubidots
def send_data_to_ubidots(temperature, humidity, motion):
    # URL (REST API) untuk mengirimkan data ke Ubidots
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    
    # Header terkait tipe konten dan token autentikasi
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": TOKEN
    }
    
    # Data sensor DHT dan PIR yang akan dikirim
    data = {
        "temp": temperature, # Suhu (Celcius)
        "humidity": humidity, # Kelembaban (%)
        "motion": motion # Gerakan (0 atau 1)
    }

    try:
        # Kirim data ke Ubidots dengan metode POST
        response = requests.post(url, json=data, headers=headers)
        
        # Periksa apakah data berhasil terkirim
        if response.status_code == 200:
            print("Data berhasil dikirim ke Ubidots!")
        else:
            print(f"Gagal mengirim data: {response.status_code}")
        
        # Menutup koneksi HTTP
        response.close()
    except Exception as e:
        # Menangani kegagalan pengiriman data
        print(f"Error: {e}")

# Fungsi untuk menerima data sensor dan mengirimkannya ke API Services yang terhubung dengan MongoDB
def send_data_to_server(temperature, humidity, motion, timestamp):
    # URL (API Services) untuk mengirimkan data ke MongoDB
    url = "http://192.168.249.70:7000/data" # Gunakan IPv4 Address
    
    # Header terkait tipe konten
    headers = {"Content-Type": "application/json"}
    
    # Data sensor DHT, PIR, dan timestamp yang akan dikirim
    data = {
        "temp": temperature, # Suhu (Celcius)
        "humidity": humidity, # Kelembaban (%)
        "motion": motion, # Gerakan (0 atau 1)
        "timestamp": timestamp # Data timestamp sebagai riwayat tersimpannya data
    }

    try:
        # Kirim data ke API Services dengan metode POST
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        # Periksa apakah data berhasil terkirim
        if response.status_code == 200:
            print("Data berhasil dikirim ke MongoDB!")
        else:
            print(f"Gagal mengirim data: {response.status_code}")
        
        # Menutup koneksi HTTP
        response.close()
    except Exception as e:
        # Menangani kegagalan pengiriman data
        print(f"Error: {e}")

# Koneksi ke WiFi
do_connect()

while True:
    try:
        dht.measure() # Membaca data dari sensor DHT11
        temp = dht.temperature() # Data suhu (Celcius)
        hum = dht.humidity() # Data kelembaban (%)
        motion = pir.value() # Membaca gerakan dari sensor PIR (0 = tidak ada gerakan, 1 = ada gerakan)
        
        # Mengambil data timestamp hanya untuk MongoDB
        timestamp_mongodb = get_formatted_timestamp()

        # Jika ada gerakan, maka buzzer akan diaktifkan
        if motion:
            buzzer.value(1) # Buzzer menyala
            print("Gerakan terdeteksi! Buzzer ON")
        else:
            buzzer.value(0) # Buzzer mati

        # Jika suhu > 30°C, maka LED akan dinyalakan
        if temp > 30:
            led.value(1) # LED menyala
            print("Suhu tinggi! LED ON")
        else:
            led.value(0) # LED mati

        # Mengirim data ke Ubidots (tanpa timestamp)
        send_data_to_ubidots(temp, hum, motion)

        # Mengirim data ke API Services dan menyimpannya di MongoDB (dengan timestamp)
        send_data_to_server(temp, hum, motion, timestamp_mongodb)

        # Tunggu 1 detik sebelum membaca ulang sensor
        time.sleep(1)
    except Exception as e:
        # Menampilkan eror jika terjadi kesalahan
        print(e)