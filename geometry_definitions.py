"""
The idea here is to define functions that return the building blocks
fuel elements/tie tubes, and that will fill these with the appropriate materials
The main function will plot both with sample materials
"""

import openmc
import numpy as np
import matplotlib.pyplot as plt


def get_material(materials, name):
    """
    searches materials object for a matching name and returns it
    """
    for material in materials:
        if material.name == name:
            return material


def fuel_assembly(propellent, clad, fuel):
    # build a single element
    # Measurements from Schnitzler et al. 2012
    propellant_channel_diameter = 0.2565
    propellant_channel_inner_cladding_thickness = 0.01
    propellant_channel_pitch = 0.4089
    assembly_cladding_thickness = 0.005
    flat_to_flat = 1.905
    flat_to_flat_fuel = flat_to_flat - assembly_cladding_thickness
    assembly_edge_length = 0.5*flat_to_flat/np.cos(np.deg2rad(30))
    fuel_edge_length = 0.5*flat_to_flat_fuel/np.cos(np.deg2rad(30))

    # OpenMC Geometry
    borehole = openmc.ZCylinder(r=propellant_channel_diameter/2)
    borehole_inner_cladding = openmc.ZCylinder(r=propellant_channel_diameter/2
                                               - propellant_channel_inner_cladding_thickness)
    fuel_assembly = openmc.model.HexagonalPrism(
        orientation='x', edge_length=fuel_edge_length)
    fuel_assembly_cladding = openmc.model.HexagonalPrism(
        orientation='x', edge_length=assembly_edge_length)

    # OpenMC Cells and Universes
    propellant_channel_interior = openmc.Cell(
        region=-borehole_inner_cladding, fill=propellent)
    propellant_channel_cladding = openmc.Cell(
        region=-borehole & +borehole_inner_cladding, fill=clad)
    propellant_channel_outer_fuel = openmc.Cell(region=+borehole, fill=fuel)
    propellant_channel = openmc.Universe(cells=(propellant_channel_interior, propellant_channel_cladding,
                                                propellant_channel_outer_fuel))
    fuel_assembly_cell = openmc.Cell(region=-fuel_assembly, fill=fuel)
    fuel_assembly_cladding_cell = openmc.Cell(
        region=+fuel_assembly & -fuel_assembly_cladding, fill=clad)

    outer_lattice_universe = openmc.Universe(cells=[fuel_assembly_cell])

    # OpenMC Fuel Lattice
    fuel_lattice = openmc.HexLattice()
    fuel_lattice.orientation = "x"
    fuel_lattice.outer = outer_lattice_universe
    fuel_lattice.pitch = (propellant_channel_pitch,)
    fuel_lattice.universes = [[propellant_channel] *
                              12, [propellant_channel]*6, [propellant_channel]]
    fuel_lattice.center = (0.0, 0.0)

    # Full Fuel Asembly
    fuel_assembly_lattice_cell = openmc.Cell(
        region=-fuel_assembly, fill=fuel_lattice)
    fuel_assembly_universe = openmc.Universe(cells=[fuel_assembly_cladding_cell,
                                                    fuel_assembly_lattice_cell])

    return fuel_assembly_universe


