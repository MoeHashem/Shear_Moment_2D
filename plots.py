import beams
import loadfactors
from matplotlib.figure import Figure
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

# model = beams.load_beam_model("test_data/example_beam_wb6.txt")
# model.analyze(check_statics=False)
# moment_arrays = beams.extract_arrays_all_combos(model, "moment", "Mz", n_points=3)
# # shear_arrays = beams.extract_arrays_all_combos(model, "shear", "Fy")
# env_moment_x_y = loadfactors.load_combo_array(moment_arrays, "ULS2")
# print(env_moment_x_y)
# # print(f"{env_moment_x_y=}")
# # env_shear_x_y = loadfactors.envelope_max(shear_arrays)




def beam_2D_plot(x_y_array, force_type:str, direction:str, force_units: str, length_units:str) -> Figure:
    coor = x_y_array[0]
    val = x_y_array[1]
    max_val = max(val)
    max_val_idx = val.index(max_val)
    max_val_loc = coor[max_val_idx]
    min_val = min(val)
    min_val_idx = val.index(min_val)
    min_val_loc = coor[min_val_idx]

    if force_type == "moment":
        force_units = force_units+length_units
    fig = Figure()
    ax = fig.gca()
   
    ax.set_title(f"{force_type.title()} ({direction}) in beam [{force_units}]")
    ax.set_xlabel(f"Beam length [{length_units}]")
    ax.set_ylabel(f"{force_type.title()} [{force_units}]")
    ax.plot(coor, [0]*len(coor), color="black", lw=3)
    ax.fill_between(coor, val, ec = "black")

    ax.annotate(f"{round(max_val)} [{force_units}]", (max_val_loc, max_val))
    ax.annotate(f"{round(min_val)} [{force_units}]", (min_val_loc, min_val))
    fig.savefig("test")
    return fig


# beam_2D_plot(env_moment_x_y, "M_test.png", "moment", "Mz", "Nmm", "mm")
# beam_2D_plot(env_shear_x_y, "V_test.png", "shear", "Fy", "kN", "mm")

def plot_beam(beam_data):
    fig, ax = plt.subplots()
    
    # Plot the beam line
    ax.plot([0, beam_data['L']], [0, 0], color='black', linestyle='-', linewidth=2)
    
    # Plot supports
    for pos, support_type in beam_data['Supports'].items():
        if support_type == 'P':
            ax.plot(pos, 0, marker='^', color='blue', markersize=10)
        elif support_type == 'R':
            ax.plot(pos, 0, marker='o', color='green', markersize=10)
        elif support_type == 'F':  # Plot "F" support as a square
            ax.plot(pos, 0, marker='s', color='purple', markersize=10)
    
    # Plot loads
    max_load_magnitude = 0
    for load in beam_data['Loads']:
        if load['Type'] == 'Point':
            ax.arrow(load['Location'], -load['Magnitude'], 0, load['Magnitude'], head_width=0.015*np.abs(beam_data['L']), head_length=0.015*np.abs(beam_data['L']), fc='red', ec='red', head_starts_at_zero = False, length_includes_head = True)
            ax.text(load['Location'], -load['Magnitude'], f"{abs(load['Magnitude'])}", va='bottom', ha='center')
            max_load_magnitude = max(max_load_magnitude, np.abs(load['Magnitude']))
        elif load['Type'] == 'Dist':
            start_loc = load['Start Location']
            end_loc = load['End Location']
            start_mag = load['Start Magnitude']
            end_mag = load['End Magnitude']
            
            # Plot start and end values
            ax.text(start_loc, -start_mag, f"{abs(start_mag)}", va='bottom', ha='center')
            ax.text(end_loc, -end_mag, f"{abs(end_mag)}", va='bottom', ha='center')
            
            # Plot load segment
            x = [start_loc, end_loc, end_loc, start_loc]
            y = [0, 0, -end_mag, -start_mag]
            ax.fill(x, y, color='orange', alpha=0.5)
            
            max_load_magnitude = max(max_load_magnitude, np.abs(start_mag), np.abs(end_mag))

    # Set labels and title
    ax.set_title(beam_data['Name'])
    ax.set_ylabel('Force [kN]')
    ax.set_xlabel('Beam length [mm]')
    
    # Set axis limits and grid
    ax.set_xlim(-30, beam_data['L']+30)
    ax.set_ylim(-1.4 * max_load_magnitude, 1.4 * max_load_magnitude)  # Adjust y-axis limits to raise the beam visualization
    ax.grid(True)
    
    return fig