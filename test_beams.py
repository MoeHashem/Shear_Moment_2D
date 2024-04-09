import eng_module.beams as beams
from PyNite import FEModel3D
import pytest
import math

def test_convert_to_numeric():
    ex_data_1 = [['Balcony transfer'],
    ['4800', '24500', '1200000000', '1', '1'],
    ['1000:P', '3800:R'],
    ['POINT:Fy', '-10000', '4800', 'case:Live'],
    ['DIST:Fy', '30', '30', '0', '4800', 'case:Dead']]

    assert beams.convert_to_numeric(ex_data_1) == [['Balcony transfer'],
    [4800.0, 24500.0, 1200000000.0, 1.0, 1.0],
    ['1000:P', '3800:R'],
    ['POINT:Fy', -10000.0, 4800.0, 'case:Live'],
    ['DIST:Fy', 30.0, 30.0, 0.0, 4800.0, 'case:Dead']]


def test_calc_shear_modulus():
    # Material 1
    E1 = 200000 # MPa
    nu1 = 0.3

    # Material 2
    E2 = 3645 # ksi ("ksi" == "kips per square inch"; "kips" == "kilopound" == 1000 lbs)
    nu2 = 0.2

    assert beams.calc_shear_modulus(nu1, E1) == 76923.07692307692
    assert beams.calc_shear_modulus(nu2, E2) == 1518.75

def test_euler_buckling_load():
    # Column 1 - Value will be in Newtons
    l1 = 5300 # mm
    E1 = 200000 # MPa
    I1 = 632e6 # mm**4
    k1 = 1.0

    # Column 2 - Value will be in kips ("kips" == "kilopound" == 1000 lbs)
    l2 = 212 # inch
    E2 = 3645 # ksi ("ksi" == "kips per square inch")
    I2 = 5125.4 # inch**4
    k2 = 2.0

    assert beams.euler_buckling_load(l1, E1, I1, k1) == 44411463.02234584
    assert beams.euler_buckling_load(l2, E2, I2, k2) == 1025.6361727834453

def test_beam_reactions_ss_cant():
    # Beam 1
    w1 = 50 # kN/m (which is the same as N/mm)
    a1 = 2350 # mm
    b1 = 4500 # mm

    # Beam 2 # Equal spans; should get 0.0 at backspan reaction
    w2 = 19 # lbs/inch == 228 lbs/ft
    a2 = 96 # inch
    b2 = 96 # inch

    R1_1, R2_1 = beams.beam_reactions_ss_cant(w1, a1, b1)
    R1_2, R2_2 = beams.beam_reactions_ss_cant(w2, a2, b2)
    assert (round(R1_1, 2), round(R2_1, 2)) == (-260680.56, -81819.44)
    assert (round(R1_2, 2), round(R2_2, 2)) == (-3648.0, -0.0)

def test_fe_model_ss_cant():
    # Beam 1
    w1 = 50 # kN/m (which is the same as N/mm)
    a1 = 2350 # mm
    b1 = 4500 # mm

    # Beam 2 # Equal spans; should get 0.0 at backspan reaction
    w2 = 19 # lbs/inch == 228 lbs/ft
    a2 = 96 # inch
    b2 = 96 # inch

    E=1
    I=1
    A=1
    J=1
    nu=1
    rho = 1

    model1 = beams.fe_model_ss_cant(w1, b1, a1, E, I, A, J, nu, rho)
    model1.analyze()

    R2_1 = model1.Nodes["N0"].RxnFY['Combo 1']
    R1_1 = model1.Nodes["N1"].RxnFY['Combo 1']

    aR1_1, aR2_1 = beams.beam_reactions_ss_cant(w1, a1, b1)

    assert round(aR1_1, 2) == round(R1_1, 2)
    assert round(aR2_1, 2) == round(R2_1, 2)



    model2 = beams.fe_model_ss_cant(w2, b2, a2, E, I, A, J, nu, rho)
    model2.analyze()

    R2_2 = model2.Nodes["N0"].RxnFY['Combo 1']
    R1_2 = model2.Nodes["N1"].RxnFY['Combo 1']

    aR1_2, aR2_2 = beams.beam_reactions_ss_cant(w2, a2, b2)

    assert round(aR1_2, 2) == round(R1_2, 2)
    assert round(aR2_2, 2) == round(R2_2, 2)

