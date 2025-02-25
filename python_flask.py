from flask import Flask, jsonify, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

# Inisialisasi app penampung Flask
app = Flask(__name__)

# Koneksi langsung ke MongoDB, di mana uri tersebut sesuai dengan yang ada di 
uri = "mongodb+srv://neotech_polman:neotechpolman1234@cluster-neotech-polman.43ik8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-NeoTech-Polman"
client = MongoClient(uri, server_api=ServerApi('1'))

# Buat database dan koleksi untuk menyimpan data sensor
db = client['Database_IoT']
my_collections = db['Data_Sensor']

# Cek koneksi ke MongoDB
try:
    client.admin.command('ping')
    print("Pinged your deployment. Connected to MongoDB")
except Exception as e:
    print(e)

# Route (endpoint) untuk menerima data sensor
@app.route('/data', methods=['POST'])
def save_sensor_data():
    # Ambil data dari request dalam format JSON
    data = request.json

    # Validasi apabila tidak ada data
    if not data:
        return jsonify({"Error": "No data provided"}), 400
    
    try:
        # Tambahkan timestamp sebelum menyimpan ke MongoDB
        data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Simpan data ke koleksi MongoDB
        my_collections.insert_one(data)

        # Pesan yang muncul jika data sukses tersimpan
        return jsonify({"Message": "Data inserted successfully"}), 200
    except Exception as e:
        # Tangani eror jika data gagal tersimpan
        return jsonify({"Error": str(e)}), 500

# Jalankan server Flask
if __name__ == '__main__':
    # Konfigurasi host sesuai dengan IPv4 Address dan port sesuai keinginan
    app.run(host="192.168.249.70", debug=True, port=7000)