import numpy as np
import pandas as pd
import requests
import datetime
import re
import time
from tkinter import *
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
import seaborn as sns
from pandastable import Table, TableModel
from fake_useragent import UserAgent
import random
import mplcursors
import warnings

df = pd.DataFrame({
    'Type':['a','a','b','b'],
    'Value':[2,4,6,9],
})

TABLE_WIDTH=0.2
TABLE_HEIGHT=0.2
PLOT_WIDTH=8
PLOT_HEIGHT=6


class UserInterface(Table):
    # Launch the df in a pandastable frame

    def handleCellEntry(self, row, col):
        super().handleCellEntry(row, col)
        print('changed:', row, col, "(TODO: update database)")
        return 0

    def change_df_combo(self, event):
        global ui_df, refresh_plot
        combo_selection = str(combo_box.get())
        
        ui_df = pos_df.copy()
        
        if combo_selection == "Type":
            pass
        else:
            ui_df = ui_df[pos_df.Type.apply(lambda x:str(x)) == combo_selection]
            
        refresh_plot(event)
            
        self.updateModel(TableModel(ui_df))
        self.redraw()
        mplcursors.cursor()
        
        
def create_plot():
    global PLOT_WIDTH, PLOT_HEIGHT
    
    fig, ax = plt.subplots(2,1,figsize=(PLOT_WIDTH, PLOT_HEIGHT))
    plt.subplots_adjust(hspace=0.4)

    ax[0].plot(list(range(len(ui_df.Value))), ui_df.Value)
    sns.histplot(x='Value', hue='Type', kde=False, stat='count', data=ui_df, ax=ax[1])

    ax[0].set_title('Trend')
    ax[1].set_title('Type Dist')

    return fig, ax

    
def refresh_plot(event):
    global fig, ax, canvas, ui_df, PLOT_WIDTH, PLOT_HEIGHT, cursor
    
    plt.clf()
    fig, ax = plt.subplots(2,1,figsize=(PLOT_WIDTH, PLOT_HEIGHT))
    plt.subplots_adjust(hspace=0.4)

    ax[0].plot(list(range(len(ui_df.Value))), ui_df.Value)
    sns.histplot(x='Value', hue='Type', kde=False, stat='count', data=ui_df, ax=ax[1])

    ax[0].set_title('Trend')
    ax[1].set_title('Type Dist')
    
    canvas.figure = fig
    canvas.draw()
    cursor = mplcursors.cursor(hover=True)

    
pos_df = df
ui_df = pos_df

#Launch Tkinter basics
root = Tk()
root.title("Type")

mainframe = ttk.Frame(root, padding="3 3 3 3")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

f = Frame(mainframe)
f.grid(column=0, columnspan=3,row=1, sticky=(E, W))
screen_width = f.winfo_screenwidth() * TABLE_WIDTH
screen_height = f.winfo_screenheight() * TABLE_HEIGHT

ui = UserInterface(f, dataframe=pos_df, height = screen_height, width = screen_width, showtoolbar=True, editable=False)


#Combobox to filter df
combo_choices = ['Type']+list(np.unique(df.Type))
choice = StringVar()
combo_box = ttk.Combobox(mainframe, textvariable=choice)
combo_box['values'] = combo_choices
combo_box.grid(column=0, row=0, sticky=(NW))
combo_box.set("Type")
combo_box.bind('<<ComboboxSelected>>', ui.change_df_combo)
combo_box.columnconfigure(0, weight=1)
combo_box.rowconfigure(0, weight=1)


fig, ax = create_plot()
canvas = FigureCanvasTkAgg(fig, master=root)

cursor = mplcursors.cursor()

canvas.draw()
canvas.get_tk_widget().grid(column=4, row=0, rowspan=3)



toolbarFrame = Frame(master=root)
toolbarFrame.grid(row=22,column=4)
toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
toolbar.update()

ui.show()
root.mainloop()

root.quit()