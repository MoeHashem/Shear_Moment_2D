

def CSA_S6_2019_combos(alpha_D = 1.2, alpha_E = 1.25, alpha_P = 1.05, alpha_L_1 = 1.7, alpha_L_2 = 1.6, alpha_L_3 = 1.4, alpha_L_8 = 0):
    """
    Returns CSA S6 2019 load factors with the appropriate factors

       
    A = ice accretion load
    D = dead load
    E = loads due to earth pressure and hydrostatic pressure, including surcharges but excluding dead load
    EQ = earthquake load
    F = loads due to stream pressure and ice forces or to debris torrents
    H = collision load arising from highway vehicles or vessels
    K = all strains, deformations, and displacements and their effects, including the effects of their restraint and the effects of friction
    or stiffness in bearings. Strains and deformations include strains and deformations due to temperature change and
    temperature differential, concrete shrinkage, differential shrinkage, and creep, but not elastic strains
    L = live load (including the dynamic load allowance, when applicable), including barrier loads
    P = secondary prestress effects
    S = load due to differential settlement and/or movement of the foundation
    V = wind load on traffic
    W = wind load on structure


    """

    CSA_S6_2019_COMBOS = {
        "unfactored" : {"D": 1, "E": 1, "P": 1, "L": 1, "K": 1, "W": 1, "V": 1, "S": 1, "EQ": 1, "F": 1, "A": 1, "H": 1},
        "FLS1" : {"D": 1, "E": 1, "P": 1, "L": 1, "K": 0, "W": 0, "V": 0, "S": 0, "EQ": 0, "F": 0, "A": 0, "H": 0}, 
        "SLS1" : {"D": 1, "E": 1, "P": 1, "L": 0.9, "K": 0.8, "W": 0, "V": 0, "S": 1, "EQ": 0, "F": 0, "A": 0, "H": 0},
        "SLS2" : {"D": 0, "E": 0, "P": 0, "L": 0.9, "K": 0, "W": 0, "V": 0, "S": 0, "EQ": 0, "F": 0, "A": 0, "H": 0}, 
        "ULS1" : {"D": alpha_D, "E": alpha_E, "P": alpha_P, "L": alpha_L_1, "K": 0, "W": 0, "V": 0, "S": 0, "EQ": 0, "F": 0, "A": 0, "H": 0}, 
        "ULS2" : {"D": alpha_D, "E": alpha_E, "P": alpha_P, "L": alpha_L_2, "K": 1.15, "W": 0, "V": 0, "S": 0, "EQ": 0, "F": 0, "A": 0, "H": 0}, 
        "ULS3" : {"D": alpha_D, "E": alpha_E, "P": alpha_P, "L": alpha_L_3, "K": 1, "W": 0.45, "V": 0.45, "S": 0, "EQ": 0, "F": 0, "A": 0, "H": 0}, 
        "ULS4" : {"D": alpha_D, "E": alpha_E, "P": alpha_P, "L": 0, "K": 1.25, "W": 1.4, "V": 0, "S": 0, "EQ": 0, "F": 0, "A": 0, "H": 0}, 
        "ULS5" : {"D": alpha_D, "E": alpha_E, "P": alpha_P, "L": 0, "K": 0, "W": 0, "V": 0, "S": 0, "EQ": 1, "F": 0, "A": 0, "H": 0}, 
        "ULS6" : {"D": alpha_D, "E": alpha_E, "P": alpha_P, "L": 0, "K": 0, "W": 0, "V": 0, "S": 0, "EQ": 0, "F": 1.3, "A": 0, "H": 0}, 
        "ULS7" : {"D": alpha_D, "E": alpha_E, "P": alpha_P, "L": 0, "K": 0, "W": 0.75, "V": 0, "S": 0, "EQ": 0, "F": 0, "A": 1.3, "H": 0}, 
        "ULS8" : {"D": alpha_D, "E": alpha_E, "P": alpha_P, "L": alpha_L_8, "K": 0, "W": 0, "V": 0, "S": 0, "EQ": 0, "F": 0, "A": 0, "H": 0}, 
        "ULS9" : {"D": 1.35, "E": alpha_E, "P": alpha_P, "L": 0, "K": 0, "W": 0, "V": 0, "S": 0, "EQ": 0, "F": 0, "A": 0, "H": 0}
         
        }
    return CSA_S6_2019_COMBOS



