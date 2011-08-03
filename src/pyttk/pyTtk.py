# -*- coding:latin-1 -*-
"""
(~) http://pyttk.googlecode.com

Copyright® 2006, THOORENS Bruno
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
"""

#TODO :: document and comment all functions and classes

import os, sys

# Tkinter library of python 2.5 is moved to tkinter package in python 2.6+ -> 3.0+
try: import Tkinter
except: import tkinter as Tkinter

# shortcuts
Tk = Tkinter.Tk
mainloop = Tkinter.mainloop
Toplevel = Tkinter.Toplevel
TclError = Tkinter.TclError

_TILE_LOADED = False
# tk 8.5 already included in Python 2.6+
if float(sys.version[:3]) > 2.5: _TILE_LOADED = True

# PIL image increment
_nbPILimg = 0

# loads Tile package
def loadttk(tk):
	# append "[pyTtk.py path]/tcl" to AUTO_PATH in order to find Tile package here
	ttk_path = os.path.join(os.path.dirname(__file__), "tcl")
	if tk.eval("lsearch auto_path {%s}" % ttk_path) == "-1":
		tk.eval("lappend auto_path {%s}" % ttk_path)
	return tk.call("package", "require", "tile")

def customize_all_widgets(value):
	TtkWidget.extend = bool(value)

def _style(widget_or_style):
	return Tkinter.BaseWidget.cget(widget_or_style,"style") if hasattr(widget_or_style, "tk") else \
	       widget_or_style

def _img_statespec(arg):
	"""
	"""
	result = "%s" % _img(arg[0])
	if len(arg) > 1:
		statespec = arg[1] if type(arg[1]) == type({}) else {}
		for key in statespec:
			result += " {%s} %s" % (key, _img(statespec[key]))
	return result

def _img(img, name = None):
	"""
	This fonction simplify the image definition of widget, img can be
	 - a PIL Tkimage
	 - a tk image name
	 - a base64 string
	 - a pathfile

	 - an _img_statespec image
	 """

	global _nbPILimg

	if type(img) == type(()):
		return _img_statespec(img)

	else:
		# check if it is a PIL tkimage and save it into _default_root to keep
		# a reference and avoid the PIL bug
		if hasattr(img, "tk"):
			_nbPILimg = _nbPILimg + 1
			setattr(Tkinter._default_root, "PILimg%03d" % _nbPILimg, img)

		# if image is not already defined in tk-image namespace create one
		# from base64 encoded file or directly from pathfile
		elif type(img) == type("") and img not in Tkinter._default_root.tk.call("image", "names"):
			img = Tkinter._default_root.tk.call(
				"image", "create", "photo",
				"-file" if os.path.lexists(img) else "-data",
				img
			)
		return img

def _cnf(cnf = {}, **kw):
	result = dict(cnf, **kw)

	for key in ["ulabel", "utext"]:
		if key in result:
			index = result[key].find("_")
			if index >= 0 and not result[key].endswith("_"):
				result[key[1:]] = result[key][:index] + result[key][index+1:]
				result["underline"] = index
			del result[key]

	if "image" in result and result["image"] != None:
		result["image"] = _img(result["image"])

	if "padding" in result and result["padding"] != None:
		padding = result["padding"]
		if type(padding) == type(0):
			result["padding"] = (padding, ) * 4
		if type(padding) == type(()):
			if len(padding) == 2: result["padding"] = padding * 2
			elif len(padding) == 3: result["padding"] = padding + (0, )

	del cnf, kw
	return result

def _cnfpopstartswith(start, excludes, cnf = {}, **kw):
	new = {}
	for key in [k for k in cnf if k.startswith(start) if k not in excludes]:
		new[key.replace(start, "")] = cnf.pop(key)
	for key in [k for k in kw if k.startswith(start) if k not in excludes]:
		new[key.replace(start, "")] = kw.pop(key)
	return new

# def _filter_cnf(cnf, keys, **add):
# 	for key in (k for k in cnf if k not in keys): cnf.pop(key)
# 	for key in (k for k in add if k not in cnf): cnf[key] = add[key]
# 	return _cnf(cnf)

def _dict(Tcl_pairs):
	Tcl_pairs = tuple(str(elem)[1:] if isinstance(elem, Tkinter._tkinter.Tcl_Obj) else elem for elem in Tcl_pairs)
	return dict((Tcl_pairs[i], Tcl_pairs[i+1]) for i in range(0, len(Tcl_pairs), 2))

# ==================================================================================================
class Style:
	"""
	Each widget is assigned a style, which specifies the set of elements making
	up the widget and how they are arranged, along with dynamic and default settings
	for element options. By default, the style name is the same as the widget's class;
	this may be overridden by the -style option.
	"""
	theme_use = lambda self, themename: self.tk.call("ttk::style", "theme", "use", themename)
	theme_names = lambda self: self.tk.call("ttk::style", "theme", "names")
	element_options = lambda self, element: self.tk.call("ttk::style", "element", "options", element)
	element_names = lambda self: self.tk.call("ttk::style", "element", "names")