def test_read_beam_file():
    beam1_data = beams.read_beam_file('test_data/beam_1-wb4.txt')
    assert beam1_data == [['Balcony transfer'], ['4800', '24500', '1200000000', '1', '1'], ['1000:P', '3800:R'], ['POINT:Fy', '-10000', '4800', 'case:Live'], ['DIST:Fy', '30', '30', '0', '4800', 'case:Dead']]
   
def test_separate_lines():
    example_1_data = "cat, bat, hat\ntroll, scroll, mole"
    example_2_data = ""
    example_3_data = "aaa, bbb, ccc\nddd\neee, fff\n"
    assert beams.separate_lines(example_1_data) == ["cat, bat, hat", "troll, scroll, mole"]
    assert beams.separate_lines(example_2_data) == [""]
    assert beams.separate_lines(example_3_data) == ["aaa, bbb, ccc", "ddd", "eee, fff", ""]

def test_separate_data():
    ex_data_1 = ['Roof beam',
    '4800, 19200, 1000000000',
    '0, 3000',
    '100, 500, 4800',
    '200, 3600, 4800']
    
    assert beams.separate_data(ex_data_1) == [['Roof beam'],['4800', '19200', '1000000000'],['0', '3000'],['100', '500', '4800'],['200', '3600', '4800']]
                                            

def test_extract_data():
    example_1_data = ["cat, bat, hat", "troll, scroll, mole"]
    example_2_data = [""]
    example_3_data = ["aaa, bbb, ccc", "ddd", "eee, fff", ""]
    assert beams.extract_data(example_1_data, 0) == ["cat", "bat", "hat"]
    assert beams.extract_data(example_1_data, 1) == ["troll", "scroll", "mole"]
    assert beams.extract_data(example_2_data, 0) == [""]
    assert beams.extract_data(example_3_data, 2) == ["eee", "fff"]
    

def test_get_spans():
    assert beams.get_spans(10, 7) == (7, 3)
    assert beams.get_spans(30,10) == (10, 20)
    assert beams.get_spans(5, 0) == (0, 5)

def test_load_beam_model():
    
    beam_model = beams.load_beam_model("test_data/beam_3-wb4.txt")
    beam_model.analyze(check_statics=False)
    assert math.isclose(beam_model.Members['My test beam'].min_deflection("dy", combo_name="Dead"),  -58.12, rel_tol=1e-4)


def test_get_structured_beam_data():
    ex_data_1 = [['Balcony transfer'],
    ['4800', '24500', '1200000000', '1', '1'],
    ['1000:P', '3800:R'],
    ['POINT:Fy', '-10000', '4800', 'case:Live'],
    ['DIST:Fy', '30', '30', '0', '4800', 'case:Dead']]


    assert beams.get_structured_beam_data(ex_data_1) == {'Name': 'Balcony transfer',
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

def test_get_node_locations():
    
    assert beams.get_node_locations([1000.0, 4000.0, 8000.0], 10000) == {"N0": 0.0, "N1": 1000.0, "N2": 4000.0, "N3": 8000.0, "N4": 10000.0}
    assert beams.get_node_locations([0, 100], 100) == {"N0": 0.0, "N1": 100.0}
    assert beams.get_node_locations([0, 50], 100) == {"N0": 0.0, "N1": 50.0, "N2": 100}
    assert beams.get_node_locations([5, 100], 100) == {"N0": 0.0, "N1": 5, "N2": 100.0}

def test_parse_supports():
    ex_data = ['1000:P', '3800:R', '4800:F', '8000:R']
    assert beams.parse_supports(ex_data) == {1000: 'P', 3800: 'R', 4800: 'F', 8000: 'R'}

def test_parse_loads():
    ex_data = [
    ['POINT:Fy', -10000.0, 4800.0, 'case:Live'],
    ['DIST:Fy', 30.0, 30.0, 0.0, 4800.0, 'case:Dead']]

    assert beams.parse_loads(ex_data) == [
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

def test_parse_beam_attributes():
    ex_data_1 = [20e3, 200e3, 6480e6, 390e6, 43900, 11900e3, 0.3]
    ex_data_2 = [4800, 24500, 1200000000, 10]

    assert beams.parse_beam_attributes(ex_data_1) == {"L": 20e3, "E": 200e3, "Iz": 6480e6, "Iy": 390e6, "A": 43900, "J": 11900e3, "nu": 0.3, "rho": 1}
    assert beams.parse_beam_attributes(ex_data_2) == {"L": 4800, "E": 24500, "Iz": 1200000000, "Iy": 10, "A": 1, "J": 1, "nu": 1, "rho": 1}