def get_alpha_factors (material_type: str = "M2", alpha_D_max_min: int = 0,
                       earth_pressure_type: str = "E1", alpha_E_max_min: int = 0,
                       alpha_P_max_min: int = 0, 
                       L_span_type: str = "Normal", L_vehicle_vessle: int = 0
                       ) -> tuple:
    """
    Returns in this order: alpha_D, alpha_E, alpha_P, alpha_L_1, alpha_L_2, alpha_L_3, alpha_L_8

    *max_min variables should be 0 for max, 1 for min
    *L_vehicle_vessle should be 0 for vehicle collision, 1 for vessle collision
    *Type variables should be one of these exact strings:

    Material_type:
    - "M1" : Factory-produced components, excluding wood
    - "M2" : Cast-in-place concrete, wood, and all non-structural components
    - "M3" : Wearing surfaces, based on nominal or specified thickness
    - "M4" : Earth fill, negative skin friction on piles
    - "M5" : Water
    - "M6" : Dead load in combination with earthquakes (ULS5)
    
    Earth Pressure Type:
    - "E1" : Passive earth pressure, considered as a load*
    - "E2" : At-rest earth pressure
    - "E3" : Active earth pressure
    - "E4" : Backfill pressure
    - "E5" : Hydrostatic pressure
    
    Live load span type
    - "Normal": Normal load
    - "Special_mixed_short": Special loads mixed with normal traffic for short spans
    - "Special_mixed_other": Special loads mixed with normal traffic for other spans
    - "Special_alone_short": Special loads for short spans
    - "Special_alone_other": Special loads for other spans
    
    """

    material_type_dict = {
        "M1":(1.1, 0.95),
        "M2":(1.2, 0.9),
        "M3":(1.5, 0.65),
        "M4":(1.25, 0.8),
        "M5":(1.1, 0.9),
        "M6":(1.25, 0.8)}
    
    earth_pressure_type_dict = {
        "E1":(1.25, 0.5),
        "E2":(1.25, 0.8),
        "E3":(1.25, 0.8),
        "E4":(1.25, 0.8),
        "E5":(1.1, 0.9)}
    
    live_load_dict = {
        "Normal": (1.7, 1.6, 1.4),
        "Special_mixed_short": (1.7, 1.6, 1.4),
        "Special_mixed_other": (1.5, 1.4, 1.25),
        "Special_alone_short": (1.5, 1.4, 1.25),
        "Special_alone_other": (1.35, 1.25, 1.1)
    }

    alpha_D = material_type_dict.get(material_type)[alpha_D_max_min]
    alpha_E = earth_pressure_type_dict.get(earth_pressure_type)[alpha_E_max_min]
    
    if alpha_P_max_min == 0:
        alpha_P = 1.05
    else:
        alpha_P = 0.95

    alpha_L_1, alpha_L_2, alpha_L_3 = live_load_dict.get(L_span_type)    
        
    if L_vehicle_vessle == 0:
        alpha_L_8 = 0
    else:
        alpha_L_8 = 0.5

    return alpha_D, alpha_E, alpha_P, alpha_L_1, alpha_L_2, alpha_L_3, alpha_L_8

   
def factor_loads(D_load: float = 0., D: float = 0., 
                E_load: float = 0., E: float = 0.,
                P_load: float = 0., P: float = 0.,
                L_load: float = 0., L: float = 0.,
                K_load: float = 0., K: float = 0.,
                W_load: float = 0., W: float = 0.,
                V_load: float = 0., V: float = 0.,
                S_load: float = 0., S: float = 0.,
                EQ_load: float = 0., EQ: float = 0.,
                F_load: float = 0., F: float = 0.,
                A_load: float = 0., A: float = 0.,
                H_load: float = 0., H: float = 0.              
                ):
    
    return D*D_load + E*E_load + P*P_load + L*L_load + K*K_load + W*W_load + V*V_load + S*S_load + EQ*EQ_load + F*F_load + A*A_load + H*H_load

def max_factored_load(loads: dict, load_combos: dict):
    results = []
    cmb_list = list(load_combos.keys())

    for combo in load_combos.values():
        results.append(factor_loads(**loads, **combo))
        
        
    max_index = max(range(len(results)), key=results.__getitem__)
    max_result = results[max_index]
    max_cmb = cmb_list[max_index]

    return max_result, max_cmb
     
def min_factored_load(loads: dict, load_combos: dict):
    results = []
    cmb_list = list(load_combos.keys())

    for combo in load_combos.values():
        results.append(factor_loads(**loads, **combo))
        
        
    min_index = min(range(len(results)), key=results.__getitem__)
    min_result = results[min_index]
    min_cmb = cmb_list[min_index]

    return min_result, min_cmb   

