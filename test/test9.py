import sys

if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk

r = tk.Tk()
r.title('Counting Seconds')
button = tk.Button(r, text='Stop', width=25,height=20, command=r.destroy)
button.pack()
r.mainloop()