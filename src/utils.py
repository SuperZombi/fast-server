import sys, os
import socket
import json
import tkinter as tk
import io
import urllib


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

def get_files_and_folders(path):
	files = []
	folders = []
	for item in os.listdir(path):
		full_path = os.path.join(path, item)
		if os.path.isdir(full_path):
			folders.append(item)
		elif os.path.isfile(full_path):
			files.append(item)
	return files, folders

def list_directory(path, urlpath):
	files, folders = get_files_and_folders(path)

	folders_html = ""
	for folder in folders:
		folders_html += f"<li>📁<a href='{folder}/'>{folder}/</a></li>"

	files_html = ""
	for file in files:
		folders_html += f"<li>🗎<a href='{file}'>{file}</a></li>"

	nothing = "<p>¯\\_(ツ)_/¯</p>"
	html = f"""
	<!DOCTYPE html>
	<html>
	<head>
		<title>Directory listing</title>
		<meta http-equiv='Content-Type' content='text/html; charset=utf-8'/>
		<meta name='viewport' content='width=device-width'>
	</head>
	<body>
		<h2>{urllib.parse.unquote(urlpath)}</h2>
		<hr>
		<ul>
			{"<li><a href='../'>↩</a></li>" if urlpath != "/" else ""}
			{nothing if (not folders_html and not files_html) else ""}
			{folders_html}
			{files_html}
		</ul>
	</body>
	</html>
	"""
	f = io.BytesIO()
	f.write(bytes(html, 'utf-8'))
	f.seek(0)
	return f

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
