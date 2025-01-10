from infi.systray import SysTrayIcon
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
import webbrowser as wbr
import socket
import sys, os
import tkinter as tk


def resource_path(relative_path):
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	return os.path.join(base_path, relative_path)

def get_host(host=""):
	if host == "0.0.0.0":
		return socket.gethostbyname(socket.gethostname())
	if host == "localhost" or not host:
		return "127.0.0.1"
	return host


def start_gui(_):
	def save_data():
		new_host = host_entry.get()
		new_port = int(port_entry.get())
		root.destroy()
		print("Restarting server...")
		SERVER.shutdown()
		Thread(target=start_server, args=(new_host, new_port), daemon=True).start()

	current_host, current_port = SERVER.get_address()

	root = tk.Tk()
	root.title("Settings")
	root.iconbitmap(icons["main"])

	root.grid_columnconfigure(0, weight=1)
	root.grid_columnconfigure(1, weight=1)

	tk.Label(root, text="Host:").grid(row=0, column=0, padx=10, pady=10)
	host_entry = tk.Entry(root)
	host_entry.grid(row=0, column=1, padx=10, pady=10)
	host_entry.insert(0, current_host)

	tk.Label(root, text="Port:").grid(row=1, column=0, padx=10, pady=10)
	port_entry = tk.Entry(root)
	port_entry.grid(row=1, column=1, padx=10, pady=10)
	port_entry.insert(0, current_port)

	save_button = tk.Button(root, text="Save", command=save_data)
	save_button.grid(row=2, column=0, columnspan=2, pady=10)

	root.mainloop()


class MyServer(HTTPServer):
	def get_address(self):
		return self.socket.getsockname()[:2]
	def get_host_url(self):
		host, port = self.get_address()
		return f"http://{host}:{port}/"


class MyRequestHandler(SimpleHTTPRequestHandler):
	def do_GET(self):
		if self.path.endswith("/"):
			self.path = self.path + 'index.html'

		f = self.send_head()
		if f:
			try:
				self.copyfile(f, self.wfile)
			finally:
				f.close()

SERVER = None
def start_server(host, port):
	global SERVER
	SERVER = MyServer((get_host(host), port), MyRequestHandler)
	print(f"Serving on {SERVER.get_host_url()}")
	try:
		SERVER.serve_forever()
	except KeyboardInterrupt:
		sys.exit(0)

icons = {"main": resource_path("server.ico")}
menu_options = (
	("Open in Browser", None, lambda _: wbr.open(SERVER.get_host_url())),
	("Setting", None, start_gui)
)
systray = SysTrayIcon(icons["main"], "HTTP Server", menu_options, on_quit=lambda _: os._exit(0))
systray.start()

Thread(target=start_server, args=("", 8000), daemon=True).start()
