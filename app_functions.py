import beams
import plots
import loadfactors
from PyNite import FEModel3D
import plotly.graph_objects as go


def get_str_beam_data(attributes: dict[str, str], supports: dict[str, str], loads: list[dict[str, str]]) -> dict:
    """
    Convert string-type beam data to structured format for building beam model.

    Args:
    - attributes (dict): Dictionary containing beam attributes.
    - supports (dict): Dictionary containing support positions and types.
    - loads (list): List of dictionaries containing load data.

    Returns:
    - dict: Structured beam data ready for building beam model.
    """
    support_floats = {float(key): value for key, value in supports.items()}
    structured_beam_data = beams.get_structured_beam_data_from_str_lib(attributes, support_floats, loads)
    return structured_beam_data

def get_model(attributes: dict[str, str], supports: dict[str, str], loads: list[dict[str, str]], **kwargs) -> FEModel3D:
    """
    Build and analyze beam model.

    Args:
    - attributes (dict): Dictionary containing beam attributes.
    - supports (dict): Dictionary containing support positions and types.
    - loads (list): List of dictionaries containing load data.
    - **kwargs: Additional keyword arguments to pass to the beam model builder.

    Returns:
    - BeamModel: Analyzed beam model.
    """
    structured_beam_data = get_str_beam_data(attributes, supports, loads)
    model = beams.build_beam(structured_beam_data, 1, **kwargs)
    model.analyze(check_statics=False)
    return model

def get_shear_plots(attributes: dict[str, str], supports: dict[str, str], loads: list[dict[str, str]], target_load_dir: str = "Fy", target_combo: str = "unfactored", **kwargs) -> tuple[go.Figure, str]:
    """
    Get shear force plots for beam.

    Args:
    - attributes (dict): Dictionary containing beam attributes.
    - supports (dict): Dictionary containing support positions and types.
    - loads (list): List of dictionaries containing load data.
    - target_load_dir (str): Target load direction for shear force.
    - target_combo (str): Target load combination.
    - **kwargs: Additional keyword arguments.

    Returns:
    - tuple: Plotly figure and target load combination.
    """
    model= get_model(attributes, supports, loads, **kwargs)
    shear_arrays = beams.extract_arrays_all_combos(model, "shear", target_load_dir)   
    
    if target_combo == "max":
        target_combo = loadfactors.get_max_combo(shear_arrays, **kwargs)[0]
    env_shear_x_y = loadfactors.load_combo_array(shear_arrays, target_combo)
    plot = plots.beam_2D_plot_plotly(env_shear_x_y, "shear", target_load_dir, "kN", "mm")

    return (plot, target_combo)

def get_moment_plots(attributes: dict[str, str], supports: dict[str, str], loads: list[dict[str, str]], target_load_dir: str = "Mz", target_combo: str = "unfactored", **kwargs) -> tuple[go.Figure, str]:
    """
    Get bending moment plots for beam.

    Args:
    - attributes (dict): Dictionary containing beam attributes.
    - supports (dict): Dictionary containing support positions and types.
    - loads (list): List of dictionaries containing load data.
    - target_load_dir (str): Target load direction for bending moment.
    - target_combo (str): Target load combination.
    - **kwargs: Additional keyword arguments.

    Returns:
    - tuple: Plotly figure and target load combination.
    """
    model= get_model(attributes, supports, loads)
    moment_arrays = beams.extract_arrays_all_combos(model, "moment", target_load_dir)   
    if target_combo == "max":
        env_moment_x_y = loadfactors.get_max_combo(moment_arrays, **kwargs)[1]
    else:
        env_moment_x_y = loadfactors.load_combo_array(moment_arrays, target_combo)
    plot = plots.beam_2D_plot_plotly(env_moment_x_y, "moment", target_load_dir, "kN", "mm")

    return (plot, target_combo)



def get_beam_visual(attributes: dict[str, str], supports: dict[str, str], loads: list[dict[str, str]]) -> go.Figure:
    """
    Get 2D visualization of the beam.

    Args:
    - attributes (dict): Dictionary containing beam attributes.
    - supports (dict): Dictionary containing support positions and types.
    - loads (list): List of dictionaries containing load data.

    Returns:
    - go.Figure: Plotly figure of the beam visualization.
    """
    structured_beam_data = get_str_beam_data(attributes, supports, loads)
    plot = plots.plot_beam_visualization(structured_beam_data)
    return plot

