# -*- encoding:latin-1 -*-
from pyTtk import Tree, Frame, Menu, Entry
import math

_values = lambda pdb, field: tuple(getattr(pdb, "_" + field)) if hasattr(pdb, "_" + field) else ()

class TreeEntry(Entry):

	def set(self, value):
		Entry.delete(self, 0, "end")
		Entry.insert(self, 0, "%r" % (value, ))

	def get(self):
		tmp = Entry.get(self)
		try: exec('value = %s' % tmp)
		except (NameError, SyntaxError): exec('value = u%s' % repr(tmp))
		return value

	def clear(self): Entry.delete(self, 0, "end")


class PdlTree(Tree):
	clear = lambda self: Tree.delete(self, *iter(self))
	# =================================================================================================
	def _columns(self):
		return self["displaycolumns"]
	# =================================================================================================
	def _2tree(self, record):
		return tuple(record[field] if field in record else "" for field in self["columns"])
	# =================================================================================================
	def _2pdb(self, item):
		tags = self.item(item, "tags")
		return self.pdb[int(tags[0])] if len(tags) and tags[0] != "tree" else {}
	# =================================================================================================
	def __init__(self, master, pdb):
		self.pdb = pdb
		headings = tuple(pdb.fields)

		Tree.__init__(self, master, columns = headings, show = "headings", displaycolumns = headings)
		for i in range(len(headings)):
			self.heading("#%d" % (i+1), text = headings[i], command = lambda arg = headings[i]: self.fill(arg))

		self.menu = Menu(self, tearoff = False)
		self.menu.add("command", compound = "left", ulabel = "_Add record", command = self.add, accelerator = "Insert")
		self.menu.add("command", compound = "left", ulabel = "E_dit record", command = self.edit, accelerator = "Alt-Insert")
		self.menu.add("command", compound = "left", ulabel = "_Delete record", command = self.delete, accelerator = "Delete")

		self.bind("<Button-3>",   self.pop_menu)
		self.bind("<Key-App>",    self.pop_menu)
		self.bind("<Key-Insert>", self.add)
		self.bind("<Key-Delete>", self.delete)
		self.bind("<Alt-Insert>", self.edit)

		self.editor = Frame(self, padding = 0, relief = "flat")
		self.editor.rowconfigure(0, weight = 1)
		i = 0
		for name in self._columns():
			w = TreeEntry(self.editor, name = name, padding = (3, 0), width = -1)
			w.grid(row = 0, column = i, sticky = "nesw")
			i += 1

		for widget in self.editor.children.values():
			widget.bind("<KeyPress-Return>", lambda event: self._hide_editor(True), add = "+")
			widget.bind("<KeyPress-Escape>", lambda event: self._hide_editor(), add = "+")

		self.fill(headings[0])
		self.autosize()
	# =================================================================================================
	def xview(self, *args):
		Tree.xview(self, *args)
		if self.editor.place_info() != {}:
			if args[0] == "scroll":
				self.update()
				self._adjust_editor()
			else:
				w = getattr(self, "BBOX")[2]
				x = max(0, float(args[-1])*w)
				dif = abs(w - self.winfo_width())
				self.editor.place_configure(x = -(x if x <= dif else dif))
	# =================================================================================================
	def yview(self, *args):
		if self.editor.place_info() == {}:
			Tree.yview(self, *args)
	# =================================================================================================
	def _adjust_editor(self, *args):
		self.editor.place_configure(x = self.bbox(getattr(self, "ITEM"))[0])
	# =================================================================================================
	def _show_editor(self, item):
		i, w = 0, 0
		for name in self._columns():
			tmp = self.column(name, "width")
			self.editor.columnconfigure(i, minsize = tmp)
			i += 1
			w += tmp

		x, y, _w, h = self.bbox(item)
		self.editor.place(x = x, y = y, w = w, h = h)

		self.editor.columnconfigure(i, weight = 1)
		first = self.editor.grid_slaves(column = 0)[0]
		first.focus()

		setattr(self, "ITEM", item)
		setattr(self, "BBOX", (x, y, w, h))
		setattr(self, "CNFEDIT", self.bind("<Configure>", self._adjust_editor, add = "+"))
	# =================================================================================================
	def _hide_editor(self, save = False):
		self.unbind("<<TreeviewSelect>>")
		self.focus_displayof().update()
		item = getattr(self, "ITEM")

		if save:
			result = dict((name, widget.get()) for (name, widget) in self.editor.children.items())
			record = self._2pdb(item)
			if record:
				self.pdb.update(record, **result)
				self.item(item, values = self._2tree(result))
			else:
				id_ = self.pdb.insert(**result)
				self.pdb.update(self.pdb[id_])
				self.item(item, tags = id_, values = self._2tree(result))
			self.pdb.commit()

		if self.item(item, "tags") == "": Tree.delete(self, item)

		for widget in tuple(w for w in self.editor.children.values()): widget.clear()
		self.editor.place_forget()
		self.focus()
		delattr(self, "ITEM")
		delattr(self, "BBOX")
		self.unbind("<Configure>", getattr(self, "CNFEDIT"))
		delattr(self, "CNFEDIT")
	# =================================================================================================
	def fill(self, sortkey):
		if self.editor.place_info() != {}: self._hide_editor()
		self.clear()
		for record in sorted([rec for rec in self.pdb], key=lambda r: r[sortkey], reverse = True):
			self.insert("", 0, tags = record["__id__"], values = self._2tree(record))
	# =================================================================================================
	def pop_menu(self, event):
		len_ = len(self.selection())
		self.menu.entryconfigure(1, state = "normal" if 0 < len_ <= 1 else "disabled")
		self.menu.entryconfigure(2, state = "normal" if len_ > 0 else "disabled")
		if len_ > 1: self.menu.entryconfigure(2, ulabel = "_Delete records")
		else: self.menu.entryconfigure(2, ulabel = "_Delete record")
		self.menu.tk_popup(event.x_root, event.y_root)
	# =================================================================================================
	def autosize(self):
		maxwidth = tuple(self.tk.call("font", "measure", "TkDefaultFont", column) for column in self._columns())
		for item in self:
			values = self.set(item)
			width = tuple(self.tk.call("font", "measure", self.font(item), values[column]) for column in self._columns())
			maxwidth = tuple(max(maxwidth[i], width[i]) for i in range(len(maxwidth)))
		for i in range(len(maxwidth)):
			self.column("#%d" % (i+1), stretch = False, width = maxwidth[i] + 10)
	# =================================================================================================
	def add(self, event = None):
		item = self.insert("", 0)
		self.see(item)
		self._show_editor(item)
		self.bind("<<TreeviewSelect>>", lambda *args: self._hide_editor(False))
	# =================================================================================================
	def edit(self, event = None):
		item = self.selection()[0]
		record = self._2pdb(item)
		if record != {}:
			for name, widget in self.editor.children.items():
				widget.set(record[name])
		self._show_editor(item)
		self.bind("<<TreeviewSelect>>", lambda *args: self._hide_editor(False))
	# =================================================================================================
	def delete(self, event = None):
		selection = self.selection()
		self.pdb.delete(self._2pdb(item) for item in selection)
		self.pdb.commit()
		Tree.delete(self, *selection)