# ==================================================================================================
	def __init__(self, master = None):

		global _TILE_LOADED

		if Tkinter._support_default_root:
			if not master:
				if not Tkinter._default_root:
					Tkinter._default_root = Tk()
				master = Tkinter._default_root
		else:
			master = Tk()

		self.master = master
		self.tk = master.tk

		if not _TILE_LOADED:
			_TILE_LOADED = loadttk(self.tk)

	def style_configure(self, widget_or_style, cnf = {}, **kw):
		items = _cnf(cnf, **kw).items()
		style = _style(widget_or_style)

		if not len(items):
			return self.tk.call("ttk::style", "configure", style)

		options = ()
		for key, value in items:
			options += ('-' + (key[:-1] if key[-1] == '_' else key), self._register(value) if hasattr(value, '__call__') else value)
		self.tk.call(("ttk::style", "configure", style) + options)
	configure = style_configure

	def style_map(self, widget_or_style, cnf = {}, **kw):
		items = _cnf(cnf, **kw).items()
		style = _style(widget_or_style)

		options = ()
		for option, statespec_value in items:
			list_ = ""
			if type(statespec_value) == type({}):
				for state in statespec_value:
					list_ += "{%s} %s " % (state, statespec_value[state])
				options += ("-" + option, list_)

		self.tk.call(("ttk::style", "map", style,) + options)
	map = style_map

	def style_lookup(self, widget_or_style, option, states = None):
		return self.tk.call("ttk::style", "lookup", _style(widget_or_style), "-" + option, None if not states else "{%s}" % states)
	lookup = style_lookup

	def style_layout(self, widget_or_style, layout_spec = None):
		return self.tk.call("ttk::style", "layout", _style(widget_or_style), layout_spec)
	layout = style_layout

	def style_element_create(self, name, *imagespec, **options):
		tupple_options = ()
		for key, value in options.items(): tupple_options += ("-" + key , value)
		return self.tk.call(("ttk::style", "element", "create", name, "image", _img_statespec(imagespec)) + tupple_options)
	element_create = style_element_create

# TODO if really needed

# ttk::style theme create themeName ?-parent basedon? ?-settings script... ?
# Creates a new theme. It is an error if themeName already exists. If -parent is
# specified, the new theme will inherit styles, elements, and layouts from the
# parent theme basedon. If -settings is present, script is evaluated in the context
# of the new theme as per ttk::style theme settings.

# ttk::style theme settings themeName script
# Temporarily sets the current theme to themeName, evaluate script, then restore
# the previous theme. Typically script simply defines styles and elements, though
# arbitrary Tcl code may appear.


# ==================================================================================================
class Menu(Tkinter.Menu):
	_nbPILimg = 0
# ==================================================================================================
	def __init__(self, master = None, cnf = {}, **kw):
		Tkinter.Menu.__init__(self, master, cnf, **kw)

		global _TILE_LOADED

		if not _TILE_LOADED:
			_TILE_LOADED = loadttk(self.tk)

	# Tile does not provide Menu widgets. This function is created to allow the new
	# options and ways to manage images.
	def fix_options(self, cnf = {}, **kw):

		cnf = _cnf(cnf, **kw)
		for key in ["selectimage", "bitmap"]:
			if key in cnf:
				# check if cnf[key] is a PIL tkimage and save it into _default_root
				# to keep a reference and avoid the PIL bug
				if hasattr(cnf[key], "tk"):
					Menu._nbPILimg += 1
					setattr(self, "PILimg%03d" % Menu._nbPILimg, cnf[key])
				# if cnf[key] is not already defined in tk-image namespace create one
				# from base64 encoded file or directly from pathfile
				elif type(cnf[key]) == type("") and cnf[key] not in self.tk.call("image", "names"):
					cnf[key] = self.tk.call(
						"image", "create",
						"photo" if "image" in key else "bitmap",
						"-file" if os.path.lexists(cnf[key]) else "-data",
						cnf[key]
					)

		for key in ["ulabel", "utext"]:
			if key in cnf:
				index = cnf[key].find("_")
				if index >= 0 and not cnf[key].endswith("_"):
					cnf[key[1:]] = cnf[key][:index] + cnf[key][index+1:]
					cnf["underline"] = index
				del cnf[key]
		return self._options(cnf)

	# easier ways to insert, add and modify menu items
	def add(self, item, cnf = {}, **kw): return self.tk.call((self._w, "add", item) + self.fix_options(cnf, **kw))
	def insert(self, index, item, cnf = {}, **kw): return self.tk.call((self._w, "insert", index, item) + self.fix_options(cnf, **kw))
	def entryconfigure(self, index, cnf = {}, **kw): return self.tk.call((self._w, 'entryconfigure', index) + self.fix_options(cnf, **kw))
	def clone(self, master = None, name = None, cloneType = "normal"):
		name = "clony" + self._w if name == None else name
		name = (self._w if master == None else master._w) + "." + name
		self.tk.call(self._w, "clone", name, cloneType)
		return name
