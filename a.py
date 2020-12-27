import tkinter as tk
import sys
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SimplePlot(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        print(f"Matplotlib version: {matplotlib.__version__}")
        print(f"tkinter version: {tk.TkVersion}")

        self.make_plot()

    def make_plot(self):
        container = tk.Toplevel(self)

        fig = Figure()
        ax = fig.add_subplot(111)

        # Make dummy annotation
        annot = ax.annotate("", xy=(3,3), xytext=(0,0),textcoords="offset points")
        annot.set_visible(False)

        def update_annot(ind):
            pos = sc.get_offsets()[ind]
            annot.xy = pos
            text = "x: {}, y: {}".format(*pos)
            annot.set_text(text)

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, index = sc.contains(event)
                if cont:
                    ind = index["ind"][0]  # Get useful value from dictionary
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        canvas = FigureCanvasTkAgg(fig, container)
        canvas.show()
        canvas.get_tk_widget().grid(row=1, column=0)
        fig.canvas.mpl_connect("motion_notify_event", hover)

        xs = [1, 2, 3, 4, 5]
        ys = [1, 4, 7, 4, 8]

        sc = ax.scatter(xs, ys, marker="o")


if __name__ == "__main__":
    app = SimplePlot()
    app.resizable(False, False)
    app.mainloop()