import beams
import loadfactors
from matplotlib.figure import Figure
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

def beam_2D_plot_plotly(x_y_array, force_type:str, direction:str, force_units: str, length_units:str) -> go.Figure:
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

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=coor, y=[0]*len(coor), mode='lines', line=dict(color='black', width=5), name='Beam'))

    fig.add_trace(go.Scatter(x=coor, y=val, mode='lines', fill='tozeroy', fillcolor='rgba(0,0,255,0.3)', line=dict(color='blue'), name=force_type))

    fig.update_layout(title=f"{force_type.title()} ({direction}) in beam [{force_units}]",
                      xaxis=dict(title=f"Beam length [{length_units}]"),
                      yaxis=dict(title=f"{force_type.title()} [{force_units}]"),
                      plot_bgcolor='white')

    fig.add_annotation(x=max_val_loc, y=max_val, text=f"{round(max_val)} [{force_units}]", showarrow=True, arrowhead=1, font=dict(color='black'))
    fig.add_annotation(x=min_val_loc, y=min_val, text=f"{round(min_val)} [{force_units}]", showarrow=True, arrowhead=1, font=dict(color='black'))

    return fig


def beam_2D_plot_matplotlib(x_y_array, force_type:str, direction:str, force_units: str, length_units:str) -> Figure:
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

def plot_beam_visualization(beam_data):
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

def plot_beam_visualization_plotly(beam_data):
    """
    Not properly implemented yet
    """
    fig = go.Figure()
    
    # Plot the beam line
    fig.add_trace(go.Scatter(x=[0, beam_data['L']], y=[0, 0], mode='lines', line=dict(color='black', width=2), name='Beam'))
    
    # Plot supports
    for pos, support_type in beam_data['Supports'].items():
        if support_type == 'P':
            fig.add_trace(go.Scatter(x=[pos], y=[0], mode='markers', marker=dict(symbol='triangle-up', color='blue', size=10), name='Point Support'))
        elif support_type == 'R':
            fig.add_trace(go.Scatter(x=[pos], y=[0], mode='markers', marker=dict(symbol='circle', color='green', size=10), name='Roller Support'))
        elif support_type == 'F':
            fig.add_trace(go.Scatter(x=[pos], y=[0], mode='markers', marker=dict(symbol='square', color='purple', size=10), name='Fixed Support'))
    
    # Plot loads
    max_load_magnitude = 0
    for load in beam_data['Loads']:
        if load['Type'] == 'Point':
            fig.add_trace(go.Scatter(x=[load['Location'], load['Location']], y=[0, -load['Magnitude']], mode='lines', line=dict(color='red', width=5), name='Point Load'))
            fig.add_annotation(x=load['Location'], y=-load['Magnitude'], text=f"{abs(load['Magnitude'])} kN", showarrow=False)
            max_load_magnitude = max(max_load_magnitude, abs(load['Magnitude']))
        elif load['Type'] == 'Dist':
            start_loc = load['Start Location']
            end_loc = load['End Location']
            start_mag = load['Start Magnitude']
            end_mag = load['End Magnitude']
            fig.add_trace(go.Scatter(x=[start_loc, end_loc], y=[-start_mag, -end_mag], mode='lines', line=dict(color='orange', width=5), name='Distributed Load'))
            fig.add_annotation(x=start_loc, y=-start_mag, text=f"{abs(start_mag)} kN", showarrow=False)
            fig.add_annotation(x=end_loc, y=-end_mag, text=f"{abs(end_mag)} kN", showarrow=False)
            max_load_magnitude = max(max_load_magnitude, abs(start_mag), abs(end_mag))
    
    # Set labels and title
    fig.update_layout(title=beam_data['Name'],
                      xaxis_title='Beam length [mm]',
                      yaxis_title='Force [kN]')
    
    # Set axis limits and grid
    fig.update_xaxes(range=[-30, beam_data['L']+30], showgrid=True)
    fig.update_yaxes(range=[-1.4 * max_load_magnitude, 1.4 * max_load_magnitude], showgrid=True)
    
    return fig