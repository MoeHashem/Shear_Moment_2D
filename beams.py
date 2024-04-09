import math
from PyNite import FEModel3D
from PyNite.Visualization import render_model
import csv
from eng_module.utils import str_to_int, str_to_float, read_csv_file
import loadfactors


def beam_reactions_ss_cant(w: float, a: float, b: float) -> tuple[float, float]:
    """
    Determines the reactions "R1" and "R2" for a simply supported beam with a continuous cantilever on one end, as shown above. It will take three parameters (all float):

    w - Representing the magnitude of a uniform distributed load on the beam
    b - Representing the length of the backspan
    a - Representing the length of the cantilever
    
    Return two values (reactions) in this order:
    R1 (Canteliver support)
    R2 (Backspan support)
    """
    len = a+b
    centroid_udl = len/2
    equiv_point_load = w*len
    
    R1= equiv_point_load * centroid_udl/b
    R2= equiv_point_load - R1
    
    return -R1, -R2

def fe_model_ss_cant(
    w:float,
    b:float,
    a:float,
    E:float,
    I:float,
    A:float,
    J:float,
    nu:float,
    rho:float,   
) ->FEModel3D:
    """
    Returns a Pynite.FEModel3D model of a simply supported beam with a canteliver on one end. Beam is under UDL loading
    
    w - The magnitude of the distributed load
    b - The length of the backspan
    a - The length of the cantilever
    E - The elastic modulus of the beam material
    I - The moment of inertia of the beam section
    A - The cross-sectional area of the beam section
    J - The polar moment of inertia of the beam section
    nu - The Poisson's ratio of the beam material
    rho - The density of the beam material
    
    
    """

    model=FEModel3D()

    G = calc_shear_modulus(nu, E)
    model.add_material("default", E, G, nu, rho)

    model.add_node("N0", 0, 0, 0)
    model.add_node("N1", b, 0, 0)
    model.add_node("N2", b+a, 0, 0)

    model.def_support("N0", True, True, True, True, True, False)
    model.def_support("N1", False, True, False, False, False, False)

    model.add_member("M0", "N0", "N2", "default", Iy=1, Iz=I, J=J, A=A)
    model.add_member_dist_load("M0", "Fy" , w1=w, w2=w)

    return model

def get_spans(tot_beam_len: float, cant_support_loc: float) -> tuple[float, float]:
    """
    Returns the length of the backspan ("b") and the length of the cantilever ("a"), in that order, for a beam with a main span and a canteliver span on one end
    This function will assume that the backspan support is located at 0.0
    """

    cant_span_len = float(tot_beam_len) - float(cant_support_loc)
    main_span_len = float(cant_support_loc)

    return main_span_len, cant_span_len

def convert_to_numeric(data: list[list[str]]) -> list[list[float]]:
    """
    converts a list of strings into a list of floats
    """
    outside_acc = []
    for outside_data in data:
        inner_acc = []
        for inner_data in outside_data:
            inner_acc.append(str_to_float(inner_data))
        outside_acc.append(inner_acc)
    return outside_acc

def read_beam_file(file_name: str) -> list[list[str]]:
    """
    Reads the comma seperated data in a beam file (file_name.txt). Beam file is assumed to be in the following format
    Retruns list of list of str ()

    Beam name
    Length,E,Iz,[Iy,A,J,nu,rho]
    support_loc:support_type,support_loc:support_type, ...
    POINT:load_direction,load_magnitude,load_location,case:load_case
    DIST:load_direction,load_start_magnitude,load_end_magnitude,load_start_location,load_end_location,case:load_case
    ... more loads
    """
    return read_csv_file(file_name)

def separate_lines(file_data: str) -> list[str]:
    """
    Splits line delineated data into a list, with each element representing one line
    """
    lines = str(file_data).split("\n")
    return lines

def separate_data(data: list) -> list[list[str]]:
    """
    separates items in a list to be their own sub-list
    ["A, B, C", "D", "E, F"] -> [["A, B, C"], ["D"], ["E", "F"]]   
    """
    acc = []
    for item in data:
        acc.append(str(item).split(", "))
    return acc

def extract_data(string_list: list, index: int) -> list[str]:
    """
    Returns the data list item corresponding to the index separated out as their own list items
    """
    return string_list[index].split(", ")

def calc_shear_modulus(nu: float, E: float) ->float:
    """
    Retrun shear modulus based on 'E' and 'nu'
    """
    G=E/(2*(1+nu))
    return G

def euler_buckling_load(
    l: float, 
    E: float,
    I: float,
    k: float,
) -> float:
    """
    Returns Euler buckling load based on:
    l: braced length 
    E: Elastic modulus
    I: 2nd  moment of intertia
    k: Effective length factor
    """
    P_cr = math.pi**2 * E * I / (k * l)**2
    return P_cr