# ==================================================================================================

# ==================================================================================================
class TtkWidget(Tkinter.BaseWidget):
	"""
	"""
	extend = True
# ==================================================================================================
	def __init__(self, master, widgetName, cnf = {}, kw = {}, extra = ()):
		"""
		"""
		global _TILE_LOADED

		config = {}
		config.update(cnf)
		config.update(kw)

		if "extend" in config: self.extend = bool(config.pop("extend"))

		# initialize
		Tkinter.BaseWidget._setup(self, master, config)

		# load Tile if not already loaded
		if not _TILE_LOADED:
			_TILE_LOADED = loadttk(self.tk)

		# here is a fix for panedwindow widget because of its readonly attribute -orient !
		if "orient" in config.keys():
			self.tk.call(("ttk::" + widgetName, self._w, "-orient", config.pop("orient")) + extra)
		else:
			self.tk.call(("ttk::" + widgetName, self._w) + extra)

		classes = []
		for key in [k for k in config.keys() if isinstance(k, type)]:
			classes.append((key, config.pop(key)))

		# if user does not give explicitly a style (and implicitly wants to extend the widget)
		# we create a style based on widget name to allow customisation of this and only this widget.
		if self.extend and "style" not in config and widgetName not in ["scrollbar", "scale", "panedwindow", "progressbar"]:
			config["style"] = self._name + "." + "T" + widgetName.capitalize()

		# configure widget with given options
		self.configure(config)

		for key, value in classes:
			key.configure(self, value)

	def configure(self, cnf = {}, **kw):
		items = _cnf(cnf, **kw).items()

		# list of widget options != style options
		widget_keys = list(self.keys())

		# builds tupple for widget configuration
		widget_options = ()
		for key, value in [item for item in items if item[0] in widget_keys]:
			widget_options += (
				'-' + (key[:-1] if key[-1] == '_' else key),
				self._register(value) if hasattr(value, '__call__') else value
			)
		self.tk.call((self._w, "configure") + widget_options)

		# appends other options given in cnf and **kw and uses 'ttk::style configure' command.
		# if user explicitly gived a style on initialisation it will affect all widgets of the
		# same style...
		if self.extend:
			widget_style = ()
			for key, value in [item for item in items if item[0] not in widget_keys]:
				widget_style += (
					'-' + (key[:-1] if key[-1] == '_' else key),
					self._register(value) if hasattr(value, '__call__') else value
				)
			self.tk.call(("ttk::style", "configure", self["style"]) + widget_style)

	__setitem__ = lambda self, item, value: self.configure(**{item : value})
	config = configure

	def cget(self, item):
		result = self.tk.call("ttk::style", "lookup", Tkinter.BaseWidget.cget(self,"style"), "-" + item, self.state())
		if result == "":
			try:    result = Tkinter.BaseWidget.cget(self,item)
			except: return None
		return result
	__getitem__ = cget
# ==================================================================================================

# ==================================================================================================
class Widget(TtkWidget, Tkinter.Pack, Tkinter.Place, Tkinter.Grid):
	"""
	"""
	widgetName = None
# ==================================================================================================
	def __init__(self, master = None, cnf = {}, **kw):
		TtkWidget.__init__(self, master, self.widgetName, cnf, kw)

	def identify(self, x, y):
		"""
		Returns the name of the element at position x, y, or the empty
		string if the point does not lie within any element.
		x and y are pixel coordinates relative to the widget.
		"""
		return self.tk.call(self._w, "identify", x, y)

	def instate(self, state, command = None, *args):
		"""
		Test the widget's state. Returns 1 if the widget state matches
		statespec and 0 otherwise.
		"""
		if command: return self.tk.call(self._w, 'instate', state, command, args)
		else: return self.tk.call(self._w, 'instate', state)

	def state(self,state = None):
		"""
		Modify or inquire widget state. Returns a new state spec indicating
		which flags were changed.
		"""
		if state: self.tk.call(self._w, 'state', state)
		else: return self.tk.call(self._w, 'state')
# ==================================================================================================

# ==================================================================================================
class Button(Widget, Tkinter.Button):
	"""
	A button widget displays a textual label and/or image, and evaluates
	a command when pressed.
	"""
	widgetName = "button"
# ==================================================================================================
# ==================================================================================================
class Menubutton(Widget, Tkinter.Menubutton):
	"""
	A menubutton widget displays a textual label and/or image,
	and displays a menu when pressed.
	"""
	widgetName = "menubutton"
	menu = None
