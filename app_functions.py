import beams
import plots
import loadfactors


def get_str_beam_data(attributes, supports, loads):
    support_floats = {float(key): value for key, value in supports.items()}
    structured_beam_data = beams.get_structured_beam_data_from_str_lib(attributes, support_floats, loads)
    return structured_beam_data

def get_model(attributes, supports, loads):
    structured_beam_data = get_str_beam_data(attributes, supports, loads)
    model = beams.build_beam(structured_beam_data, 1)
    model.analyze(check_statics=False)
    return model

def get_shear_plots(attributes, supports, loads, target_load_dir = "Fy", target_combo = "unfactored"):
    model= get_model(attributes, supports, loads)
    shear_arrays = beams.extract_arrays_all_combos(model, "shear", target_load_dir)   
    env_shear_x_y = loadfactors.load_combo_array(shear_arrays, target_combo)
    plot = plots.beam_2D_plot(env_shear_x_y, "shear", target_load_dir, "kN", "mm")

    return plot

def get_moment_plots(attributes, supports, loads, target_load_dir = "Mz", target_combo = "unfactored"):
    model= get_model(attributes, supports, loads)
    moment_arrays = beams.extract_arrays_all_combos(model, "moment", target_load_dir)   
    env_moment_x_y = loadfactors.load_combo_array(moment_arrays, target_combo)
    plot = plots.beam_2D_plot(env_moment_x_y, "moment", target_load_dir, "kN", "mm")

    return plot



def plot_beam(attributes, supports, loads):
    structured_beam_data = get_str_beam_data(attributes, supports, loads)
    plot = plots.plot_beam(structured_beam_data)
    return plot