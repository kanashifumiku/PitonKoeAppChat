import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import time
import datetime

class ChatClientGUI:
    def __init__(self, root, client_id):
        self.root = root
        self.client_id = client_id
        self.root.title(f'Chat Klien - {client_id}')
        self.root.geometry('600x450')
        # Teks Area untuk Log Chat
        self.text_area = scrolledtext.ScrolledText(root, height=20, width=70)
        self.text_area.pack(padx=10, pady=10)
        # Frame untuk Input
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=5)
        # Label dan input untuk ID Penerima
        tk.Label(self.input_frame, text='Kepada (ID):').pack(side=tk.LEFT, padx=5)
        self.target_entry = tk.Entry(self.input_frame, width=20)
        self.target_entry.pack(side=tk.LEFT, padx=5)
        # Input untuk pesan
        tk.Label(self.input_frame, text='Pesan:').pack(side=tk.LEFT, padx=5)
        self.message_entry = tk.Entry(self.input_frame, width=30)
        self.message_entry.pack(side=tk.LEFT, padx=5)
        # Tombol untuk koneksi 
        self.server_entry = tk.Entry(root, width=20)
        self.server_entry.pack(pady=5)
        self.server_entry.insert(0, 'server')
        self.connect_button = tk.Button(root, text='Hubungkan ke Peladen', command=self.connect_to_server_gui)
        self.connect_button.pack(padx=5)
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
                    self.log_message('Server mengakhiri koneksi')
                    self.running = False
                    break
                self.log_message(f'Diterima: {data}')
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
                full_message = f'TO:{target_id}:{message}'
                self.client_socket.send(full_message.encode('ascii'))
                rtt = (time.time() - start_time) * 1000 # satuan MS
                ascii_codes = [ord(char) for char in message]
                self.log_message(f'Terkirim ke {target_id}: {message} (ASCII: {ascii_codes}, RTT: {rtt:.2f} ms)')
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

    def connect_to_server_gui(self):
        host = self.server_entry.get()
        self.connect_to_server(host, 12345)
    
    def connect_to_server(self, host, port=12345):
        # Menghubungkan ke Peladen
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.client_socket.send(self.client_id.encode('ascii')) # Utk Kirim ID Klien
            self.log_message(f'Terhubung ke {host}:{port}')
            self.connect_button.config(state='disabled')
            self.message_entry.bind('<Return>', self.send_message) # Even -driven: Enter utk Kirim
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.log_message(f'Galat Koneksi: {e}')

if __name__ == '__main__':
    print('Klien Perpesanan Lokal (Pesan Privat)')
    client_id = input('Masukkan ID Klien. Misalnya Klien1\n> ')
    root = tk.Tk()
    app = ChatClientGUI(root, client_id)
    root.mainloop()
