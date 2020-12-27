import tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np
import pandas as pd
import mplcursors
from pandastable import Table, TableModel


root = tkinter.Tk()
root.wm_title("Embedding in Tk")


t = np.arange(0, 3, .01)

fig, axes = plt.subplots(ncols=2)
ax = axes[0]
line = ax.plot(t, 2 * np.sin(2 * np.pi * t))

ax1 = axes[1]
line1 = ax1.plot(t, 210* np.sin(10 * np.pi * t))

canvas = FigureCanvasTkAgg(fig, master=root)


cursor = mplcursors.cursor(line + line1)

mplcursors.cursor(line)

canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)

def _quit():
    root.quit()
    root.destroy()  

df = pd.DataFrame({
    1:[1,2,3],
    2:[2,4,6]
})


button = tkinter.Button(master=root, text="Quit", command=_quit)
button.pack(side=tkinter.BOTTOM)


f = Frame(tkinter.main)
f.pack(fill=BOTH,expand=1)
tkinter = df = Table(f, dataframe=df,
                                    showtoolbar=True, showstatusbar=True)

tkinter.mainloop()




#launch the app
try:
    app.mainloop()
except UnicodeDecodeError:
    pass