# ==================================================================================================
	def __call__(self): return self.menu

	def menu_insert(self, item, index = 0, cnf = {}, **kw):
		if not self.menu:
			self.menu = Menu(self)
			self["menu"] = self.menu
		self.menu.insert(index, item, cnf, **kw)

	def menu_add(self, item, cnf = {}, **kw):
		if not self.menu:
			self.menu = Menu(self)
			self["menu"] = self.menu
		self.menu.add(item, cnf, **kw)

	def menu_modify(self, index, cnf, **kw):
		if self.menu: self.menu.entryconfigure(index, cnf, **kw)

	def menu_option(self, index, option):
		if self.menu: self.menu.entrycget(index, option)

	def menu_delete(self, index1, index2 = None):
		if self.menu: self.menu.delete(index1, index2)

	def menu_configure(self, cnf = {}, **kw):
		if self.menu: return self.menu.configure(cnf, **kw)
# ==================================================================================================
# ==================================================================================================
class Checkbutton(Widget, Tkinter.Checkbutton):
	"""
	A checkbutton widget is used to show or change a setting. It has
	two states, selected and deselected. The state of the checkbuton
	may be linked to a Tcl variable.
	"""
	widgetName = "checkbutton"
# ==================================================================================================
# ==================================================================================================
class Radiobutton(Widget, Tkinter.Radiobutton):
	"""
	Radiobutton widgets are used in groups to show or change a set of
	mutually - exclusive options. Radiobuttons are linked to a Tcl
	variable, and have an associated value; when a radiobutton is clicked,
	it sets the variable to its associated value.
	"""
	widgetName = "radiobutton"
# ==================================================================================================
# ==================================================================================================
class Label(Widget, Tkinter.Label):
	"""
	A label widget displays a textual label and/or image. The label may
	be linked to a Tcl variable to automatically change the displayed text.
	"""
	widgetName = "label"
# ==================================================================================================
# ==================================================================================================
class Scale(Widget, Tkinter.Scale):
	"""
	"""
	widgetName = "scale"
# ==================================================================================================
# ==================================================================================================
class Separator(Widget):
	"""
	A separator widget displays a horizontal or vertical separator bar
	"""
	widgetName = "separator"
# ==================================================================================================
# ==================================================================================================
class Sizegrip(Widget):
	"""
	A sizegrip widget (also known as a grow box) allows the user to resize
	the containing toplevel window by pressing and dragging the grip.
	"""
	widgetName = "sizegrip"
# ==================================================================================================
# ==================================================================================================
class Frame(Widget, Tkinter.Frame):
	"""
	A frame widget is a container, used to group other widgets together.
	"""
	widgetName = "frame"
# ==================================================================================================
# ==================================================================================================
class Labelframe(Widget, Tkinter.LabelFrame):
	"""
	A container used to group other widgets together. It has an optional label,
	which may be a plain text string or another widget.
	"""
	widgetName = "labelframe"
	labelkeys  = ["labelanchor", "labelwidget", "labelmargins", "labeloutside"]
# ==================================================================================================
	def configure(self, cnf = {}, **kw):
		label_cnf = _cnfpopstartswith("label", self.labelkeys, cnf, **kw)

		Widget.configure(self, cnf, **kw)
		self.tk.call(("ttk::style", "configure", self["style"] + ".Label") + self._options(label_cnf))

	def cget(self, item):
		if item.startswith("label") and item not in self.labelkeys:
			result = self.tk.call("ttk::style", "lookup", Widget.cget(self,"style") + ".Label", "-" + item.replace("label", ""))
		else:
			result = self.tk.call("ttk::style", "lookup", Widget.cget(self,"style"), "-" + item, self.state())
		if result == "":
			try:    result = Widget.cget(self,item)
			except: return None
		return result
	__getitem__ = cget
# ==================================================================================================
class Entry(Widget, Tkinter.Entry):
	"""
	An entry widget displays a one-line text string and allows that
	string to be edited by the user. The value of the string may be
	linked to a Tcl variable with the -textvariable option. Entry
	widgets support horizontal scrolling with the standard -xscrollcommand
	option and xview widget command.
	"""
	widgetName="entry"
# ==================================================================================================
# ==================================================================================================
class Combobox(Entry):
	"""
	A combobox combines a text field with a pop-down list of values;
	the user may select the value of the text field from among the
	values in the list.
	"""
	widgetName="combobox"
# ==================================================================================================
	def get(self):
		"""
		Returns the current value of the combobox.
		"""
		return self.tk.call(self._w, 'get')

	def current(self,index=None):
		"""
		If index is supplied, sets the combobox value to the element at
		position index in the list of values. Otherwise, returns the index
		of the current value in the list of values or -1 if the current
		value does not appear in the list.
		"""
		return self.tk.call(self._w, 'current', index)

	def set(self, value):
		"""
		Sets the value of the combobox to value.
		"""
		self.tk.call(self._w, 'set', value)
