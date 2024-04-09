import beams
import loadfactors

structured_data ={
  "Name": "Beam Name",
  "L": 100,
  "E": 1.01,
  "Iz": 1,
  "Iy": 1,
  "A": 1,
  "J": 1,
  "nu": 1,
  "rho": 1,
  "Supports": {
    1.0: "P",
    100.0: "P"
  },
  "Loads": [
    {
      "Type": "Point",
      "Direction": "Fy",
      "Magnitude": 8000000,
      "Location": 50,
      "Case": "D"
    }
  ]
}



# {
#   "Name": "Beam Name",
#   "L": 4800,
#   "E": 2450,
#   "Iz": 12000,
#   "Iy": 111111,
#   "A": 111,
#   "J": 111111,
#   "nu": 0.99,
#   "rho": 1,
#   "Supports": {
#     0.0: "P",
#     4000.0: "P"
#   },
#   "Loads": [
#     {
#       "Type": "POINT",
#       "Direction": "Fy",
#       "Magnitude": 1000,
#       "Location": 500,
#       "Case": "Dead"
#     }
#   ]
# }


model = beams.build_beam(structured_data, 1)
model.analyze(check_statics=False)

    

shear_arrays = beams.extract_arrays_all_combos(model, "shear", "Fy", 5)
env_shear_x_y = loadfactors.load_combo_array(shear_arrays, "ULS1")
print(env_shear_x_y)