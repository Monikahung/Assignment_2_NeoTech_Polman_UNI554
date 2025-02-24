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