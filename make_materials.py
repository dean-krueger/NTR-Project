from pyne.material import Material, MultiMaterial
from pyne.material_library import MaterialLibrary


# sorry this uses pyne but it makes it so much easier
# u can pull this docker image for a working version
# docker pull ejpflug/openmc_chtc:08
# I will also write out a materials.xml and push that to github

# these materials are perfectly pure, so not 100% realistic

# NERVA GRAPHITE FUEL SCHNITZLER 2012 p4
# TAUB 1975 Review of fuel element development for nuclear rocket engines
# in table 6 of the taub paper many possible fuel compositions are listed

def carbon():
    nucvec = {60000000: 1}
    C = Material(nucvec)
    C.density = 2.1  # g/cm3, from taub, slightly lower than crystalline
    C = C.expand_elements()
    C.metadata['mat_number'] = 1
    return C


def zirconium():
    nucvec = {400000: 1}
    Zr = Material(nucvec)
    Zr = Zr.expand_elements()
    Zr.density = 6.49  # g/cm3
    Zr.metadata['mat_number'] = 2
    return (Zr)


def hydrogen_STP():
    nucvec = {10000: 1}
    H = Material(nucvec)
    H = H.expand_elements()
    H.density = 8.988e-5
    H.metadata['mat_number'] = 9
    return H


def uranium(enrichment):
    U = Material({'U238': 1-enrichment, 'U235': enrichment})  # mass enrichment
    U.density = 19.1  # g/cm3
    U.metadata['mat_number'] = 3
    return U

def beryllium():
    nucvec = {40000: 1}
    Be = Material(nucvec)
    Be = Be.expand_elements()
    Be.density = 1.85 #g/cm3
    Be.metadata['mat_number'] = 11
    return Be

def copper():
    nucvec = {290000: 1}
    Cu = Material(nucvec)
    Cu = Cu.expand_elements()
    Cu.density = 8.96 #g/cm3
    Cu.metadata['mat_number'] = 12
    return Cu

def boron():
    nucvec = {50000: 1}
    B = Material(nucvec)
    B = B.expand_elements()
    B.density = 2.3 #g/cm3
    B.metadata['mat_number'] = 13
    return B

def copper_boron(Cu, B, C):
    
    # ref https://www.osti.gov/servlets/purl/1067489
    B4C = Material()
    B4C.from_atom_frac({B:4,C:1})
    B4C.density = 2.5 #g/cm3

    mix = MultiMaterial({Cu:0.5, B4C:0.5})

    CuB = mix.mix_by_volume()
    CuB.metadata['mat_number'] = 14

    return CuB


def uranium_carbide(U, C):
    UC = Material()
    UC.from_atom_frac({U: 1, C: 1})
    UC.density = 13.60  # g/cm3 from taub
    UC.metadata['mat_number'] = 4
    return UC


def zirconium_carbide(Zr, C):
    ZrC = Material()
    ZrC.from_atom_frac({Zr: 1, C: 1})
    ZrC.density = 6.59  # g/cm3 from taub
    ZrC.metadata['mat_number'] = 5
    return ZrC


def zirconium_hydride_II():

    Zr = zirconium()
    H = hydrogen_STP()

    ZrH2 = Material()
    ZrH2.from_atom_frac({Zr: 1, H: 2})
    ZrH2.density = 5.60  # g/cm3
    ZrH2.metadata['mat_number'] = 7

    return ZrH2


def inconel_718():
    #composition from wikipedia, impurities omitted, balance Fe
    nucvec = {280000: 52.5, 240000: 19, 420000: 3,
              410000: 2.5, 730000: 2.5, 130000: 0.6, 220000: 0.9, 260000: 19}
    inconel = Material(nucvec)
    inconel = inconel.expand_elements()
    inconel.density = 8.22 #g/cm3
    inconel.metadata['mat_number'] = 8
    return inconel

def zirconium_carbide_insulator(ZrC):
    mix = MultiMaterial({ZrC:1})
    insulator = mix.mix_by_volume()
    insulator.density = ZrC.density/2
    insulator.metadata['mat_number'] = 10
    return insulator