def parse_supports(support_list: list[str]) -> dict[float:str]:
    """
    
    # Example input
    ['1000:P', '3800:R', '4800:F', '8000:R']

    # Example output
    {1000: 'P', 3800: 'R', 4800: 'F', 8000: 'R'}
    """
    support_acc ={}
    for support in support_list:
        sup_loc, sup_type = support.split(":")
        support_acc.update({str_to_float(sup_loc): sup_type})
    return support_acc

def parse_loads(load_list: list[list[str|float]]) -> list[dict]:
    """
    # Example input (list[list[str|float])
[
    ['POINT:Fy', -10000.0, 4800.0, 'case:Live'],
    ['DIST:Fy', 30.0, 30.0, 0.0, 4800.0, 'case:Dead']
]

# Example output (list[dict])
[
    {
        "Type": "Point", 
        "Direction": "Fy", 
        "Magnitude": -10000.0, 
        "Location": 4800.0, 
        "Case": "Live"
    },
    {
        "Type": "Dist", 
        "Direction": "Fy",
        "Start Magnitude": 30.0,
        "End Magnitude": 30.0,
        "Start Location": 0.0,
        "End Location": 4800.0,
        "Case": "Dead"
    }
]
"""

    load_acc = []
    for load in load_list:
        load_type = load[0].split(":")[0].title()
        load_dir = load[0].split(":")[1]
        case = load[-1].split(":")[1]
        if load_type.strip() == "Point":
            magnitude = str_to_float(load[1])
            location = str_to_float(load[2])
            load_acc.append({"Type": load_type, "Direction": load_dir, "Magnitude": magnitude, "Location": location, "Case": case})
        elif load_type.strip() == "Dist":
            magnitude_start = str_to_float(load[1])
            magnitude_end = str_to_float(load[2])
            location_start = str_to_float(load[3])
            location_end = str_to_float(load[4])
            load_acc.append({"Type": load_type, "Direction": load_dir, "Start Magnitude": magnitude_start, "End Magnitude": magnitude_end, "Start Location": location_start, "End Location": location_end,"Case": case})
    return load_acc

def parse_beam_attributes(attribute_list: list[float]) -> dict[str:float]:
    """
    Returns a dictionary containing all of the beam attributes required for modelling the beam in PyNite (dict[str, float]).

    If one (or more) of the required beam attributes is not in the list of beam attributes, then assign a default value of 1 for that attribute in the output dict.

    # Example input 1
    [20e3, 200e3, 6480e6, 390e6, 43900, 11900e3, 0.3]

    # Example input 2
    [4800, 24500, 1200000000, 10]

    # Example output 1
    {"L": 20e3, "E": 200e3, "Iz": 6480e6, "Iy": 390e6, "A": 43900, "J": 11900e3, "nu": 0.3, "rho": 1}

    # Example output 2
    {"L": 4800, "E": 24500, "Iz": 1200000000, "Iy": 10, "A": 1, "J": 1, "nu": 1, "rho": 1}"""

    attributes = ["L", "E", "Iz", "Iy", "A", "J", "nu", "rho"]
    acc = {}
    for idx, attribute in enumerate(attributes):
        try:
            acc.update({attribute: attribute_list[idx]})
        except IndexError:
            acc.update({attribute: 1})
    return acc

def get_structured_beam_data(data: list[list[str]]) ->dict:
    """
    Converts list of lists of raw data into dictionary of beam data in the following format
    # Output
    {'Name': 'Balcony transfer',
    'L': 4800.0,
    'E': 24500.0,
    'Iz': 1200000000.0,
    'Iy': 1.0,
    'A': 1.0,
    'J': 1.0,
    'nu': 1.0,
    'rho': 1.0,
    'Supports': {1000.0: 'P', 3800.0: 'R'},
    'Loads': [{'Type': 'Point',
    'Direction': 'Fy',
    'Magnitude': -10000.0,
    'Location': 4800.0,
    'Case': 'Live'},
    {'Type': 'Dist',
    'Direction': 'Fy',
    'Start Magnitude': 30.0,
    'End Magnitude': 30.0,
    'Start Location': 0.0,
    'End Location': 4800.0,
    'Case': 'Dead'}]}
        """
    
    acc = {}
    numeric_data = convert_to_numeric(data)
    acc.update({"Name" : data[0][0]})
    acc.update({**parse_beam_attributes(numeric_data[1])})
    acc.update({"Supports" : parse_supports(numeric_data[2])})
    acc.update({"Loads" : parse_loads(numeric_data[3:])})

    return acc
  
