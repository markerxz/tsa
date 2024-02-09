import numpy as np
import subprocess

axes = ['x','y']
def create_dat (interval,xlim, ylim):
    import json
    import numpy as np
    import matplotlib
    matplotlib.use('TkAgg') 
    filename = 'drawing_data.json'
    config = {"interval": interval, "xlim":xlim, "ylim":ylim}  # Set your desired sampling rate here
    with open('config.json', 'w') as f:
        json.dump(config,f)
    dat = subprocess.run(['python', 'ts_gen.py'])
    with open(filename, 'r') as f:
        dat = json.load(f)
        for key in dat:
            dat[key] = np.array(dat[key])
    return dat
    
def plot_data (data, interval,xlim, ylim):
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    import matplotlib
    matplotlib.use('TkAgg') 


    # Create the figure and axis for the animation
    fig, ax = plt.subplots(figsize=(8,8))
    lines = [ax.plot([], [], marker='o')[0] for _ in data]

    # Set the axes limits
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)

    # Initialize function for the animation
    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    # Animation update function
    def animate(i):
        for j, dataset in enumerate(data):
            # Update each line up to the current frame
            x = dataset['x'][:i]
            y = dataset['y'][:i]
            lines[j].set_data(x, y)
        return lines

    # Determine the number of frames based on the longest dataset
    frames = max(len(dataset['T']) for dataset in data)
    # Create the animation
    ani = FuncAnimation(fig, animate, frames=frames, init_func=init, blit=True, interval=interval*1000)
    # Display the animation in a popup window
    plt.show()

def draw_time_series (n,interval,xlim, ylim):
    return [create_dat(interval,xlim, ylim) for i in range(n)]

def create_table (L,seg):
    table = [0] * seg
    L = sorted(L)
    n = len(L)
    for i in range(seg):
        if i == 0:
            table[i] = L[0]
        else:
            idx = ((i/seg) * n) - 1
            if idx % 1 == 0:
                idx = int(idx)-1
                table[i] = L[idx]
            else:
                idx_temp = int(idx//1)-1
                diff = L[idx_temp+1] - L[idx_temp]
                table[i] = L[idx_temp] + diff*(idx%1)
    return table

def table_look_up (val,table):
    for i in range(1,len(table)):
        if val <= table[i]:
            return i
    return len(table)-1

def sorted_segment (data, seg = 4, share_axis = True, share_trial = True):
    seg = seg+1
    import copy
    cdata = copy.deepcopy(data)
    if share_axis and share_trial:
        L = []
        for trial in cdata:
            for axis in axes:
                ts = trial[axis]
                L.extend(ts.tolist())
        table = create_table(L,seg)
        for trial in cdata:
            for axis in axes:
                for i in range(len(trial[axis])):
                    trial[axis][i] = table_look_up(trial[axis][i],table)
        return cdata
    
    if share_axis and not share_trial:
        for trial in cdata:
            L = []
            for axis in axes:
                ts = trial[axis]
                L.extend(ts.tolist())
            table = create_table(L,seg)
            for axis in axes:
                for i in range(len(trial[axis])):
                    trial[axis][i] = table_look_up(trial[axis][i],table)
        return cdata
    
    if not share_axis and share_trial:
        for axis in axes:
            L = []
            for trial in cdata:
                ts = trial[axis]
                L.extend(ts.tolist())
            table = create_table(L,seg)
            for trial in cdata:
                for i in range(len(trial[axis])):
                    trial[axis][i] = table_look_up(trial[axis][i],table)
        return cdata

    if not share_axis and not share_trial:
        for trial in cdata:
            for axis in axes:
                L = []
                ts = trial[axis]
                L.extend(ts.tolist())
                table = create_table(L,seg)
                for i in range(len(trial[axis])):
                    trial[axis][i] = table_look_up(trial[axis][i],table)
        return cdata