# ==================================================================================================
# ==================================================================================================
class Scrollbar(Widget, Tkinter.Scrollbar):
	"""
	Scrollbar widgets are typically linked to an associated window
	that displays a document of some sort, such as a file being edited
	or a drawing. A scrollbar displays a thumb in the middle portion
	of the scrollbar, whose position and size provides information about
	the portion of the document visible in the associated window. The thumb
	may be dragged by the user to control the visible region. Depending
	on the theme, two or more arrow buttons may also be present; these are
	used to scroll the visible region in discrete units.
	"""
	widgetName="scrollbar"
# ==================================================================================================
# ==================================================================================================
class Autoscrollbar(Scrollbar):
	"""
	A scrollbar that hides itself if it's not needed. Only works with
	grid geometry manager.
	"""
	# idea from Fredrik Lundh
	# http://effbot.org/zone/tkinter-autoscrollbar.htm
# ==================================================================================================
	def set(self, lo ,hi):
		try:
			if float(lo) <= 0.0 and float(hi) >= 1.0:
				self.grid_remove()
			else:
				self.grid()
			Scrollbar.set(self, lo, hi)
		except:
			pass

	def pack(self, **kw):pass
	def place(self, **kw):pass
# ==================================================================================================
# ==================================================================================================
class Progressbar(Widget):
	"""
	A progress bar widget shows the status of a long-running operation.
	They can operate in two modes: determinate mode shows the amount
	completed relative to the total amount of work to be done, and
	indeterminate mode provides an animated display to let the user
	know that something is happening.
	"""
	widgetName="progressbar"
# ==================================================================================================
	def start(self, interval=50):
		"""
		Begin autoincrement mode: schedules a recurring timer event that
		calls step every interval milliseconds. If omitted, interval
		defaults to 50 milliseconds (20 steps/second).
		"""
		self.tk.call(self._w, 'start', interval)
		self.update()

	def stop(self):
		"""
		Stop autoincrement mode: cancels any recurring timer event initiated
		by self.start.
		"""
		self.tk.call(self._w, 'stop')
		self.update()

	def step(self, amount):
		"""
		Increments the value by amount. amount defaults to 1.0 if omitted.
		"""
		self.tk.call(self._w, 'step', amount)
		self.update()
# ==================================================================================================

# ==================================================================================================
class Notebook(Widget):
	"""
	A notebook widget manages a collection of subpanes and displays
	a single one at a time. Each pane is associated with a tab,
	which the user may select to change the currently-displayed pane.

	List of available tab options :
	text      : Specifies a string to be displayed in the tab.
	sticky    : Specifies how the child pane is positioned within the
	            pane area. Value is a string containing zero or more of
	            the characters n, s, e, or w. Each letter refers to a
	            side (north, south, east, or west) that the child window
	            will "stick" to, as per the grid geometry manager.
	compound  : Specifies how to display the image relative to the text,
	            in the case both -text and -image are present.
	underline : Specifies the integer index (0-based) of a character to
	            underline in the text string. The underlined character is
	            used for mnemonic activation if ttk::notebook::enableTraversal
	            is called.
	image     : Specifies an image to display in the tab, which must have
	            been created with the image create command.
	"""
	widgetName="notebook"
	tabkeys = ["tabposition", "tabmargins"]
# ==================================================================================================
	def configure(self, cnf = {}, **kw):
		tab_cnf = _cnfpopstartswith("tab", self.tabkeys, cnf, **kw)

		Widget.configure(self, cnf, **kw)
		self.tk.call(("ttk::style", "configure", self["style"] + ".Tab") + self._options(tab_cnf))

	def insert(self, pos, pane, **options):
		"""
		Inserts a pane at the specified position. pos is either the string end,
		an integer index, or the name of a managed subwindow. If subwindow is
		already managed by the notebook, moves it to the specified position.
		"""
		tabid = self.tk.call(self._w, "insert", pos, pane)
		self.tab(pane, **options)
		return tabid

	def add(self, child, **options):
		"""
		Adds a new tab to the notebook. When the tab is selected, the child
		window will be displayed. child must be a direct child of the
		notebook window.
		"""
		return self.tk.call((self._w, 'add', child) + self._options(_cnf(options)))

	def tab(self, child, option = None, **options):
		"""
		Query or modify the options of the specific tab. If no option is specified,
		returns a dictionary of the tab option values. If one option is specified,
		returns the value of that option. Otherwise, sets the options to the
		corresponding values.
		"""
		if option: return self.tk.call(self._w, "tab", child, "-" + option)
		elif len(options): self.tk.call((self._w,"tab", child) + self._options(_cnf(options)))
		else: return self.tk.call(self._w, "tab", child)

	def index(self, tabid):
		"""
		Returns the numeric index of the tab specified by tabid, or the
		total number of tabs if tabid is the string "end".
		"""
		return self.tk.call(self._w, "index", tabid)

	def tabs(self):
		"""
		Returns a list of all windows managed by the widget.
		"""
		return self.tk.call(self._w, "tabs")

	def hide(self, tabid):
		"""
		Hides the tab specified by tabid. The tab will not be displayed,
		but the associated window remains managed by the notebook and
		its configuration remembered. Hidden tabs may be restored with
		the add command.
		"""
		self.tk.call(self._w, "hide", tabid)

	def forget(self, tabid):
		"""
		Removes the tab specified by tabid, unmaps and unmanages the
		associated child window.
		"""
		self.tk.call(self._w, "forget", tabid)

	def select(self, tabid = None):
		"""
		Selects the specified tab. The associated child pane will be displayed,
		and the previously-selected pane (if different) is unmapped. If tabid
		is omitted, returns the widget name of the currently selected pane.
		"""
		return self.tk.call(self._w, "select", tabid)

	def enableTraversal(self): self.tk.call('ttk::notebook::enableTraversal', self._w)
