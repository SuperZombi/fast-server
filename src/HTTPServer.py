from infi.systray import SysTrayIcon
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
import webbrowser as wbr
import sys, os
import tkinter as tk
from urllib.parse import urlparse
from utils import *


SETTINGS = {
	"host": "localhost",
	"port": 8000,
	"root": "index"
}
SETTINGS.update(load_settings())

def start_gui(_):
	def save_data():
		new_host = host_entry.get()
		new_port = int(port_entry.get())
		root_path = directory_behavior.get()
		root.destroy()
		SETTINGS.update({"host": new_host, "port": new_port, "root": root_path})
		save_settings(SETTINGS)
		print("Restarting server...")
		Thread(target=lambda:SERVER.shutdown(), daemon=True).start()
		Thread(target=start_server, daemon=True).start()

	def inset_url(host, port):
		host_entry.delete(0, 'end')
		port_entry.delete(0, 'end')
		host_entry.insert(0, host)
		port_entry.insert(0, port)

	root = tk.Tk()
	root.title("Settings")
	root.iconbitmap(icons["main"])

	###
	frame1 = tk.Frame(root)
	frame1.pack(pady=(10,5))

	local_button = tk.Button(frame1, text="Local", command=lambda: inset_url("localhost", 8000))
	local_button.pack(padx=5, side=tk.LEFT)

	public_button = tk.Button(frame1, text="Global", command=lambda: inset_url("0.0.0.0", 80))
	public_button.pack(padx=5, side=tk.LEFT)

	###
	grid2 = tk.Frame(root)
	grid2.pack()

	tk.Label(grid2, text="Host:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
	host_entry = EntryWithPlaceholder(grid2, placeholder="localhost")
	host_entry.grid(row=0, column=1, padx=10, pady=5)
	host_entry.insert(0, SETTINGS.get("host"))

	tk.Label(grid2, text="Port:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
	port_entry = tk.Entry(grid2)
	port_entry.grid(row=1, column=1, padx=10, pady=5)
	port_entry.insert(0, SETTINGS.get("port"))

	###
	directory_behavior = tk.StringVar(value=SETTINGS.get("root"))
	tk.Label(grid2, text="Root:").grid(row=2, column=0, padx=10, pady=5, sticky="en")

	grid3 = tk.Frame(grid2)
	grid3.grid(row=2, column=1, padx=10, pady=5, sticky="w")

	show_index_rb = tk.Radiobutton(grid3, text="index.html", variable=directory_behavior, value="index")
	show_index_rb.pack(anchor="w")

	show_directory_rb = tk.Radiobutton(grid3, text="Directory", variable=directory_behavior, value="directory")
	show_directory_rb.pack(anchor="w")

	###
	save_button = tk.Button(root, text="   Save   ", command=save_data)
	save_button.pack(pady=5)
	root.mainloop()


class MyServer(HTTPServer):
	def get_address(self):
		return self.socket.getsockname()[:2]
	def get_host_url(self):
		host, port = self.get_address()
		return f"http://{host}:{port}/"


class MyRequestHandler(SimpleHTTPRequestHandler):
	def do_GET(self):
		URL = urlparse(self.path)
		path = self.translate_path(URL.path)
		if URL.path.endswith("/"):
			if SETTINGS.get("root") == "index":
				self.path = URL.path + 'index.html'
			else:
				return self.copyfile(list_directory(path, URL.path), self.wfile)
		else:
			if not os.path.exists(path):
				self.path = URL.path + '.html'

		f = self.send_head()
		if f:
			try:
				self.copyfile(f, self.wfile)
			finally:
				f.close()

SERVER = None
def start_server():
	global SERVER
	SERVER = MyServer((get_host(SETTINGS.get("host")), SETTINGS.get("port")), MyRequestHandler)
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

Thread(target=start_server, daemon=True).start()
