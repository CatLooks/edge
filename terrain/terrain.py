from threading import Thread
from tkinter.messagebox import *
from tkinter.simpledialog import *
from tkinter.filedialog import *
from tkinter import *
import pygame as py

py.init()

rainbow_colors = (
	(255, 0, 0),
	(255, 128, 0),
	(255, 255, 0),
	(128, 255, 0),
	(0, 255, 0),
	(0, 255, 128),
	(0, 255, 255),
	(0, 128, 255),
	(0, 0, 255),
	(128, 0, 255),
	(255, 0, 255),
	(255, 0, 128)
)

pallete = (
	(128, 255, 255), #0
	(255, 255, 255), #1
	(255, 255, 128), #2
	(255, 160, 255), #3
	(255, 160, 128), #4
	(255, 96, 255),  #5
	(255, 96, 128),  #6
	(255, 0, 255),   #7
	(255, 0, 128),   #8
	(255, 255, 0)    #9
)

def cnv(s, a, b):
	try:
		v = int(float(s.get()))
	except:
		v = a

	if v < a:
		v = a
	elif v > b:
		v = b

	s.delete(0, "end")
	s.insert(0, str(v))
	return v

class Level:
	data = [[[(0, 0, 0)]]]
	x, y, z = 1, 1, 1

	@classmethod
	def updateSize(cls, s):
		sx = s[0] << 8 | s[1]
		sy = s[2] << 8 | s[3]
		sz = s[4]
		new = []

		for z in range(sz):
			new.append([])
			for y in range(sy):
				new[z].append([])
				for x in range(sx):
					new[z][y].append((0, 0, 0))

		for z in range(cls.z):
			for y in range(cls.y):
				for x in range(cls.x):
					c = cls.get(x, y, z)
					if c:
						try:
							new[z][y][x] = c
						except:
							pass

		cls.data = new
		cls.x = sx
		cls.y = sy
		cls.z = sz

	@classmethod
	def set(cls, x, y, z, t):
		try:
			cls.data[z][y][x] = t
		except:
			pass
	
	@classmethod
	def get(cls, x, y, z):
		try:
			return cls.data[z][y][x]
		except:
			return

	@classmethod
	def open(cls):
		print("Open:")
		path = input("> ").strip()

		if path == "":
			return

		with open(path, "rb") as f:
			file = f.read()

		if len(file) < 6:
			showerror("Error", "Invalid Terrain Sum File")
			return

		name = file[5:].decode("raw-unicode-escape")
		size = file[0] << 8 | file[1], file[2] << 8 | file[3], file[4]
		layers = []

		try:
			for z in range(size[2]):
				layer = py.image.load(name + ".%s.png" % z)
				if layer.get_size() != size[:2]:
					showerror("Error", "Layer %s has invalid size" % z)
					return
				layers.append(layer)
		except:
			showerror("Error", "Failed to open layer %s" % z)
			return

		Controller.setSize(*size)
		Level.updateSize(file[:5])

		for z in range(size[2]):
			for y in range(size[1]):
				for x in range(size[0]):
					Level.set(x, y, z, layers[z].get_at((x, y))[:3])

	@classmethod
	def save(cls):
		print("Save:")
		path = input("> ").strip()
		if path == "":
			return

		name = input("> ").strip()
		if name == "":
			return

		try:
			with open(path, "wb+") as f:
				f.write(Level.x.to_bytes(2, "big"))
				f.write(Level.y.to_bytes(2, "big"))
				f.write(Level.z.to_bytes(1, "big"))
				f.write(bytes(name, "raw-unicode-escape"))
		except:
			showerror("Error", "Invalid save filename")
			return

		for z in range(Level.z):
			s = py.Surface((Level.x, Level.y))
			for y in range(Level.y):
				for x in range(Level.x):
					s.set_at((x, y), Level.get(x, y, z))
			try:
				py.image.save(s, "%s.%s.png" % (name, z))
			except:
				showerror("Error", "Failed to save layer %s" % z)
				return

class Controller:
	color = bytearray(3)
	size = bytearray(5)

	@classmethod
	def updateColor(cls):
		cls.color[0] = cnv(w.tkw.s4, 0, 255)
		cls.color[1] = cnv(w.tkw.s5, 0, 255)
		cls.color[2] = cnv(w.tkw.s6, 0, 255)

		w.tkw.c1.itemconfig(w.tkw.col, fill="#%02x%02x%02x" % tuple(cls.color))

	@classmethod
	def setColor(cls, c):
		cls.color[0] = c[0]
		cls.color[1] = c[1]
		cls.color[2] = c[2]

		w.tkw.s4.delete(0, "end")
		w.tkw.s5.delete(0, "end")
		w.tkw.s6.delete(0, "end")

		w.tkw.s4.insert(0, str(c[0]))
		w.tkw.s5.insert(0, str(c[1]))
		w.tkw.s6.insert(0, str(c[2]))

		w.tkw.c1.itemconfig(w.tkw.col, fill="#%02x%02x%02x" % tuple(cls.color))

	@classmethod
	def updateSize(cls):
		x = cnv(w.tkw.s1, 1, 32767)
		y = cnv(w.tkw.s2, 1, 32767)
		z = cnv(w.tkw.s3, 1, 255)

		cls.size[0] = x // 256
		cls.size[1] = x % 256
		cls.size[2] = y // 256
		cls.size[3] = y % 256
		cls.size[4] = z

		Level.updateSize(cls.size)

	@classmethod
	def setSize(cls, x, y, z):
		w.tkw.s1.delete(0, "end")
		w.tkw.s2.delete(0, "end")
		w.tkw.s3.delete(0, "end")
		w.tkw.s1.insert(0, str(x))
		w.tkw.s2.insert(0, str(y))
		w.tkw.s3.insert(0, str(z))

		cls.size[0] = x // 256
		cls.size[1] = x % 256
		cls.size[2] = y // 256
		cls.size[3] = y % 256
		cls.size[4] = z

		Level.updateSize(cls.size)