# ==================================================================================================

# ==================================================================================================
class Paned(Widget):
	"""
	A paned widget displays a number of subwindows, stacked either
	vertically or horizontally. The user may adjust the relative
	sizes of the subwindows by dragging the sash between panes.
	"""
	widgetName="panedwindow"
# ==================================================================================================
	def insert(self, pos, pane, **options):
		"""
		Inserts a pane at the specified position. pos is either the string end,
		an integer index, or the name of a managed subwindow. If subwindow
		is already managed by the paned window, moves it to the specified
		position.
		"""
		self.tk.call((self._w, "insert", pos, pane) + self._options(_cnf(options)))

	def add(self, pane, **options):
		"""
		Adds a new pane to the window. subwindow must be a direct child
		of the paned window pathname.
		"""
		return self.tk.call((self._w, "add", pane) + self._options(_cnf(options)))

	def forget(self, pane):
		"""
		Removes the specified subpane from the widget. pane is either
		an integer index or the name of a managed subwindow.
		"""
		self.tk.call(self._w, "forget", pane)

	def pane(self, pane, option = None, **options):
		"""
		Query or modify the options of the specified pane, where pane is
		either an integer index or the name of a managed subwindow. If no
		-option is specified, returns a dictionary of the pane option values.
		If one -option is specified, returns the value of that option.
		Otherwise, sets the -options to the corresponding values.
		"""
		if option: return self.tk.call(self._w, "pane", pane, "-" + option)
		elif len(options): self.tk.call((self._w, "pane", pane) + self._options(_cnf(options)))
		else: return self.tk.call(self._w, "pane", pane)

	def panes(self):
		"""
		Returns the list of all windows managed by the widget.
		"""
		return self.tk.call(self._w, "panes")

	def sashpos(self, index = 0, newpos = None):
		"""If newpos is specified, sets the position of sash number index.
		May adjust the positions of adjacent sashes to ensure that positions
		are monotonically increasing. Sash positions are further constrained
		to be between 0 and the total size of the widget. Returns the new
		position of sash number index.
		"""
		if newpos != None: return self.tk.call(self._w, "sashpos", index, "-%d" % newpos)
		else: return self.tk.call(self._w, "sashpos", index)
# ==================================================================================================

# ==================================================================================================
class Tree(Widget):
	"""
	This widget displays a hierarchical collection of items. Each item has a textual
	label, an optional image, and an optional list of data values. The data values
	are displayed in successive columns after the tree label.

	The order in which data values are displayed may be controlled by setting the
	displaycolumns widget option. The tree widget can also display column headings.
	Columns may be accessed by number or by symbolic names listed in the columns widget
	option (see COLUMN IDENTIFIERS).

	Each item is identified by a unique name. The widget will generate item IDs if
	they are not supplied by the caller. There is a distinguished root item, named {}.
	The root item itself is not displayed; its children appear at the top level of the
	hierarchy.

	Each item also has a list of tags, which can be used to associate event bindings
	with individual items and control the appearance of the item.

	Treeview widgets support horizontal and vertical scrolling with the standard
	[xy]scrollcommand options and [xy]view widget commands.

	columns        : A list of column identifiers, specifying the number of columns and
	                 their names.
	displaycolumns : A list of column identifiers (either symbolic names or integer
	                 indices) specifying which data columns are displayed and the
	                 order in which they appear, or the string #all. If set to #all
	                 (the default), all columns are shown in the order given.
	height         : Specifies the number of rows which should be visible.
	                 -Note- the requested width is determined from the sum of the column widths.
	padding        : Specifies the internal padding for the widget. The padding is a
	                 list of up to four length specifications (see Ttk_GetPaddingFromObj()).
	selectmode     : Controls how the built-in class bindings manage the selection. One of
	                 extended, browse, or none.
                    If set to extended (the default), multiple items may be selected. If browse,
                    only a single item will be selected at a time. If none, the selection will
                    not be changed.
                    Note that application code and tag bindings can set the selection
                    however they wish, regardless of the value of -selectmode.

	show           : A list containing zero or more of the following values, specifying
	                 which elements of the tree to display.
                    - tree - Display tree labels in column #0. (default)
                    - headings - Display the heading row.

	NOTE: Column #0 always refers to the tree column, even if -show tree is not specified.
	"""
	widgetName="treeview"
	# pathname configure ?option? ?value option value ...? [OK] from master class
	# pathname cget option [OK] from master class
	# pathname state ?stateSpec?  [OK] from master class
	# pathname instate statespec ?script?  [OK] from master class
