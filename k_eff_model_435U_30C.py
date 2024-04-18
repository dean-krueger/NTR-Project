import openmc
from geometry_definitions import *

height = 100
inner_gap_inner_radius = 29.5275


materials = openmc.Materials.from_xml('materials.xml')

graphite_fuel = get_material(materials, 'graphite_fuel_435U_30C')
hydrogen = get_material(materials, 'Hydrogen STP')
ZrC = get_material(materials, "zirconium_carbide")
inconel = get_material(materials, "inconel-718")
ZrH = get_material(materials, "zirconium_hydride_II")
ZrC_insulator = get_material(materials, "zirconium_carbide_insulator")
graphite = get_material(materials, "graphite_carbon")
beryllium = get_material(materials, 'beryllium')
SS316L = get_material(materials, "SS316L")
poison = get_material(materials, "CuB_poison")

FA = fuel_assembly(hydrogen, ZrC, graphite_fuel)
TT = tie_tube(hydrogen,hydrogen,inconel,ZrH,ZrC,ZrC_insulator,graphite)
BE = beryllium_assembly(beryllium, ZrC)

core_lattice_SNRE_geom = openmc.Geometry(core_lattice_SNRE(TT, FA, BE))
core_lattice_SNRE_geom.plot(pixels=(800, 800), width=(60, 60), color_by='material')
plt.savefig('SNRE_full_lattice.png')

core = core_lattice_SNRE(TT,FA,BE)
inner_reflector_universe = inner_reflector(core, hydrogen, SS316L, beryllium, height)

full_core_geom = openmc.Geometry(full_core(inner_reflector_universe, poison, beryllium, inconel, height, 180))
full_core_geom.plot(pixels=(800, 800), width=(100, 100), color_by='material')
plt.savefig('SNRE_full_core_radial_cross_section.png')
full_core_geom.export_to_xml()
print(full_core_geom.bounding_box)

#setup shannon entropy
lower_left = (-inner_gap_inner_radius, -inner_gap_inner_radius, -height/2)
upper_right = (inner_gap_inner_radius, inner_gap_inner_radius, height/2)

entropy_mesh = openmc.RegularMesh()
entropy_mesh.lower_left = lower_left
entropy_mesh.upper_right = upper_right
entropy_mesh.dimension = [30,30,10]

#setup source sampling
uniform_dist = openmc.stats.Box(lower_left, upper_right, only_fissionable = True)


settings = openmc.Settings()
settings.particles = 1000000
settings.batches = 100
settings.inactive = 50
settings.entropy_mesh = entropy_mesh
settings.source = openmc.IndependentSource(space=uniform_dist)

model = openmc.Model(materials=materials, settings=settings, geometry=full_core_geom)

model.run()