def get_structured_beam_data_from_str_lib(attributes:list, supports:dict, loads: list[dict]) ->dict:
    # Output
    # {'Name': 'Balcony transfer',
    # 'L': 4800.0,
    # 'E': 24500.0,
    # 'Iz': 1200000000.0,
    # 'Iy': 1.0,
    # 'A': 1.0,
    # 'J': 1.0,
    # 'nu': 1.0,
    # 'rho': 1.0,
    # 'Supports': {1000.0: 'P', 3800.0: 'R'},
    # 'Loads': [{'Type': 'Point',
    # 'Direction': 'Fy',
    # 'Magnitude': -10000.0,
    # 'Location': 4800.0,
    # 'Case': 'Live'},
    # {'Type': 'Dist',
    # 'Direction': 'Fy',
    # 'Start Magnitude': 30.0,
    # 'End Magnitude': 30.0,
    # 'Start Location': 0.0,
    # 'End Location': 4800.0,
    # 'Case': 'Dead'}]}

    acc = {}
    acc.update({"Name" : attributes[0],
                'L': attributes[1],
                'E':attributes[2],
                'Iz': attributes[3],
                'Iy': attributes[4],
                'A': attributes[5],
                'J': attributes[6],
                'nu': attributes[7],
                'rho': attributes[8]})
    
    acc.update({"Supports" : supports})
    acc.update({"Loads" : loads})

    return acc
def get_node_locations(support_list:list[str], beam_len: float) -> dict[str, float]:
    """
    Returns a dict[str, float] where keys will be the node names for our beam model (something like "N0" or "N1") and the values will be the position of the node on the x-axis (e.g. 0.0 or 122.5).
    Will include a (non-duplicated) node at start and end of beam + at support locations
    """
    nodes_to_create = support_list[:] # make a copy
    if 0.0 not in support_list:
        nodes_to_create.append(0.0)
    if beam_len not in support_list:
        nodes_to_create.append(beam_len)
        
    node_locations = {}
    for idx, sup_loc in enumerate(sorted(nodes_to_create)):
        node_locations.update({f"N{idx}": sup_loc})
    return node_locations

    ##works but way worse 
    # node_locations = {"N0": 0.0}
    # idx = 0
    # skipper = False
    # for support in support_list:
    #     if support == 0:
    #         idx=idx+1
    #         skipper = True
    #         continue
    #     if skipper == True:
    #         node_locations.update({f"N{idx}": str_to_float(support)})
    #         idx=idx+1
    #     if skipper == False:
    #         node_locations.update({f"N{idx+1}": str_to_float(support)})
    #         idx=idx+1
        
    # if beam_len not in node_locations.values():
    #     if skipper == True:
    #         node_locations.update({f"N{idx}": str_to_float(beam_len)})
    #     if skipper == False:
    #         node_locations.update({f"N{idx+1}": str_to_float(beam_len)})
    # return node_locations

def build_beam(beam_data: dict, combos_bool: bool, **kwargs) -> FEModel3D:
    """
    Returns a beam finite element model for the data in 'beam_data'

    beam data is a dictionary in the following format: 
    {'Name': 'Balcony transfer',
    'L': 4800.0,
    'E': 24500.0,
    'Iz': 1200000000.0,
    'Iy': 1.0,
    'A': 1.0,
    'J': 1,
    'nu': 1,
    'rho': 1,
    'Supports': {1000.0: 'P', 3800.0: 'R'},
    'Loads': [{'Type': 'Point',
    'Direction': 'Fy',
    'Magnitude': -10000.0,
    'Location': 4800.0,
    'Case': 'Live'},
    {'Type': 'Dist',
    'Direction': 'Fy',
    'Start Magnitude': 30.0,
    'End Magnitude': 30.0,
    'Start Location': 0.0,
    'End Location': 4800.0,
    'Case': 'Dead'}]}
    """
    model=FEModel3D()

    name = beam_data["Name"]
    L = beam_data["L"]
    E = beam_data["E"]
    Iz = beam_data["Iz"]
    Iy = beam_data["Iy"]
    A = beam_data["A"]
    J = beam_data["J"]
    nu = beam_data["nu"]
    rho = beam_data["rho"]

    G = calc_shear_modulus(nu, E)
    model.add_material("default", E, G, nu, rho)
    
    restraint_dict = {"P": [True, True, True, True, False, False],
                      "R": [False, True, True, False, False, False],
                      "F": [True, True, True, True, True, True],
                      "Free": [False, False, False, False, False, False]}



    nodes = get_node_locations(list(beam_data["Supports"].keys()), beam_data["L"]) #dict {"str": float}
    supports = beam_data["Supports"]
    for node_num in nodes:
        model.add_node(node_num, nodes[node_num], 0, 0)

    for idx, node in enumerate(nodes.values()):
        fixity = restraint_dict[supports.get(node, "Free")]
        node_name = f"N{idx}"
        model.def_support(node_name, *fixity)
    
    model.add_member(name, "N0", f"N{idx}", "default", Iy = Iy, Iz = Iz, J=J, A=A)

    load_data = beam_data["Loads"]
    load_cases = []
    for load in load_data:
        if load["Type"] == "Point":
            model.add_member_pt_load(name, load["Direction"], load["Magnitude"], load["Location"], load["Case"])
            if load['Case'] not in load_cases:
                load_cases.append(load['Case'])
        elif load["Type"] == "Dist":
            model.add_member_dist_load(name, load["Direction"], load["Start Magnitude"], load["End Magnitude"], load["Start Location"], load["End Location"], load["Case"])
            if load['Case'] not in load_cases:
                load_cases.append(load['Case'])


    if combos_bool:
        combo_dict = loadfactors.CSA_S6_2019_combos(**kwargs)
        for combo in combo_dict:
            model.add_load_combo(combo, combo_dict[combo])
    else:
        for load_case in load_cases:
            model.add_load_combo(load_case, {load_case: 1.0})

    #model.analyze(check_statics=True)
    return model

