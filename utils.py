# utils.py
import math
from datetime import datetime, timedelta

def sesuaikan_fraksi_bei(harga, tipe='normal'):
    harga = int(round(harga))
    if harga < 50: return 50
    elif harga < 200: fraksi = 1
    elif harga < 500: fraksi = 2
    elif harga < 2000: fraksi = 5
    elif harga < 5000: fraksi = 10
    else: fraksi = 25
    
    if tipe in ['sl', 'tp']:
        return math.floor(harga / fraksi) * fraksi
    else:
        return round(harga / fraksi) * fraksi

def hitung_batas_ara_arb(close_kemarin):
    # PERBAIKAN 1: Logika fraksi regulasi BEI (Inklusif untuk batas atas)
    if close_kemarin <= 200: 
        limit = 0.35 
    elif close_kemarin <= 5000:
        limit = 0.25 
    else:
        limit = 0.20 
        
    ara = sesuaikan_fraksi_bei(close_kemarin * (1 + limit))
    arb = sesuaikan_fraksi_bei(close_kemarin * (1 - limit))
    
    # Proteksi gocap (Saham tidak bisa ARB di bawah Rp 50 di pasar reguler)
    if arb < 50: arb = 50 
    return ara, arb

def cek_waktu_trading():
    waktu_sekarang = datetime.utcnow() + timedelta(hours=7)
    jam = waktu_sekarang.hour
    menit = waktu_sekarang.minute
    waktu_desimal = jam + (menit / 60)

    # PERBAIKAN 2: Deteksi Jam Istirahat Bursa Sesi 1
    # Memblokir waktu antara 12.00 s/d 13.30 WIB agar algoritma tahu likuiditas sedang beku
    if 12.0 <= waktu_desimal < 13.5:
        return "Istirahat Sesi 1 (Market Closed) ⏸️", "warning"

    if 9 <= jam < 10: 
        return "Pagi (High Probability - Volatilitas Tinggi) 🔥", "success"
    elif 10 <= jam < 14: 
        return "Siang (Low Probability - Rawan Jebakan / Sideways) ⚠️", "warning"
    else: 
        return "Sore (Fase Penutupan / Mark-up Bandar) 📊", "info"