def envelope_max(results_arrays:dict) -> list[list[float], list[float]]:
    """
    Outputs the X-coordinates and the Max Factored load at each coord, each in their own list
    """
    
    
    # S6_combos = CSA_S6_2019_combos()
    # all_cases = {"D": "D_load", "E": "E_load", "P": "P_load", "L": "L_load", "K": "K_load", "W": "W_load", "V": "V_load", "S": "S_load", "EQ": "EQ_load", "F": "F_load", "A": "A_load", "H": "H_load"}
    combo_names = list(results_arrays.keys())
    x_points = list(results_arrays[combo_names[0]][0])
    values = []
    for combo in combo_names:
        values.append(results_arrays[combo][1])
    max_array = []
    for idx, x_point in enumerate(x_points):
        max_at_idx = []
        for value in values:
            max_at_idx.append(value[idx])
        # print(f"{max_at_idx=}")
        max_array.append(max(max_at_idx))
    # print(f"{max_array=}")
    return [x_points, max_array]
        
    # loads_dict = {}
    # for combo_name in combo_names:
    #     load_values = list(results_arrays[combo_name][1])
    #     loads_dict.update({all_cases[combo_name]: load_values})
    # acc_max_factored_load = []
               
        # factored_loads_dict = {}
    #     for current_case in loads_dict:
    #         factored_loads_dict.update({current_case: loads_dict[current_case][idx]})
    #     #print(f"{factored_loads_dict=}")
    #     acc_max_factored_load.append(max_factored_load(factored_loads_dict, S6_combos)[0])
    # return [x_points, acc_max_factored_load]


def envelope_min(results_arrays:dict) -> list[list[float], list[float]]:
    """
    Outputs the X-coordinates and the min Factored load at each coord, each in their own list
    """

    combo_names = list(results_arrays.keys())
    x_points = list(results_arrays[combo_names[0]][0])
    values = []
    for combo in combo_names:
        values.append(results_arrays[combo][1])
    min_array = []
    for idx, x_point in enumerate(x_points):
        min_at_idx = []
        for value in values:
            min_at_idx.append(value[idx])
        # print(f"{min_at_idx=}")
        min_array.append(min(min_at_idx))
    # print(f"{min_array=}")
    return [x_points, min_array]
    # S6_combos = CSA_S6_2019_combos()
    # all_cases = {"D": "D_load", "E": "E_load", "P": "P_load", "L": "L_load", "K": "K_load", "W": "W_load", "V": "V_load", "S": "S_load", "EQ": "EQ_load", "F": "F_load", "A": "A_load", "H": "H_load"}
    # combo_names = list(results_arrays.keys())
    # x_points = list(results_arrays[combo_names[0]][0])
    # loads_dict = {}
    # for combo_name in combo_names:
    #     load_values = list(results_arrays[combo_name][1])
    #     loads_dict.update({all_cases[combo_name]: load_values})
    # acc_min_factored_load = []
    # for idx, x_point in enumerate(x_points):
    #     factored_loads_dict = {}
    #     for current_case in loads_dict:
    #         factored_loads_dict.update({current_case: loads_dict[current_case][idx]})
    #     #print(f"{factored_loads_dict=}")
    #     acc_min_factored_load.append(min_factored_load(factored_loads_dict, S6_combos)[0])
    # return [x_points, acc_min_factored_load]


def load_combo_array(results_arrays:dict, target_combo):
    """
    Outputs the Outputs the X-coordinates and the Factored load at each coord for a specivfic load combo, each in their own list
    """

    combo_names = list(results_arrays.keys())
    x_points = list(results_arrays[combo_names[0]][0])
    values = list(results_arrays[target_combo][1])
    
    
    return [x_points, values]



    # S6_combos = CSA_S6_2019_combos()
    # used_combo = S6_combos[target_combo] #{'D': 1.2, 'E': 1.25, 'P': 1.05, 'L': 1.7, 'K': 0, 'W': 0, 'V': 0, 'S': 0, 'EQ': 0, 'F': 0, 'A': 0, 'H': 0}
    # all_cases = {"D": "D_load", "E": "E_load", "P": "P_load", "L": "L_load", "K": "K_load", "W": "W_load", "V": "V_load", "S": "S_load", "EQ": "EQ_load", "F": "F_load", "A": "A_load", "H": "H_load"}
    # used_cases = list(results_arrays.keys())
    # x_points = list(results_arrays[used_cases[0]][0])
    # loads_dict = {} #{'D_load': [0.0, -216000.0, -4.656612873077393e-10], 'L_load': [1.3969838619232178e-09, -3960000.0, -5.136826075613499e-09]}
    # for case in used_cases:
    #     load_values = list(results_arrays[case][1])
    #     loads_dict.update({all_cases[case]: load_values})
    # #print(f"{loads_dict=}")
    # factored_result_acc = []
    # for idx, x_point in enumerate(x_points):
    #     indexed_loads_dict = {}
    #     for current_case in loads_dict:
    #         indexed_loads_dict.update({current_case: loads_dict[current_case][idx]})
    #     #print(f"{indexed_loads_dict=}")
    #     factored_result_acc.append(factor_loads(**used_combo, **indexed_loads_dict))
    # #print(f"{factored_result_acc=}")
    # return [x_points, factored_result_acc]

##for every node multiply the D_load by the D factor then l_load by the L factor etc...


    

# loads = {"D_load": 1, "L_load": 1}
# combos = CSA_S6_2019_combos(*get_alpha_factors("M3", 0, "E4", 0, 0, "Normal", 0))
# X = max_factored_load(loads, combos), min_factored_load(loads, combos)
# print(X)