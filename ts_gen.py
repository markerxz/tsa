import tkinter as tk
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

class InteractiveDrawingApp:
    def __init__(self, root, config_file='config.json'):
        with open(config_file, 'r') as f:
            config = json.load(f)
        self.interval = config.get('interval')
        self.xlim = config.get('xlim')
        self.ylim = config.get('ylim')
        self.root = root
        self.root.title("Interactive Drawing")

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(*self.xlim)
        self.ax.set_ylim(*self.ylim)

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_move)

        self.xs = []
        self.ys = []
        self.times = []
        self.is_drawing = False
        self.last_recorded_time = 0


    def record_point(self, x, y):
        current_time = time.time()
        if current_time - self.last_recorded_time >= self.interval:
            self.xs.append(x)
            self.ys.append(y)
            self.times.append(current_time)
            self.last_recorded_time = current_time

    def on_press(self, event):
        self.is_drawing = True
        self.record_point(event.xdata, event.ydata)

    def on_move(self, event):
        if self.is_drawing and event.inaxes:
            self.record_point(event.xdata, event.ydata)
            self.ax.plot(self.xs[-2:], self.ys[-2:], color='blue')
            self.canvas.draw()

    def on_release(self, event):
        self.is_drawing = False
        self.ax.plot(self.xs, self.ys, color='blue')
        self.canvas.draw()
    
    def save_data(self, filename='drawing_data.json'):
        data = {'x': self.xs, 'y':self.ys, 'T': self.times}
        with open(filename, 'w') as f:
            json.dump(data, f)

    def on_close(self):
        self.save_data()  # Save data when window is closed
        self.root.quit()  # Use quit() to stop the mainloop
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveDrawingApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
