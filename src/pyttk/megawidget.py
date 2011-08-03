# -*- encoding:latin-1 -*-

'''
Copyright® 2010, THOORENS Bruno
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.
* Neither the name of the *Pytools* nor the names of its contributors may be
used to endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''
from pyTtk import *
import calendar, datetime
from time import strptime

# TODO : set a case-sensitive option for autoentry
#        encoding problem for autoentry
# TODO : use arrow key to navigate in calendar

# ==================================================================================================
class Scrolledframe(Frame):
	"""
	"""
	# width and height of Scrolledframe
	W = 1
	H = 1
	# top left corner coordinates of client frame
	client_x = 0
	client_y = 0
	# width and height of client frame
	client_w = 1
	client_h = 1
	# scrollincrements
	xscrollincrement = 5
	yscrollincrement = 5
	# stretches
	stretch = False
	stretch_x = False
	stretch_y = False

	xscrollcommand = lambda *args: None
	yscrollcommand = lambda *args: None
# ==================================================================================================
	def configure(self, cnf = {}, **kw):
		cnf = dict(cnf, **kw)
		for key in cnf.keys():
			Frame.configure(self, **{key:cnf[key]}) if not hasattr(self, key) else setattr(self, key, cnf[key])
	__setitem__ = lambda self, item, value: self.configure({item : value})

	def cget(self, item):
		return Frame.cget(self, item) if not hasattr(self, item) else getattr(self, item)
	__getitem__ = cget

	def __call__(self):
		return self.client

	def __init__(self, master = None, cnf = {}, **kw):
		cnf = dict(cnf, **kw)
		self.stretch = False if "stretch" not in cnf else cnf.pop("stretch")

		Frame.__init__(self, master, cnf, **kw)
		self.client = Frame(self, **cnf)
		self.configure(border = 0, padding = 0, relief = "flat")
		self.client.columnconfigure(0, weight = 1)
# 		self.client.rowconfigure(0, weight = 1)

		self.bind("<Expose>", self.update_scrollregion)

	def xview(self, event, value, units = 'pages'):
		if event == "moveto":
			fraction = float(value)
			if fraction <= 0.0:self.client_x = 0
			elif fraction >= float(self.client_w - self.W) / self.client_w:self.client_x = self.W - self.client_w
			else:self.client_x = int( -self.client_w * fraction)
		elif event == "scroll":
			amount = int(value)
			if self.client_x == 0 and amount < 0:return
			if self.client_x == self.W - self.client_w and amount > 0:return
			self.client_x = self.client_x - (amount * self.xscrollincrement if units == "units" else amount * self.W*0.99)
		else:return

		self.update_scrollx()
		self.client.place_configure(x = self.client_x)

	def yview(self, event, value, units = 'pages'):
		if event == "moveto":
			fraction = float(value)
			if fraction <= 0.0:self.client_y = 0
			elif fraction >= float(self.client_h - self.H) / self.client_h:self.client_y = self.H - self.client_h
			else:self.client_y = int( -self.client_h * fraction)
		elif event == "scroll":
			amount = int(value)
			if self.client_y == 0 and amount < 0:return
			if self.client_x == self.H - self.client_h and amount > 0:return
			self.client_y = self.client_y - (amount * self.yscrollincrement if units == "units" else amount * self.H)
		else:return

		self.update_scrolly()
		self.client.place_configure(y = self.client_y)

	def update_scrollx(self, *args):
		low = 0.0 if self.client_x >= 0 else  -float(self.client_x) / self.client_w
		high = 1.0 if self.client_x + self.client_w <= self.W else low + float(self.W) / self.client_w
		if low <= 0.0:
			self.client_x = 0
		elif high >= 1.0:
			self.client_x = self.W - self.client_w
			low =  -float(self.client_x) / self.client_w
		self.stretch_x = self.stretch if (self.client_w < self.W) else False
		self.xscrollcommand(low, high)

	def update_scrolly(self, *args):
		low = 0.0 if self.client_y >= 0 else -float(self.client_y) / self.client_h
		high = 1.0 if self.client_y + self.client_h <= self.H else low + float(self.H) / self.client_h
		if low <= 0.0:
			self.client_y = 0
		elif high >= 1.0:
			self.client_y = self.H - self.client_h
			low = -float(self.client_y) / self.client_h
		self.stretch_y = self.stretch if (self.client_h < self.H) else False
		self.yscrollcommand(low, high)

	def update_scrollregion(self, *args):
		if len(self.client.children):
			self.client_w = self.client.winfo_reqwidth()
			self.client_h = self.client.winfo_reqheight()

			self.W = self.winfo_width()
			self.H = self.winfo_height()

			self.update_scrolly()
			self.update_scrollx()

			self.client.place_configure(
				anchor = "nw",
				y = self.client_y, height = self.H if self.stretch_y else self.client_h,
				x = self.client_x, width = self.W if self.stretch_x else self.client_w
			)
		else:
			self.xscrollcommand(0.0, 1.0)
			self.yscrollcommand(0.0, 1.0)
			self.client.place_forget()
# ==================================================================================================

# # ==================================================================================================
# class AutoEntry(Entry):
# 	"""
# 	"""
# # ==================================================================================================
# 	def set_completion(self, iterator):
# 		self.bind("<KeyPress>", lambda event: self.after_idle(self.completion, event, iterator))
#
# 	def completion(self, event, possibilities):
#
# 		if len(event.char) > 1 or event.char in "\t\n\r" or event.char == "" or ord(event.char) in (8,):
# 			return
#
# 		idx = self.tk.call(self._w, 'index', '')
# 		start = unicode(self.get()[:idx+1])
# 		search = sorted(elem for elem in possibilities if unicode(elem[:len(start)]) == start)
#
# 		if len(search):
# 			self.insert(idx, search[0][idx:])
# 			self.selection_range(idx, "end")
# 			self.icursor(idx)

# ==================================================================================================
class CalendarFrame(Frame):
	"""
	"""

	_calendar = calendar.Calendar()

	# icon set
	backward = \
	"R0lGODlhEAAQAOMMAAwMDBwbHBscHC4vLy8vL0RERFtbW3Nzc3NzdHR0c4yLjIyMi////////////////yH5BAEKAA8ALAAAAAAQABAAAAQo8MlJq7046z0X"\
	"VVoyIYdmSEaqFU/hshkhEYOcCVOAZwDVc8CgcBiMAAA7"
	foreward = \
	"R0lGODlhEAAQAOMNAAwMDBsbHBwbHBscGy4uLy4vLi8vL0RERFtbW1tcXHNzc3RzdIyMjP///////////yH5BAEKAA8ALAAAAAAQABAAAAQo8MlJq7046z0Z"\
	"9ZmiTIuGnFKiHezxuBlhGFKhCcE0aADVc8CgcBiMAAA7"
	left = \
	"R0lGODlhEAAQAOMMAA0NDR4eHx8fHzQzMzQzNDM0NEtLS0xLS2VlZX+Af4CAf5qZmv///////////////yH5BAEKAA8ALAAAAAAQABAAAAQf8MlJq704630X"\
	"l4nyISR3HIbxEUPxPYHwPsBs33j+RAA7"
	right = \
	"R0lGODlhEAAQAOMNAA4NDh8eHh8eHzQ0MzQ0NExLS0xLTEtMS0xMTGVlZYB/f3+AgJqamv///////////yH5BAEKAA8ALAAAAAAQABAAAAQf8MlJq704600Z"\
	"n8ryPUn5HQVicAQxfEIwAmNt33gWAQA7"

	# return current date
	get = lambda self: self.date
	more_one_year = lambda self: self.fill(datetime.date(self.date.year +1, self.date.month, self.date.day))
	minus_one_year = lambda self: self.fill(datetime.date(self.date.year -1 , self.date.month, self.date.day))
# ==================================================================================================
	getvalue = lambda self: str(self.date)
	getformatedvalue = lambda self: self.date.strftime(self.format)
	def __init__(self, master = None, cnf = {}, **kw):
		cnf = dict( cnf, **kw)
		# search for a date - format definition in cnf or in kw
		# %a Locale's abbreviated weekday name
		# %A Locale's full weekday name
		# %b Locale's abbreviated month name
		# %B Locale's full month name
		# %c Locale's appropriate date and time representation
		# %d Day of the month as a decimal number [01,31]
		# %j Day of the year as a decimal number [001,366]
		# %m Month as a decimal number [01,12]
		# %x Locale's appropriate date representation
		# %y Year without century as a decimal number [00,99]
		# %Y Year with century as a decimal number
		self.format = cnf.pop("format") if "format" in cnf else "%x"
		# search for a week day definition
		self.days = cnf.pop("days") if "days" in cnf else list(["lu", "ma", "me", "je", "ve", "sa", "di"])
		# search for date
		self.date = cnf.pop("date") if "date" in cnf else datetime.date.today()

		Frame.__init__(self, master, cnf)
		self.columnconfigure(2, weight = 1)
		self.rowconfigure(1, weight = 1)

		self.var = Tkinter.StringVar(self)
		self.content = Frame(self, padding = 0, border = 0)
		self.content.rowconfigure(0, weight = 0)
		self.content.grid(row = 1, column = 0, sticky = "new", columnspan = 5)

		# here the head User Interface with arrow button and date entry
		# for time navigation
		action_button_cnf = {
			"style": "action.Toolbutton",
			"width": -1,
			"padding": (2,0),
			"anchor": "center",
			"font": ("tahoma", "8", "bold"),
			"background": self["background"]
		}
		Button(self, action_button_cnf, takefocus = False, image = CalendarFrame.backward, command = self.minus_one_year).grid(row = 0, column = 0, sticky = "nesw")
		Button(self, action_button_cnf, takefocus = False, image = CalendarFrame.left, command = self.minus_one_month) .grid(row = 0, column = 1, sticky = "nesw")
		self.entry = Entry(self, textvariable = self.var, justify = "center", width = 0, padding = (1, 0))
		self.entry.grid(row = 0, column = 2, sticky = "nesw", padx = 3, pady = 3)
		self.entry.bind("<FocusOut>", self.set_date)
		Button(self, action_button_cnf, takefocus = False, image = CalendarFrame.right, command = self.more_one_month) .grid(row = 0, column = 3, sticky = "nesw")
		Button(self, action_button_cnf, takefocus = False, image = CalendarFrame.foreward, command = self.more_one_year).grid(row = 0, column = 4, sticky = "nesw")

		days_cnf = {
			"pqdding": 0,
			"anchor": "center",
			"width": 0,
			"font": ("tahoma", "8", "bold")
		}
		for day in self.days[:-2]:
			column = self.days.index(day)
			Label(self.content, days_cnf, text = day).grid(row = 0, column = column, sticky = "nesw")
			self.content.columnconfigure(column, minsize = 26)
		for day in self.days[-2:]:
			column = self.days.index(day)
			Label(self.content, days_cnf, text = day, background = "SystemHighlight", foreground = "SystemHighlightText").grid(row = 0, column = column, sticky = "nesw")
			self.content.columnconfigure(column, minsize = 26)

		# fill the dalendar at the current date
		self.fill(self.date)

	def set_date(self, *args):
		try:
			year, month, day = strptime(self.entry.get(), self.format)[:3]
			self.fill(datetime.date(year, month, day))
			self.entry["foreground"] = "black"
		except:
			self.entry["foreground"] = "red"

	def more_one_month(self):
		month, year = (1, self.date.year +1) if self.date.month == 12 else (self.date.month +1, self.date.year)
		try:
			self.fill(datetime.date(year, month, self.date.day))
		except ValueError:
			self.fill(datetime.date(year, month, self.date.day - 3))

	def minus_one_month(self):
		month, year = (12, self.date.year -1) if self.date.month == 1 else (self.date.month -1, self.date.year)
		try:
			self.fill(datetime.date(year, month, self.date.day))
		except ValueError:
			self.fill(datetime.date(year, month, self.date.day - 3))

	def clear(self):
		self.entry.delete(0, "end")
		columns, rows = self.content.grid_size()
		for row in range(1, rows):
			for widget in self.content.grid_slaves(row = row):
				widget.destroy()

	def fill(self, date, end = False):
		self.entry["foreground"] = "black"
		self.clear()
		self.date = date

		year = self.date.year
		month = self.date.month
		day = self.date.day
		self.entry.delete(0, "end")
		self.entry.insert(0, self.date.strftime(self.format))

		row = 0
		for num, column in CalendarFrame._calendar.itermonthdays2(year, month):
			row += 1 if column == 0 else 0
			config = {"width": -1, "padding": (0,-2), "anchor": "center", "takefocus": False}

			if column < 5: config.update(background = "SystemButtonFace", foreground = "SystemButtonText", style = "custom.TButton")
			else:          config.update(background = "SystemHighlight", foreground = "SystemHighlightText", style = "weekend.TButton")

			if num == day: config.update(text = num, style = "custom.TLabel", font = ("tahoma", "7", "bold"))
			elif num == 0: config.update(text = "", style = "custom.TLabel", font = ("tahoma", "7")) #, command = lambda arg = num: self.fill(datetime.date(year, month, arg)))
			else:          config.update(text = num, command = lambda arg = num: self.fill(datetime.date(year, month, arg), True))

			(Button if num != 0 else Label)(self.content, config).grid(row = row, column = column, sticky = "nsew")
			self.content.rowconfigure(row, minsize = 18)

		if row <= 5:
			for j in range(row, 6):
				self.content.rowconfigure(j+1, minsize = 18)
				for i in range(7):
					Label(
						self.content,
						background = "SystemButtonFace" if i < 5 else "SystemHighlight",
						foreground = "SystemButtonText" if i < 5 else "SystemHighlightText",
						padding = (0,-2)
					).grid(row = j+1, column = i, sticky = "nesw")

		if end and self.winfo_toplevel().overrideredirect():
			self.winfo_toplevel().withdraw()
