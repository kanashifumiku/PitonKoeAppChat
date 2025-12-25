import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import simpledialog
import socket
import threading
import time
import datetime

def awal():
    print('Klien Perpesanan Lokal (Pesan Privat)')
    while True:
        client_id = simpledialog.askstring('Pengguna PesanKoe | Masuk', 'Masukkan ID Pengguna',)
        if client_id:
            break
        else:
            galat_id = messagebox.askretrycancel("Galat", "ID Pengguna tidak boleh kosong. Masukkan ulang ID?")
            if not galat_id:
                messagebox.showwarning('Perhatian', 'Program akan ditutup')
                return
    
    while True:
        host = simpledialog.askstring('Pengguna PesanKoe | Masuk', 'Masukkan Peladen')
        if host:
            break
        else:
            galat_host = messagebox.askretrycancel('Galat', 'Peladen tidak boleh kosong. Masukkan ulang Peladen?')
            if not galat_host:
                messagebox.showinfo('Perhatian', 'Program akan ditutup')
                return
                
    messagebox.showinfo('Selamat Datang', f'Hai, {client_id}.\nPetunjuk Penggunaan:\n1. Ketik all pada ID untuk pesan BROADCAST\n2. Jika Peladen tidak bisa tersambung, mulai ulang program')
    root = tk.Tk()
    app = ChatClientGUI(root, client_id)
    app.connect_to_server(host, 12345)
    root.mainloop()

class ChatClientGUI:
    def __init__(self, root, client_id):
        self.root = root
        self.client_id = client_id

        self.root.title(f'Pengguna PesanKoe | ID: {client_id}')
        root.resizable(False, False) # Agar window tidak bisa diresize
        self.root.geometry('400x600')

        # Teks Area untuk Log Chat
        self.text_area = scrolledtext.ScrolledText(root, height=20, width=70)
        self.text_area.pack(padx=10, pady=10)

        # Frame untuk Input
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(padx=10, pady=5, fill="x")

        # Label dan input untuk ID Penerima
        tk.Label(self.input_frame, text='Kepada (ID):').pack(side=tk.TOP, padx=5, anchor='w')
        self.target_entry = tk.Entry(self.input_frame, width=20)
        self.target_entry.pack(side=tk.TOP, padx=5, anchor='w')

        # Input untuk pesan
        tk.Label(self.input_frame, text='Pesan:').pack(side=tk.TOP, padx=5, anchor='w')
        self.message_entry = tk.Entry(self.input_frame, width=30)
        self.message_entry.pack(side=tk.TOP, padx=5, anchor='w')

        self.client_socket = None
        self.log_file = f'klien_{client_id}_log.txt'
        self.running = True
    
    def log_message(self, message):
        # Catat pesan ke GUI dan Log
        timestamp = datetime.datetime.now().strftime('%Y - %m - %d %H:%M:%S')
        self.text_area.insert(tk.END, f'[{timestamp}] {message}\n')
        self.text_area.see(tk.END)
        with open(self.log_file, 'a') as f:
            f.write(f'[{timestamp}] {message}\n')

    def receive_messages(self):
        # Untuk terima pesan dari Server
        while self.running:
            try:
                data = self.client_socket.recv(1024).decode('ascii')
                if not data:
                    self.log_message('[SISTEM] Server mengakhiri koneksi')
                    self.running = False
                    break
                self.log_message(f'{data}')
            except Exception as e:
                self.log_message(f'Galat menerima: {e}')
                self.running = False
                break
    
    def send_message(self, event=None):
        # Mengirim pesan privat ke peladen
        target_id = self.target_entry.get().strip()
        message = self.message_entry.get().strip()
        if target_id and message and self.client_socket:
            try:
                start_time = time.time()
                if target_id.upper() == 'ALL':
                    full_msg = f'ALL:{message}'
                else:
                    full_msg = f'TO:{target_id}: {message}'
                # full_message = f'TO:{target_id}:{message}'
                self.client_socket.send(full_msg.encode('ascii'))
                rtt = (time.time() - start_time) * 1000 # satuan MS
                ascii_codes = [ord(char) for char in message]
                if target_id.upper() == 'ALL':
                    self.log_message(f'[BROADCAST --> ALL]: {message} (ASCII: {ascii_codes}, RTT: {rtt:.2f} ms)')
                else:
                    self.log_message(f'[PRIVAT --> {target_id}] {message} (ASCII: {ascii_codes}, ) || RTT: {rtt:.2f} ms')
                if message.lower() == 'exit':
                    self.running = False
                    self.client_socket.close()
                    self.log_message('Koneksi Ditutup')
                    self.client_socket = None
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                self.log_message(f'Galat mengirim: {e}')
        else:
            self.log_message('Galat: Isi ID Penerima dan Pesan')
    
    def connect_to_server(self, host, port=12345):
        # Menghubungkan ke Peladen
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.client_socket.send(self.client_id.encode('ascii')) # Utk Kirim ID Klien
            self.log_message(f'Terhubung ke {host}:{port}')
            # self.connect_button.config(state='disabled')
            self.message_entry.bind('<Return>', self.send_message) # Even -driven: Enter utk Kirim
            threading.Thread(target=self.receive_messages, daemon=True).start()
            messagebox.showinfo('Informasi', f'Berhasil terhubung ke Peladen\n{host}:{port}')
        except Exception as e:
            self.log_message(f'Galat Koneksi: {e}')
            galat_konek = messagebox.showerror('Galat Koneksi', f'Tidak bisa connect ke {host}:{port}\n\n{e}')
            self.root.destroy()
                

if __name__ == '__main__':
    awal()