# ==================================================================================================
	__iter__ = lambda self: self.walk("")

	def __init__(self, master = None, cnf = {}, **kw):
		cnf = dict(cnf, **kw)
		cnf["style"] = "Treeview"
		Widget.__init__(self, master, cnf)

	def font(self, item):
		for tag in self.item(item, "tags"):
			font = self.tag_configure(tag, "font")
			if font != "": break
		return "TkDefaultFont" if font == "" else font

	def find_withtag(self, tag):
		return tuple(item for item in self if tag in self.item(item, "tags"))

	def walk(self, item):
		for child in self.tk.call(self._w, "children", item):
			yield child
			for elem in self.walk(child):
				yield elem

	# pathname bbox item ?column? [OK]
	def bbox(self, item, column = None):
		return self.tk.call(self._w, "bbox", item, column)

	# pathname children item ?newchildren? [OK] --> TODO get better name
	def xchildren(self, item, newchildren = None):
		return self.tk.call(self._w, "children", item, newchildren)

	# pathname column column ?-option ?value -option value...? [OK]
	# COLUMN OPTIONS : id, anchor, minwidth, stretch, width
	def column(self, column, option = None, **options):
		if option: return self.tk.call(self._w, "column", column, "-" + option)
		elif len(options): self.tk.call((self._w, "column", column) + self._options(_cnf(options)))
		else: return self.tk.call(self._w, "column", column)

	# pathname delete itemList [OK]
	def delete(self, *itemlist):
		return self.tk.call(self._w, "delete", " ".join(itemlist))

	# pathname detach itemList [OK]
	def detach(self, *itemlist):
		return self.tk.call(self._w, "detach", " ".join(itemlist))

	# pathname exists item [OK]
	def exists(self, item):
		return self.tk.call(self._w, "exists", item)

	# pathname focus ?item? [X] can get current focus but can not set it
	def focus(self, item = None):
		return self.tk.call(self._w, "focus", item)

	# pathname heading column ?-option ?value -option value...? [OK]
	# HEADING OPTIONS : text, image, anchor, command
	def heading(self, heading, option = None, **options):
		if option: return self.tk.call(self._w, "heading", heading, "-" + option)
		elif len(options): self.tk.call((self._w, "heading", heading) + self._options(_cnf(options)))
		else: return self.tk.call(self._w, "heading", heading)

	# pathname identify component x y
		# pathname identify row x y
		# pathname identify column x y

	# pathname index item [OK]
	def index(self, item = None):
		return self.tk.call(self._w, "index", item)

	# pathname insert parent index ?-id id? options... [OK]
	# ITEM OPTIONS : text, image, values, open, tags
	def insert(self, parent = "", index = "end", cnf = {}, **kw):
		return self.tk.call((self._w, "insert", parent, index, ) + self._options(_cnf(cnf, **kw)))

	# pathname item item ?-option ?value -option value...? [OK]
	# ITEM OPTIONS : text, image, values, open, tags
	def item(self, item, option = None, **options):
		if option: return self.tk.call(self._w, "item", item, "-" + option)
		elif len(options): self.tk.call((self._w, "item", item) + self._options(_cnf(options)))
		else: return _dict(self.tk.call(self._w, "item", item))

	# pathname move item parent index [OK]
	def move(self, item, parent, index):
		return self.tk.call(self._w, "move", item, parent, index)

	# pathname next item [OK]
	def next(self, item):
		return self.tk.call(self._w, "next", item)

	# pathname parent item [OK]
	def parent(self, item):
		return self.tk.call(self._w, "parent", item)

	# pathname prev item [OK]
	def prev(self, item):
		return self.tk.call(self._w, "prev", item)

	# pathname see item [OK]
	def see(self, item):
		return self.tk.call(self._w, "see", item)

	# pathname selection ?selop itemList? [OK]
		# pathname selection set itemList
		# pathname selection add itemList
		# pathname selection remove itemList
		# pathname selection toggle itemList
	def selection(self, operation = None, *itemlist):
		if operation and len(itemlist): self.tk.call(self._w, "selection", operation, " ".join(itemlist))
		else: return self.tk.call(self._w, "selection")

	# pathname set item ?column? ?value? [OK]
	def set(self, item, column = None, value = None):
		if column == None and value == None: return _dict(self.tk.call(self._w, "set", item))
		else: return self.tk.call(self._w, "set", item, column, value)

	# pathName tag args... [OK]
	# TAG OPTIONS : foreground, background, font, image
	def tag_configure(self, tagname, option = None, **options):
		if option: return self.tk.call(self._w, "tag", "configure", tagname, "-" + option)
		elif len(options): self.tk.call((self._w, "tag", "configure", tagname) + self._options(_cnf(options)))
		else: return self.tk.call(self._w, "tag", "configure", tagname)

	# pathName tag has tagName ?item?
