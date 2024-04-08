"""
A model with a single fuel element. Infinite in z, and with reflective
boundary conditions
"""

import openmc
import openmc.statepoint
import geometry_definitions as gd

openmc.config['cross_sections'] = "/filespace/e/epflug/research/endfb-viii.0-hdf5/cross_sections.xml"

materials = openmc.Materials.from_xml('materials.xml')

propellent = gd.get_material(materials, "Hydrogen STP")
clad = gd.get_material(materials, 'zirconium_carbide')
fuel = gd.get_material(materials, "graphite_fuel_70U_15C")

fuel_element = gd.fuel_assembly(propellent, clad, fuel,'reflective')

geometry = openmc.Geometry(fuel_element)

particles = 500
inactive = 10
batches = 30

settings = openmc.Settings()
settings.batches = batches
settings.inactive = inactive
settings.particles = particles
source = openmc.IndependentSource()
source.space = openmc.stats.Point()
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Watt()
settings.source = source

#filters
fuel_cells_filter = openmc.CellFilter([3,4])

#tallies
heating_tally = openmc.Tally(name='heating tally')
heating_tally.filters = [fuel_cells_filter]
heating_tally.scores = ['heating']

tallies = openmc.Tallies([heating_tally])

model = openmc.Model(materials=materials, geometry=geometry, settings=settings,
                     tallies=tallies)

model.update_cell_temperatures(list(geometry.get_all_cells().keys()),2500)

model.export_to_model_xml()

model.run()