def load_beam_model(file_name: str, combos_bool :bool = False, **kwargs) -> FEModel3D:
    """
    Converts a beam data file int a FEModel3D ready for analysis.

    Assumes that the data in the beam file describes a simply supported beam with a cantilever on one side and a single UDL loading it in the gravity direction.

    Beam file is assumed to be in the following format
    
   beam data in txt file in the following format: 
    Girder #Name
    20e3,200e3,6480e6,390e6,43900,11900e3,0.3 #L, E, Iz, Iy, A, J, nu, rho (can be left blank)
    0.0:R,17e3:P #Support locations and restraint
    DIST:Fy,3.6,3.6,0.0,20e3,case:D #the rest are all loads
    POINT:Fy,145e3,8e3,case:L
    POINT:Fy,145e3,14.5e3,case:L
    POINT:Fy,145e3,18.3e3,case:L
    """


    beam_txt = read_beam_file(file_name)
    beam_data = get_structured_beam_data(beam_txt)
    model_beam = build_beam(beam_data, combos_bool, **kwargs)

    return model_beam

def extract_arrays_all_combos(solved_beam_model: FEModel3D, result_type: str, direction: str="Fy", n_points:int=500) -> dict:
    """
    result_type: could take values of `"shear"`, `"moment"`, `"axial"`, `"deflection"`, or `"torque"`
    Direction: which could be any of the valid direction strings that PyNite accepts in the context of a certain result type (e.g. `"Fy"`, `"Fx"`, `"Fz"` [for shear] or `"Mx"`, `"My"`, `"Mz"` [for moment], `"dx"`, `"dy"`, `"dz"` [for deflection])
    n_points: the number of points to return
    """
    
    member_name = list(solved_beam_model.Members.keys())[0]
    combo_names = list(solved_beam_model.LoadCombos.keys())
    results = {}
    
    for combo_name in combo_names:
        if result_type.lower().strip() == "shear":
            array = solved_beam_model.Members[member_name].shear_array(direction, n_points, combo_name)
        elif result_type.lower().strip() == "moment":
            array = solved_beam_model.Members[member_name].moment_array(direction, n_points, combo_name)
        elif result_type.lower().strip() == "axial":
            array = solved_beam_model.Members[member_name].axial_array(n_points, combo_name)
        elif result_type.lower().strip() == "torque":
            array = solved_beam_model.Members[member_name].torque_array(n_points, combo_name)
        elif result_type.lower().strip() == "deflection":
            array = solved_beam_model.Members[member_name].deflection_array(direction, n_points, combo_name)

        results.update({combo_name: array})
    return results

# model =load_beam_model("test_data/example_beam_wb6.txt", True)
# model.analyze()
# array = extract_arrays_all_combos(model, "moment", "Mz", 2)
# print(f"{array=}")
# print(loadfactors.load_combo_array(array, "ULS6"))

        
# model = load_beam_model("test_data/example_beam_wb6.txt")
# model.analyze(check_statics=False)
# arr = extract_arrays_all_combos(model, "shear", "Fy", 4)
# #print(arr)
# print(loadfactors.envelope_max(arr))
# print(loadfactors.envelope_min(arr))
# #x = loadfactors.envelope_max(arr)





# print(f"Read Beam: {read_beam_file('eng_module/test_data/beam_4_W3.txt')}")








# raw = read_beam_file('eng_module/test_data/beam_2.txt')
# print(f"raw: {raw}")
# sep = separate_data(raw)
# print(f"list seperated: {sep}")
# numeric = convert_to_numeric(raw)
# print(f"numeric: {numeric}")
# structured = get_structured_beam_data(sep)
# print(f"structured: {structured}")



# model = load_beam_model("eng_module/test_data/beam_2.txt")
# model.add_load_combo("combo 1", {"L": 1, "D":1})
# model.analyze(check_statics=True)

