import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import datetime

class ChatServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Chat Peladen - Lokal (Pesan Privat)')
        self.root.geometry('600x600')
        # Teks Area untuk log Peladen
        self.text_area = scrolledtext.ScrolledText(root, height=20, width=70)
        self.text_area.pack(padx=10, pady=10)
        # Tombol mulai peladen
        self.start_button = tk.Button(root, text='Mulai Peladen', command=self.start_server_gui)
        self.start_button.pack(pady=5)
        self.server_socket = None
        self.clients = [] # Daftar (socket, klien_id)
        self.client_lock = threading.Lock() # Lock untuk sinkron
        self.log_file = 'LogPeladen.txt'
        self.host_entry = tk.Entry(root, width=30) # Tombol untuk input Host
        self.host_entry.pack(pady=5)
        self.host_entry.insert(0, "Masukkan IP Server Peladen")

    def log_message(self, message):
        # Catat Pesan ke Berkas Log
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.text_area.insert(tk.END, f'[{timestamp}] {message}\n')
        self.text_area.see(tk.END)
        with open(self.log_file, 'a') as f:
            f.write(f'[{timestamp}] {message}\n')

    def send_private_message(self, message, source_socket, target_id):
        # Kirim Pesan Privat ke Klien dengan ID Tertentu
        with self.client_lock:
            for client_socket, client_id in self.clients:
                if client_id == target_id:
                    try:
                        client_socket.send(message.encode('ascii'))
                        return True
                    except Exception as e:
                        self.log_message(f'Galat mengirim ke {target_id}: {e}')
                        return False
            return False
    
    def handle_client(self, client_socket, client_address, client_id):
        # Menangani Pesan dari Klien
        self.log_message(f'Koneksi dari {client_address} (ID: {client_id})')
        with self.client_lock:
            self.clients.append((client_socket, client_id))
        try:
            while True:
                data = client_socket.recv(1024).decode('ascii')
                if not data or data.lower() == 'exit':
                    self.log_message(f'Client {client_id} mengakhiri koneksi')
                    break
                # Parse pesan degan format TO:<target_id>:<message>
                if data.startswith('TO:'):
                    try:
                        _, target_id, message = data.split(':', 2)
                        ascii_codes = [ord(char) for char in message]
                        log_meessage = f'Dari {client_id} ke {target_id}: {message} (ASCII: {ascii_codes})'
                        self.log_message(log_meessage)
                        success = self.send_private_message(log_meessage, client_socket, target_id)
                        if not success:
                            try:
                                client_socket.send(f'Galat: Klien {target_id} tak ditemukan'.encode('ascii'))
                            except:
                                pass
                    except ValueError:
                        self.log_meessage(f'Galat Pada Format Pesan dari {target_id}: {data}')
                        client_socket.send('Galat: Format Pesan Salah (TO:<target_id>:<message>)'.encode('ascii'))
                else:
                    self.log_message(f'Galat: Pesan Dari {client_id} tidak menggunakan format TO:<target_id:<message>')
                    client_socket.send('Galat: Gunakan Format TO:<target_id>:<message>'.encode('ascii'))
        except Exception as e:
            self.log_message(f'Galat pada Klien {client_id}: {e}')
        finally:
            with self.client_lock:
                self.clients = [(cs, cid) for cs, cid in self.clients if cs != client_socket]
            client_socket.close()
    
    def accept_connections(self):
        # Menerima koneksi dari klien
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_id = client_socket.recv(1024).decode('ascii') # Terima ID Klien
                threading.Thread(target=self.handle_client, args=(client_socket, client_address, client_id), daemon=True).start()
            except:
                break

    def start_server_gui(self):
        host = self.host_entry.get()
        self.start_server(host, 12345)
    
    def start_server(self, host, port=12345):
        # Mulai Server
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(5)
            self.log_message(f'Peladen berjalan di {host}:{port}')
            self.start_button.config(state='disabled')
            threading.Thread(target=self.accept_connections, daemon=True).start()
        except Exception as e:
            self.log_message(f'Galat saat memulai Peladen: {e}')

if __name__ == '__main__':
    print('Peladen Perpesanan Lokal (Pesan Privat)')
    root = tk.Tk()
    app = ChatServerGUI(root)
    root.mainloop()