def tie_tube(hydrogen_inner, hydrogen_outer, inconel, ZrH, ZrC, ZrC_insulator, graphite):
    
    #THIS IS A GUESS BASED ON THE FUEL ELEMENT
    assembly_cladding_thickness = 0.005
    
    inner_hydrogen_outer_radius = 0.20955
    inner_tie_tube_outer_radius = 0.26035
    first_gap_outer_radius = 0.26670
    moderator_outer_radius = 0.58420
    second_gap_outer_radius = 0.67818
    outer_tie_tube_outer_radius = 0.69850
    third_gap_outer_radius = 0.70485
    insulator_outer_radius = 0.80645
    fourth_gap_outer_radius = 0.81280
    flat_to_flat = 1.905
    flat_to_flat_inner = flat_to_flat-2*assembly_cladding_thickness
    assembly_edge_length = 0.5*flat_to_flat/np.cos(np.deg2rad(30))
    inner_edge_length = 0.5*flat_to_flat_inner/np.cos(np.deg2rad(30))

    # OpenMC Geometry
    inner_hydrogen = openmc.ZCylinder(r=inner_hydrogen_outer_radius)
    inner_tie_tube = openmc.ZCylinder(r=inner_tie_tube_outer_radius)
    first_gap = openmc.ZCylinder(r=first_gap_outer_radius)
    moderator_tube = openmc.ZCylinder(r=moderator_outer_radius)
    second_gap = openmc.ZCylinder(r=second_gap_outer_radius)
    outer_tie_tube = openmc.ZCylinder(r=outer_tie_tube_outer_radius)
    third_gap = openmc.ZCylinder(r=third_gap_outer_radius)
    insulator = openmc.ZCylinder(r=insulator_outer_radius)
    fourth_gap = openmc.ZCylinder(r=fourth_gap_outer_radius)
    tie_tube_assembly = openmc.model.HexagonalPrism(orientation='x',
                                                    edge_length=inner_edge_length)
    tie_tube_assembly_cladding = openmc.model.HexagonalPrism(orientation='x',
                                                             edge_length=assembly_edge_length)

    # OpenMC Cells and Universes
    inner_hydrogen_cell = openmc.Cell(region=-inner_hydrogen, fill=hydrogen_inner)
    inner_tie_tube_cell = openmc.Cell(
        region=+inner_hydrogen & - inner_tie_tube, fill=inconel)
    first_gap_cell = openmc.Cell(region=+inner_tie_tube & -first_gap, fill=hydrogen_outer)
    moderator_tube_cell = openmc.Cell(region=+first_gap & -moderator_tube,fill=ZrH)
    outer_hydrogen_cell = openmc.Cell(region=+moderator_tube & -second_gap, fill=hydrogen_outer)
    outer_tie_tube_cell = openmc.Cell(region=+second_gap & -outer_tie_tube, fill=inconel)
    third_gap_cell = openmc.Cell(region=+outer_tie_tube & -third_gap, fill=hydrogen_outer)
    insulator_cell = openmc.Cell(region=+outer_tie_tube & -insulator,fill = ZrC_insulator)
    fourth_gap_cell = openmc.Cell(region=+insulator & -fourth_gap, fill=hydrogen_outer)
    tie_tube_assembly_cell = openmc.Cell(region=-tie_tube_assembly & +fourth_gap, fill=graphite)
    tie_tube_assembly_cladding_cell = openmc.Cell(
        region=+tie_tube_assembly & -tie_tube_assembly_cladding, fill=ZrC)

    # Full Tie Tube Assembly
    tie_tube_assembly_universe = openmc.Universe(cells=[inner_hydrogen_cell, inner_tie_tube_cell, first_gap_cell,
                                                        moderator_tube_cell, outer_hydrogen_cell, outer_tie_tube_cell,
                                                        third_gap_cell, insulator_cell, fourth_gap_cell,
                                                        tie_tube_assembly_cell, tie_tube_assembly_cladding_cell])
    
    return tie_tube_assembly_universe


def main():
    # plot a sample geometry by material type

    materials = openmc.Materials.from_xml('materials.xml')

    hydrogen = get_material(materials, "Hydrogen STP")
    ZrC = get_material(materials, "zirconium_carbide")
    graphite_fuel = get_material(materials, "graphite_fuel_70U_15C")
    ZrH = get_material(materials, 'zirconium_hydride_II')
    inconel = get_material(materials, "inconel-718")
    ZrC_insulator = get_material(materials,'zirconium_carbide_insulator')
    graphite = get_material(materials, 'graphite_carbon')

    fuel_assembly_geom = openmc.Geometry(fuel_assembly(hydrogen, ZrC, graphite_fuel))
    fuel_assembly_geom.plot(pixels=(800, 800), width=(3, 3), color_by='material')
    plt.savefig('fuel_element_by_material.png')
    fuel_assembly_geom.plot(pixels=(800, 800), width=(3, 3), color_by='cell')
    plt.savefig('fuel_element_by_cell.png')

    tie_tube_geom = openmc.Geometry(tie_tube(hydrogen,hydrogen,inconel,ZrH,ZrC,ZrC_insulator,graphite))
    tie_tube_geom.plot(pixels=(800, 800), width=(3, 3), color_by='material')
    plt.savefig('tie_tube_element_by_material.png')
    tie_tube_geom.plot(pixels=(800, 800), width=(3, 3), color_by='cell')
    plt.savefig('tie_tube_element_by_cell.png')


if __name__ == '__main__':
    main()