# 	def tag_has(self, tagname, item = None):
# 		if item: self.tk.call(self._w, "tag", "has", tagname, item)
# 		else: self.tk.call(self._w, "tag", "has", tagname)

		# pathName tag bind tagName ?sequence? ?script?
		# pathName tag configure tagName ?option? ?value option value...?
		# pathName tag names
		# pathName tag add tag items
		# pathName tag remove tag ?items?

	# pathName xview args [OK]
	def xview(self, *args):
		return self.tk.call((self._w, "xview",) + args)

	# pathName yview args [OK]
	def yview(self, *args):
		return self.tk.call((self._w, "yview",) + args)

# =================================================================================================
class Dialog(Toplevel):
	"""
	"""
	result = None
	# =================================================================================================
	def __init__(self, master = None, yes = "Oui", no = "Non", cancel = "Annuler", cnf = {}, **kw):
		config = {}
		config.update(cnf)
		config.update(kw)

		Toplevel.__init__(self, master)
		if master != None:
			master.attributes("-disabled", True)
			if master.winfo_viewable():
				self.transient(master)

		self.configure(dict((k, config[k]) for k in config if k in list(self.keys())))
		self.withdraw()

		# place buttons
		self.buttonframe = Frame(self, padding = 0, relief = "flat")
		self.buttonframe.pack(side = "bottom", fill = "x")
		self.buttonframe.columnconfigure(1, weight = 1)
		if yes != False: # --> apply
			self.yesbutton = Button(self.buttonframe, default = "active", width = -1, padding = (10, 0), text = yes, command = lambda: self.close(1), compound = "left")
			self.yesbutton.grid(row = 1, column = 0)
		if no != False: # --> cancel
			self.nobutton = Button(self.buttonframe, width = -1, padding = (10, 0), text = no, command = lambda: self.close(0), compound = "left")
			self.nobutton.grid(row = 1, column = 2)
		if cancel != False: #--> close
			self.cancelbutton = Button(self.buttonframe, width = -1, padding = (10, 0), text = cancel, command = lambda: self.close(None), compound = "left")
			self.cancelbutton.grid(row = 1, column = 1, padx = self["border"])

		# fill content
		self.contentframe = Frame(self, padding = 0, relief = "flat")
		self.contentframe.pack(side = "top", fill = "both", expand = "yes")
		firstwidget = self.fill(self.contentframe, **config)
		if firstwidget != None: firstwidget.focus_set()

		Separator(self).pack(side = "top", fill = "x", pady = 5, padx = 0)

		self.center()
		self.resizable(False, False)
		self.deiconify()

		self.wait_visibility() # window needs to be visible for the grab
		self.grab_set()
		self.protocol('WM_DELETE_WINDOW', self.close)

		self.bind("<Key-Escape>", lambda *args:self.close())
		self.bind("<Key-Return>", lambda *args: self.yesbutton.invoke())

		self.result = None
		self.wait_window(self)
	# =================================================================================================
	def close(self, answer = None):
		if self.master is not None:
			self.master.focus_set()
		self.grab_release()
		if self.master != None:
			self.master.attributes("-disabled", False)
		if answer == 0: self.cancel()
		if answer == 1: self.apply()
		self.destroy()
	# =================================================================================================
	def fill(self, master, **cnf): pass
	# =================================================================================================
	def apply(self): pass
	# =================================================================================================
	def cancel(self): pass
	# =================================================================================================
	def center(self):
		self.overrideredirect(True)
		self.geometry("+0+0")

		topmaster = self.master.winfo_toplevel()
		topmaster.update()
		if topmaster.winfo_ismapped():
			W, H = topmaster.winfo_width(), topmaster.winfo_height()
			X, Y = topmaster.winfo_rootx(), topmaster.winfo_rooty()
		else:
			W, H = topmaster.winfo_screenwidth(), topmaster.winfo_screenheight()
			X, Y = 0, 0

		self.overrideredirect(False)
		self.update()
		w, h = self.winfo_width(), self.winfo_height()
		self.geometry("+%s+%s" % (X + (W-w)/2 - self.winfo_rootx(), Y + (H-h)/2 - self.winfo_rooty()))
