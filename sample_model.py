import core_template
import openmc

model = core_template.get_model(89,90)

model.settings.batches = 30
model.settings.particles = 100000
model.settings.inactive = 10
model.settings.temperature = {'default':2500}

#set up a distribcell filter over fuel elements
#there are 2 cells that have fuel

propellent_fuel_cell_filter = openmc.DistribcellFilter(3)

# this one actually crashes openmc idk why
#edge_fuel_cell_filter = openmc.DistribcellFilter(4)

edge_fuel_cell_filter = openmc.CellFilter(4)

# do a heating tally, gotta do 2 to get the plotter to work
heating_tally3 = openmc.Tally(name='Heating3')
heating_tally3.filters = [propellent_fuel_cell_filter]
heating_tally3.scores = ['kappa-fission']

# I think this one scores the sum of the heating of every instance of this cell
heating_tally4 = openmc.Tally(name='Heating4')
heating_tally4.filters = [edge_fuel_cell_filter]
heating_tally4.scores = ['kappa-fission']

model.tallies = [heating_tally3, heating_tally4]

model.export_to_model_xml()

statepoint = model.run()