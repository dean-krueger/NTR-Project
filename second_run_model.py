# %%
import geometry_definitions as gd
import openmc
import numpy as np
import pandas as pd

# %%
# From Linear Interpolation of Control Drum Data
critical_insertion_angle = 180 - 52
fuel_name = "graphite_fuel_435U_30C"
core_height = 89

# Generate the Model:
model = gd.get_model(core_height ,critical_insertion_angle)

model.settings.batches = 200
model.settings.particles = 1_000_000
model.settings.inactive = 40
model.settings.temperature = {'default':2500}
model.settings.photon_transport = True
model.settings.statepoint = {'batches': [80,100,120,130,170,190,200]}
model.settings.trigger_batch_interval = 10
model.settings.trigger_max_batches = 200
model.settings.trigger_active = True

# Create Initial Source:
# Measurements from Schnitzler 2007
inner_gap_inner_radius = 29.5275

# ENDF/B-VIII.0 broad group library (56 energy groups):
energy_bins = [20000000, 6434000, 4304000, 3000000, 1850000, 1500000, 1200000, 861100, 750000,
                600000, 470000, 330000, 270000, 200000, 50000, 20000, 17000,
                3740, 2250, 191.5, 187.7, 117.5, 116, 105, 101.2,
                67.5, 65, 37.13, 36, 21.75, 21.2, 20.5, 7, 6.875,
                6.5, 6.25, 5, 1.13, 1.08, 1.01, 0.625, 0.45,
                0.375, 0.35, 0.325, 0.25, 0.2, 0.15, 0.1, 0.08,
                0.06, 0.05, 0.04, 0.0253, 0.01, 0.004]

energy_bins.reverse()

# Set up Filters and triggers
low_u_fuel_filter = openmc.DistribcellFilter(7)
intermediate_u_fuel_filter = openmc.DistribcellFilter(11)
high_u_fuel_filter = openmc.DistribcellFilter(3)
energy_filter = openmc.EnergyFilter(energy_bins)
n_filter = openmc.ParticleFilter('neutron')

radial_mesh = openmc.CylindricalMesh(r_grid=[0,inner_gap_inner_radius,10],
                                     z_grid=[-core_height/2, core_height/2],
                                     phi_grid=[0,2*np.pi])
radial_mesh_filter =openmc.MeshFilter(radial_mesh)

axial_mesh = openmc.CylindricalMesh(r_grid=[0,inner_gap_inner_radius],
                                    z_grid=np.linspace(-core_height/2,core_height/2, 12),
                                    phi_grid=[0,2*np.pi])
axial_mesh_filter = openmc.MeshFilter(axial_mesh)

flux_trigger = openmc.Trigger(trigger_type='rel_err', threshold=0.05)
heating_trigger = openmc.Trigger(trigger_type='rel_err', threshold=0.05)

# Set up tallies for flux and kappa-fission
heating_tally_low_u = openmc.Tally(name='low u Heating')
heating_tally_low_u.filters = [low_u_fuel_filter]
heating_tally_low_u.scores = ['kappa-fission']
heating_tally_low_u.triggers = [heating_trigger]

heating_tally_inter_u = openmc.Tally(name='inter u Heating')
heating_tally_inter_u.filters = [intermediate_u_fuel_filter]
heating_tally_inter_u.scores = ['kappa-fission']
heating_tally_inter_u.triggers = [heating_trigger]

heating_tally_high_u = openmc.Tally(name='high u Heating')
heating_tally_high_u.filters = [high_u_fuel_filter]
heating_tally_high_u.scores = ['kappa-fission']
heating_tally_high_u.triggers = [heating_trigger]

axial_flux_tally = openmc.Tally(name='Axial Flux Tally')
axial_flux_tally.filters = [axial_mesh_filter, energy_filter, n_filter]
axial_flux_tally.scores = ['flux']

radial_flux_tally = openmc.Tally(name='Radial Flux Tally')
radial_flux_tally.filters = [axial_mesh_filter, energy_filter, n_filter]
radial_flux_tally.scores = ['flux']

model.tallies = [heating_tally_low_u, heating_tally_inter_u, heating_tally_high_u, radial_flux_tally, axial_flux_tally]

model.export_to_model_xml()

# %%