class TkWindow:
	def __init__(self):
		self.root = Tk()
		self.root.resizable(0, 0)
		self.root.title("Details")

		self.l1 = Label(self.root, text="X")
		self.l2 = Label(self.root, text="Y")
		self.l3 = Label(self.root, text="Z")
		self.s1 = Spinbox(self.root, from_=1, to=32767, width=6)
		self.s2 = Spinbox(self.root, from_=1, to=32767, width=6)
		self.s3 = Spinbox(self.root, from_=1, to=255, width=6)
		self.b1 = Button(self.root, text="Update Size", command=Controller.updateSize)

		self.l4 = Label(self.root, text="R")
		self.l5 = Label(self.root, text="G")
		self.l6 = Label(self.root, text="B")
		self.s4 = Spinbox(self.root, from_=0, to=255, width=6, command=Controller.updateColor)
		self.s5 = Spinbox(self.root, from_=0, to=255, width=6, command=Controller.updateColor)
		self.s6 = Spinbox(self.root, from_=0, to=255, width=6, command=Controller.updateColor)
		self.c1 = Canvas(self.root, width=160, height=32)

		self.l1.grid(column=0, row=0)
		self.l2.grid(column=1, row=0)
		self.l3.grid(column=2, row=0)
		self.s1.grid(column=0, row=1)
		self.s2.grid(column=1, row=1)
		self.s3.grid(column=2, row=1)
		self.b1.grid(column=0, row=2, columnspan=3, sticky="we")

		self.l4.grid(column=0, row=3)
		self.l5.grid(column=1, row=3)
		self.l6.grid(column=2, row=3)
		self.s4.grid(column=0, row=4)
		self.s5.grid(column=1, row=4)
		self.s6.grid(column=2, row=4)
		self.c1.grid(column=0, row=6, columnspan=3, sticky="we")

		self.col = self.c1.create_rectangle((0, 0, 160, 32), fill="#000000")

	def loop(self):
		self.root.mainloop()
		w.running = False

class PyWindow:
	def __init__(self):
		py.display.set_caption("Terrain")
		self.win = py.display.set_mode((720, 480))

		self.font = py.font.SysFont("courier", 16)
		self.clock = py.time.Clock()

		self.tkw = TkWindow()
		self.running = True

	def loop(self):
		pos = [0, 0]
		z = 0

		rainbow = 0

		while self.running:
			mouse = py.mouse.get_pos()
			keys = py.key.get_pressed()

			mx, my = mouse[0] // 16, mouse[1] // 16

			for evt in py.event.get():
				if evt.type == py.QUIT:
					Level.save()
				if evt.type == py.KEYDOWN:
					if keys[py.K_LCTRL] or keys[py.K_LALT]:
						if evt.key == py.K_s:
							Level.save()
						elif evt.key == py.K_o:
							Level.open()

					if py.K_0 <= evt.key <= py.K_9:
						Controller.setColor(pallete[evt.key - 0x30])

					if evt.key == py.K_UP:
						if pos[1] < Level.y - 30:
							pos[1] += 1
					if evt.key == py.K_DOWN:
						if pos[1] > 0:
							pos[1] -= 1
					if evt.key == py.K_LEFT:
						if pos[0] < Level.x - 45:
							pos[0] += 1
					if evt.key == py.K_RIGHT:
						if pos[0] > 0:
							pos[0] -= 1

					if evt.key == py.K_q:
						if z < Level.z - 1:
							z += 1
					if evt.key == py.K_a:
						if z > 0:
							z -= 1

			m = py.mouse.get_pressed()
			
			if m[2]:
				Level.set(mx + pos[0], my + pos[1], z, tuple(Controller.color))
			elif m[0]:
				Level.set(mx + pos[0], my + pos[1], z, (0, 0, 0))

			self.win.fill((32, 32, 32))

			for y in range(30):
				for x in range(45):
					c = Level.get(x + pos[0], y + pos[1], z)
					if c:
						py.draw.rect(self.win, c, (x * 16, y * 16, 16, 16))

			py.draw.rect(self.win, rainbow_colors[rainbow // 6], (mx * 16, my * 16, 16, 16), 1)

			pos_text = self.font.render("%s, %s, %s" % (pos[0] + mx, pos[1] + my, z), 1, (255, 255, 255), (32, 32, 32))
			self.win.blit(pos_text, (720 - pos_text.get_width(), 0))

			rainbow = (rainbow + 1) % 72

			py.display.flip()
			self.clock.tick(60)

	def run(self):
		self.th = Thread(target=self.loop)
		self.th.start()
		self.tkw.loop()

w = PyWindow()
w.run()