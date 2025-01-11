import sys, os
import socket
import json
import tkinter as tk


def resource_path(relative_path):
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	return os.path.join(base_path, relative_path)

def AppData(relative_path):
	data_dir = os.path.join(os.getenv('APPDATA'), 'Fast Server')
	os.makedirs(data_dir, exist_ok=True)
	return os.path.join(data_dir, relative_path)

def load_settings():
	file = AppData("settings.json")
	if os.path.exists(file):
		with open(AppData("settings.json"), 'r') as f:
			return json.loads(f.read())
	return {}

def save_settings(settings):
	with open(AppData("settings.json"), 'w') as f:
		f.write(json.dumps(settings, indent=4, ensure_ascii=False))

def get_host(host=""):
	if host == "0.0.0.0":
		return socket.gethostbyname(socket.gethostname())
	if host == "localhost" or not host:
		return "127.0.0.1"
	return host

class EntryWithPlaceholder(tk.Entry):
	def __init__(self, master, placeholder, color='grey'):
		super().__init__(master)
		self.placeholder = placeholder
		self.placeholder_color = color
		self.default_fg_color = self['fg']
		self.bind("<FocusIn>", self.foc_in)
		self.bind("<FocusOut>", self.foc_out)
		self.original_insert = self.insert
		self.insert = self.custom_insert
		self.put_placeholder()

	def put_placeholder(self):
		self.insert(0, self.placeholder)
		self['fg'] = self.placeholder_color

	def custom_insert(self, position, value):
		if value:
			self.delete(0, 'end')
			self['fg'] = self.default_fg_color
			self.original_insert(position, value)
		else:
			self.put_placeholder()

	def foc_in(self, *args):
		if self['fg'] == self.placeholder_color:
			self.delete(0, 'end')
			self['fg'] = self.default_fg_color

	def foc_out(self, *args):
		if not self.get(): self.put_placeholder()
