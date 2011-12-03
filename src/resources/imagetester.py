import Tkinter
import ttk
import logo_packed

t = Tkinter.Tk()
t.title("boo")
p = Tkinter.PhotoImage(master=t,data=logo_packed.packed,format="gif89")
def boo():
  print "ha"


l = ttk.Button(t,image=p,text="Bestand toevoegen", compound=Tkinter.LEFT, command=boo)
l.pack(pady=5)

t.mainloop()
