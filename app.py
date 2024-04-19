import streamlit as st
import loadfactors
import beams
import app_functions
import plots



#Attribute inputs

st.sidebar.header("Attribute Inputs (SI units):")
beam_name = st.sidebar.text_input("Beam Name:", value="Beam Name")
L = st.sidebar.number_input("L (mm):", value=1000.0)
E = st.sidebar.number_input("E (kN/mm2):", value=1.0)
Iz = st.sidebar.number_input("Iz (mm4):", value=1.0)
Iy = st.sidebar.number_input("Iy (mm4):", value=1.0)
A = st.sidebar.number_input("A (mm2):", value=1.0)
J = st.sidebar.number_input("J (mm4):", value=1.0)
nu = st.sidebar.number_input("nu:", value=1.0)
rho = st.sidebar.number_input("rho:", value=1.0)
list_attributes = [beam_name, L, E, Iz, Iy, A, J, nu, rho]


st.sidebar.header("Target S6 Combo")
load_combos = list(loadfactors.CSA_S6_2019_combos())
load_combos_with_max = ["max"] + load_combos
target_combo = st.sidebar.selectbox(f"Target Combo:", options=load_combos_with_max)
load_factor_details = st.sidebar.selectbox("Load factor details: ", options=["Default", "Advanced"])

if load_factor_details == "Advanced":
    material_dict = {"Factory-produced components, excluding wood": "M1", "Cast-in-place concrete, wood, and all non-structural components" : "M2", "Wearing surfaces, based on nominal or specified thickness" : "M3", "Earth fill, negative skin friction on piles" : "M4", "Water" : "M5", "Dead load in combination with earthquakes (ULS5)":"M6"}
    material_type = material_dict[st.sidebar.selectbox(f"Material Type:", options=list(material_dict.keys()))]
    earth_pressure_dict = {"Passive earth pressure, considered as a load" : "E1", "At-rest earth pressure":"E2", "Active earth pressure":"E3", "Backfill pressure":"E4", "Hydrostatic pressure":"E5"}
    earth_pressure_type = earth_pressure_dict[st.sidebar.selectbox(f"Earth Pressure Type:", options=list(earth_pressure_dict.keys()))]
    LL_type_dict = {"Normal load":"Normal", "Special loads mixed with normal traffic for short spans":"Special_mixed_short", "Special loads mixed with normal traffic for other spans":"Special_mixed_other", "Special loads for short spans":"Special_alone_short", "Special loads for other spans":"Special_alone_other"}
    LL_span_type = LL_type_dict[st.sidebar.selectbox(f"Live Load Span Type:", options=list(LL_type_dict.keys()))]
    max_min_dict = {"Max":0, "Min": 1}
    alpha_D = max_min_dict[st.sidebar.selectbox(f"Dead load max/min:", options=list(max_min_dict.keys()))]
    alpha_E = max_min_dict[st.sidebar.selectbox(f"Earth load max/min:", options=list(max_min_dict.keys()))]
    alpha_factors = loadfactors.get_alpha_factors(material_type=material_type, alpha_D_max_min=alpha_D, earth_pressure_type=earth_pressure_type, alpha_E_max_min=alpha_E, L_span_type=LL_span_type)
else:
    alpha_factors = loadfactors.get_alpha_factors()





# Support inputs
st.sidebar.header("Support Inputs (SI units):")
support_acc_dict = {}
support_types = ["P", "R", "F", "Free"]
num_supports = int(st.sidebar.number_input("Number of supports", value=2, step=1))
for support in range(num_supports):
    st.sidebar.subheader(f"Support {support+1}")
    if support == 0:
        sup_loc = float(st.sidebar.number_input(f"Support {support+1} location:", value = float(0.0), min_value=0.0, max_value=L+0.00001))  # First support placed at 0
    elif support == 1:
        sup_loc = float(st.sidebar.number_input(f"Support {support+1} location:", value = float(L), min_value=0.0, max_value=L+0.00001))  # Second support placed at L
    else:
        sup_loc = float(st.sidebar.number_input(f"Support {support+1} location:", value = float(L/2), min_value=0.0, max_value=L))
        

    sup_rest = st.sidebar.selectbox(f"Support {support+1} restraint:", options=support_types)
    st.sidebar.write("")
    support_acc_dict.update({float(sup_loc): sup_rest})

#Load inputs
st.sidebar.header("Loading Inputs (SI units):")
load_list_acc = []
load_types = ["Point", "Dist"]
load_directions = ["Fy", "Fx"]
load_cases = list(loadfactors.CSA_S6_2019_combos()["ULS1"].keys())
num_loads = int(st.sidebar.number_input("Number of loads", value=1, step=1))
for load in range(num_loads):
    inner_load_dict_acc = {}
    st.sidebar.subheader(f"Load {load+1}")
    l_type = st.sidebar.selectbox(f"Load {load+1} type:", options=load_types)
    inner_load_dict_acc.update({"Type": l_type})
    l_dir = st.sidebar.selectbox(f"Load {load+1} direction:", options=load_directions)
    inner_load_dict_acc.update({"Direction": l_dir})
    if l_type == "Dist":
        start_value = st.sidebar.number_input(f"Load {load+1} start value:", value=-100.0)
        end_value = st.sidebar.number_input(f"Load {load+1} end value:", value=-100)
        start_loc = st.sidebar.number_input(f"Load {load+1} start location:", min_value=0.0, max_value=L, value=0.0)
        end_loc = st.sidebar.number_input(f"Load {load+1} end location:", min_value=0.0, max_value=L, value=L)
        inner_load_dict_acc.update({"Start Magnitude": start_value,'End Magnitude': end_value, 'Start Location': start_loc, 'End Location': end_loc})
    else:
        point_val = st.sidebar.number_input(f"Load {load+1} value:", value=-100)
        point_loc = st.sidebar.number_input(f"Load {load+1} location:", min_value=0.0, max_value=L, value=L/2)
        inner_load_dict_acc.update({'Magnitude': point_val, 'Location': point_loc})
    l_case = st.sidebar.selectbox(f"Load {load+1} case:", options=load_cases)
    inner_load_dict_acc.update({"Case": l_case})
    st.sidebar.write("")
    load_list_acc.append(inner_load_dict_acc)



shear_plot = app_functions.get_shear_plots(list_attributes, support_acc_dict, load_list_acc, target_combo=target_combo, **alpha_factors)
moment_plot = app_functions.get_moment_plots(list_attributes, support_acc_dict, load_list_acc, target_combo=target_combo, **alpha_factors)
beam_visual = app_functions.get_beam_visual(list_attributes, support_acc_dict, load_list_acc)



#Display

st.title("Shear and bending moment diagrams for 2D loading")
st.write("")
if target_combo == "max":
    st.write(f"The Max loading occurs at combo {shear_plot[1]}")
    st.write("")

st.header("Beam Visualization")
st.write(beam_visual)
st.header("Shear Diagram")
st.write(shear_plot[0])
st.header("Bending Moment Diagram")
st.write(moment_plot[0])


