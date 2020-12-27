import tkinter as tk
from tkinter.filedialog import askopenfilename
import pandas as pd

root = tk.Tk()
root.withdraw() #Prevents the Tkinter window to come up
exlpath = askopenfilename()
root.destroy()
print(exlpath)
df = pd.read_excel(exlpath)