import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import datetime

class ChatServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Peladen PesanKoe') # Judul window
        root.resizable(False, False) # Agar window tidak bisa diresize 
        self.text_area = scrolledtext.ScrolledText(root, height=10, width=50) # Teks Area untuk log Peladen
        self.text_area.pack(padx=5, pady=5, side=tk.BOTTOM)
        self.server_socket = None
        self.clients = {} # Daftar (socket, klien_id) pake DICT
        self.client_lock = threading.Lock() # Lock untuk sinkron
        self.top = tk.Frame(root)
        self.top.pack(padx=10, pady=5, fill="x")
        self.host_entry = tk.Entry(self.top, width=30) # Entry untuk input Host biar dinamis
        self.host_entry.pack(pady=5, side=tk.TOP, anchor='w')
        self.host_entry.insert(0, "Masukkan IP Server Peladen")
        self.start_button = tk.Button(self.top, text='Mulai Peladen', command=self.start_server_gui)  # Tombol mulai peladen
        self.start_button.pack(pady=5, side=tk.TOP, anchor='w')
        self.log_file = 'Peladen.txt'

    def log_message(self, message):
        # Catat Pesan ke Berkas Log
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.text_area.insert(tk.END, f'[{timestamp}] {message}\n')
        self.text_area.see(tk.END)
        with open(self.log_file, 'a') as f:
            f.write(f'[{timestamp}] {message}\n')

    def send_broadcast(self, message, sender_id): # Kirim Broadcast
        with self.client_lock:
            sent_count = 0
            for client_id, client_socket in self.clients.items(): 
                if client_id != sender_id:
                    try:
                        brd_msg = f'[BROADCAST] {message}'
                        client_socket.send(brd_msg.encode('ascii'))
                        self.log_message(f'[BROADCAST] {sender_id} ke {client_id}: {message}')
                        sent_count += 1
                    except Exception as e:
                        self.log_message(f'Galat kirim Ke {client_id}: {e}')
            if sent_count > 0:
                self.log_message(f'BROADCAST berhasil ke {sent_count} klien')
            return sent_count > 0

    def send_private_message(self, message, source_socket, target_id): # Kirim privat
        # Kirim Pesan Privat ke Klien dengan ID Tertentu
        with self.client_lock:
            if target_id in self.clients:
                client_socket = self.clients[target_id]
                try:
                     client_socket.send(message.encode('ascii'))
                     return True
                except Exception as e:
                    self.log_message(f'Galat mengirim ke {target_id}: {e}')
                    return False
        return False
    
    def handle_client(self, client_socket, client_address, client_id):
        # Menangani Pesan dari Klien
        self.log_message(f'[SISTEM] Koneksi baru dari {client_address} (ID: {client_id})')
        with self.client_lock:
            self.clients[client_id] = client_socket #Dict
        try:
            while True:
                data = client_socket.recv(1024).decode('ascii')
                if not data or data.lower() == 'exit':
                    self.log_message(f'[SISTEM] Client {client_id} mengakhiri koneksi')
                    break
                # Parse pesan dengan format yang sudah ditentukan
                if data.startswith('TO:'): # Ini Untuk Pesan Privat
                    try:
                        _, target_id, message = data.split(':', 2)
                        ascii_codes = [ord(char) for char in message]
                        log_message = f'[PRIVAT {client_id} --> {target_id}] {message} (ASCII: {ascii_codes})'
                        self.log_message(log_message)
                        success = self.send_private_message(log_message, client_socket, target_id)
                        if not success:
                            try:
                                client_socket.send(f'[SISTEM] Galat: Klien {target_id} tak ditemukan'.encode('ascii'))
                            except:
                                pass
                    except ValueError:
                        self.log_message(f'[SISTEM] Galat Pada Format Pesan dari {target_id}: {data}')
                        client_socket.send('[SISTEM] Galat: Format Pesan Salah (TO:<target_id>:<message>)'.encode('ascii'))
                elif data.startswith('ALL:'): # Ini untuk pesan broadcast
                    try:
                        broadcast_msg = data[4:].strip()  # Hilangkan "ALL:"
                        if broadcast_msg:
                            success = self.send_broadcast(broadcast_msg, client_id)
                            if not success:
                                messagebox.showwarning('Pemberitahuan', f'Tidak ada pengguna lain untuk menerima broadcast anda')
                                client_socket.send('[SISTEM] Galat: Tidak ada client lain untuk broadcast'.encode('ascii'))
                        else:
                            client_socket.send('[SISTEM] Galat: Pesan broadcast kosong'.encode('ascii'))
                    except Exception as e:
                        self.log_message(f'[SISTEM] Galat broadcast {client_id}: {e}')
                        client_socket.send('Galat: Format broadcast salah (ALL:message)'.encode('ascii'))
                else:
                    self.log_message(f'[SISTEM] Galat: Pesan Dari {client_id} tidak menggunakan format TO:<target_id:<message>')
                    client_socket.send('Galat: Gunakan Format TO:<target_id>:<message>'.encode('ascii'))
        except Exception as e:
            self.log_message(f'[SISTEM] Galat pada Klien {client_id}: {e}')
        finally:
            with self.client_lock:
                if client_id in self.clients:
                    del self.clients[client_id]
    
    def accept_connections(self):
        # Menerima koneksi dari klien
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_id = client_socket.recv(1024).decode('ascii') # Terima ID Klien
                threading.Thread(target=self.handle_client, args=(client_socket, client_address, client_id), daemon=True).start()
            except:
                break

    def start_server_gui(self): # Custom host input using GUI
        host = self.host_entry.get()
        self.start_server(host, 12345)
    
    def start_server(self, host, port=12345):
        # Mulai Server
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(5)
            self.log_message(f'[SISTEM] Peladen berjalan di {host}:{port}')
            self.start_button.config(state='disabled')
            threading.Thread(target=self.accept_connections, daemon=True).start()
            messagebox.showinfo('Ingfo', f'Peladen berhasil diaktifkan\n{host}:{port}')
        except Exception as e:
            messagebox.showerror('Galat', f'{e}')
            self.log_message(f'[SISTEM] Galat saat memulai Peladen: {e}')

if __name__ == '__main__':
    print('Peladen Perpesanan Lokal (Pesan Privat)')
    root = tk.Tk()
    app = ChatServerGUI(root)
    root.mainloop()