def SS316LN_mat():
    nucvec = {50000000:0.030, 
              60000000:0.030, 
              70000000:0.160, 
              140000000:1.0, 
              150000000:0.030, 
              160000000:0.020, 
              240000000:17.250, 
              250000000:2.00 , 
              260000000:64.830, 
              270000000:0.100, 
              280000000:12.00, 
              410000000:0.050, 
              420000000:2.5}
    
    SS316LN = Material(nucvec)
    SS316LN.density = 7.93
    SS316LN=SS316LN.expand_elements()
    SS316LN.metadata['citation']='GilbertHandbookITERCCFE_2016'
    SS316LN.metadata['mat_number'] = 15
    return SS316LN

def mix_UZrC_graphite(ZrC_wo, UC_wo, C_wo, void_percent, mat_number,
                      U_enrichment=0.93):
    """
    UC_wo: weight percent UC
    ZrC_wo: weight percent ZrC
    C_wo: free carbon (graphite) weight percent
    void_percent: desired void percent
    U_enrichment: percent U235, 0.93 default from taub

    returns: material object, mix the materials by weight, then scale density
    to get void fraction
    """
    Zr = zirconium()
    U = uranium(U_enrichment)
    C = carbon()

    ZrC = zirconium_carbide(Zr, C)
    UC = uranium_carbide(U, C)

    mix = MultiMaterial({ZrC: ZrC_wo, UC: UC_wo, C: C_wo})
    UZrC_graphite = mix.mix_by_mass()

    UZrC_graphite.density = UZrC_graphite.density*(1-void_percent)
    UZrC_graphite.metadata['mat_number'] = mat_number

    return UZrC_graphite


def main():

    # get the material objects
    C = carbon()
    Zr = zirconium()
    U = uranium(0.93)
    Be = beryllium()
    Cu = copper()
    B = boron()
    ZrC = zirconium_carbide(Zr, C)
    UC = uranium_carbide(U, C)
    UZrC70_15 = mix_UZrC_graphite(38.4, 2.8, 58.5, 0.117,6)
    #the numbers in the table add up to more than 100% for this one
    #so i reduced the free carbon percentage because that makes sense
    UZrC70_20 = mix_UZrC_graphite(46.1, 2.7, 51.2, 0.114, 16) 
    UZrC70_30 = mix_UZrC_graphite(59.7, 2.4, 37.7, 0.113, 17)
    UZrC435_30 = mix_UZrC_graphite(52.7, 13.1, 33.7, 0.155, 18)
    UZrC435_35 = mix_UZrC_graphite(57.7, 12.6, 29.2, 0.150, 19)
    UZrC435_40 = mix_UZrC_graphite(63.4, 11.8, 24.7, 0.135, 20)
    UZrC435_45 = mix_UZrC_graphite(67.6, 11.2, 20.8, 0.140, 21)
    ZrH2 = zirconium_hydride_II()
    Inc_718 = inconel_718()
    H_STP = hydrogen_STP()
    ZrC_insulator = zirconium_carbide_insulator(ZrC)
    CuB = copper_boron(Cu, B, C)
    ss316l = SS316LN_mat()

    # print em out and have a look
    print(C)
    print(Zr)
    print(U)
    print(ZrC)
    print(UC)
    print(UZrC70_15)
    print(ZrH2)
    print(Inc_718)
    print(H_STP)

    # make the library and export to xml
    lib = MaterialLibrary()
    lib['graphite_carbon'] = C
    lib['Zirconium'] = Zr
    lib['zirconium_carbide'] = ZrC
    lib['Uranium_cabide_0.93'] = UC
    # these numbers correspond to headers in taub table 6
    lib['graphite_fuel_70U_15C'] = UZrC70_15
    lib['graphite_fuel_70U_20C'] = UZrC70_20
    lib['graphite_fuel_70U_30C'] = UZrC70_30
    lib['graphite_fuel_435U_30C'] = UZrC435_30
    lib['graphite_fuel_435U_35C'] = UZrC435_35
    lib['graphite_fuel_435U_40C'] = UZrC435_40
    lib['graphite_fuel_435U_45C'] = UZrC435_45
    lib['graphite_fuel_']
    lib['zirconium_hydride_II'] = ZrH2
    lib['inconel-718'] = Inc_718
    lib['Hydrogen STP'] = H_STP
    lib['zirconium_carbide_insulator'] = ZrC_insulator
    lib['Beryllium'] = Be
    lib['copper_boron'] = CuB
    lib['SS316L'] = ss316l
    lib.write_openmc('materials.xml')


if __name__ == '__main__':
    main()
