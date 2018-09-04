import math

ptimport = False
try:
    from prettytable import PrettyTable
    ptimport = True
except ImportError:
    pass

# Radar pseudocode:
# Keywords:
# within: "the distance between DET and TAR is less than"

# Abbreviations:
# DET: detector craft
# TAR: target craft
# AR: active radar
# PGW: PlanetGravityWell
# M: Mass
# G: Earth Standard Gravity, 9.81 m/s^2

# Constants:
# MVR:   MaxVisibilityRange = 200000
# GDR:   GuaranteedDetectionRange = 1000
# DSC:   DecoyStealthCoefficient = 1.05

# Variables:
# MR:    MarkerRange; maximum operating beacon/antenna range
# TRP:   TotalRadarPower; sum([ERP for radar if radar is AC])
# ERP:   EffectiveRadarPower
# ADR:   ActiveDetectionRate = VDBDR/DSC^DC
# VDBDR: VisibilityDistanceByDefaultRule = WVR*300
# DC:    DecoysCount; number of active decoys
# RO:    ReactorOutput; sum of all reactor power output in MW
# WV:    WorldVolume; volume of a sphere that circumscribes an entity
# WVR:   WorldVolumeRadius; radius of the RV
# GD:    GravityDistortion = MD + AGD
# MD:    MassDistortion = (3.75229E-6)*M^(3/2)
# AGD:   ArtificialGravityDistortion = (500/G)*sum([abs(GA) for grav gens])
# GA:    GravityAcceleration; acceleration of a gravity generator in m/s^2

# want all entities that are "nearby" and are grids
# entity list = [TAR for TAR in entities if (within DET MVR)
#                                            and (TAR is a grid)]
# For TAR in entity list:
#     If (within GDR)
#         or (TAR in line of sight
#           and ( (TAR is broadcasting and within (TAR MR))
#                or ( DET AR is on and within (DET TRP)*(TAR ADR)/40000 )
#                or ( TAR has physics and within (TAR TRP)/1.5 )
#                or ( TAR has physics and within (TAR RO)*200 )
#                or ( TAR has physics
#                     and TAR is not static
#                     and not in PGW
#                     and not [[TAR WV within close asteroid WVR*3]]
#                     and within (TAR GD) )
#                )
#          ):
#     Make a MyDetectedEntityInfo object
#     Try to add the info object to the DetectedEntity list
#     Determine if adding a marker is necessary. It is NOT necessary if:
#         The Info object could not be added to the DetectedEntity list
#         DET radar isn't functional
#         DET radar not set to display markers
#         DET radar does not have owner in relay
#         TAR has a RadarableGrid component, TAR is not a working grid,
#             and DET is set to show working grids only
#         TAR has a RadarableGrid component, TAR has functional beacons/antennae,
#               and DET is within the MarkerRange of those beacons/antennae
#         TAR is friendly and DET radar is set to display only hostiles
#         TAR is floating and DET radar not set to display floating grids
#         There is not already a marker in the DET radar's list
#     Create marker if necessary

TERMINAL_TABWIDTH = 8 # number of spaces equal to a full tab

# G = 9.81 # Standard Gravity (m/s^2)
PR = 120000 # PlanetRadius (m)
MR = 19000 # MoonRadius (m)
SRP = 15000 # SmallReactorPower (kW)
LRP = 300000 # LargeReactorPower (kW)
MVR = 200000 # MaxVisibilityRange (m)
GDR = 1000 # GuaranteedDetectionRange (m)
DSC = 1.05 # DecoyStealthCoefficient
MP = 50000 # Radar MaxPower (kW)

class Grid:
    def __init__(self, blocks={}, mass=0, boundingradius=0,
                 artificialgravity=0, hasphysics=True, isstatic=False):
        blocks = {'radar-active':0,
                  'large-reactor':0,
                  'small-reactor':0,
                  'decoy':0, **blocks}

        self.blocks = blocks
        self.M = mass # (kg)
        self.boundingradius = boundingradius # (m)
        self.hasphysics = hasphysics
        self.isstatic = isstatic
        
        # to determine the artificial gravity for a ship:
        # for each grav generator:
        #     artificial gravity += abs(gravity generated in G's)
        self.artificialgravity = artificialgravity # (G's)
        
    def TRP(self):
        return self.blocks['radar-active']*MP
    def ADR(self):
        return self.VDBDR()/pow(DSC, self.DC())
    def VDBDR(self):
        return self.WVR()*300
    def DC(self):
        return self.blocks['decoy']
    def RO(self):
        return (self.blocks['large-reactor']*LRP
                + self.blocks['small-reactor']*SRP)
    def WV(self):
        return math.pi*(4/3)*pow(self.boundingradius,3)
    def WVR(self):
        return self.boundingradius
    def GD(self):
        return self.MD() + self.AGD()
    def MD(self):
        return (3.75229E-6)*pow(self.M,3/2)
    def AGD(self):
        return (500)*self.artificialgravity

    def detect(det, tar):
        # Guaranteed/"Turret" Detection
        gdrrange = GDR
        # Active Radar
        arrange = min(MVR, det.TRP()*tar.ADR()/40000)
        # Passive Radar
        prrange = min(MVR, tar.TRP()/1.5 if tar.hasphysics else 0)
        # Heat/Radiation
        heatrange = min(MVR, tar.RO()*.2 if tar.hasphysics else 0)
        # Gravimetric
        isgravable = tar.hasphysics and (not tar.isstatic) 
        gravrange = min(MVR, tar.GD() if isgravable else 0)
        return (gdrrange, arrange, prrange, heatrange, gravrange)
        
class Ship(Grid):
    def Tugboat():
        s = Ship()
        s.blocks['small-reactor'] = 1
        s.M = 100E3 # kg
        s.boundingradius = 2.5*5 # m
        return s
    def MiningShip():
        s = Ship()
        s.blocks['small-reactor'] = 2
        s.M = 250E3 # kg
        s.boundingradius = 2.5*10 # m
        return s
    def StealthShip():
        s = Ship()
        s.blocks['decoy'] = 10
        s.M = 700E3 # kg
        s.boundingradius = 2.5*15
        return s
    def DetectorShip():
        s = Ship()
        s.blocks['radar-active'] = 10
        s.blocks['large-reactor'] = 2
        s.M = 2000E3 # kg
        s.boundingradius = 2.5*18 # m
        return s
    def BattleShip():
        s = Ship()
        s.blocks['large-reactor'] = 2
        s.M = 10000E3 # kg
        s.boundingradius = 2.5*40 # m
        return s
    def MotherShip():
        s = Ship()
        s.blocks['large-reactor'] = 8
        s.M = 20000E3 # kg
        s.boundingradius = 2.5*55 # m
        return s

class Station(Grid):
    def OreProcessingFacility():
        s = Station()
        s.blocks['large-reactor'] = 4
        s.M = 25000E3 # kg
        s.boundingradius = 2.5*45 # m
        return s
    def Shipyard():
        s = Station()
        s.blocks['large-reactor'] = 1
        s.M = 35000E3 # kg
        s.boundingradius = 2.5*80 # m
        return s
    def MiningOutpost():
        s = Station()
        s.blocks['small-reactor'] = 4
        s.M = 3000E3 # kg
        s.boundingradius = 2.5*40 # m
        return s

def main():
    n_tab = TERMINAL_TABWIDTH
    det = Ship.DetectorShip()
    targets = [Ship.Tugboat(), Ship.MiningShip(), Ship.StealthShip(),
               Ship.DetectorShip(), Ship.BattleShip(), Ship.MotherShip(),
               Station.OreProcessingFacility(), Station.Shipyard(),
               Station.MiningOutpost()]
    names = ['Tugboat', 'Mining Ship', 'Stealth Ship', 'Detector Ship',
             'Battleship', 'Mothership', 'Ore Facility',
             'Shipyard', 'Mining Outpost']
    firstrow = ['Target', 'Turret', 'Active', 'Passive', 'Heat', 'Gravity']
    if ptimport:
        pt = PrettyTable(firstrow)
    else:
        for i in range(1,6):
            firstrow[i] = ((13 - len(firstrow[i]))//2)*' ' + firstrow[i]
        pt = [firstrow, None]


    for i, tar in enumerate(targets):
        detectresult = Grid.detect(det, tar)
        (gdrrange, arrange, prrange, heatrange, gravrange) = detectresult

        reverseresult = Grid.detect(tar, det)
        (gdrrev, arrev, prrev, heatrev, gravrev) = reverseresult


        row = []
        for j in range(5):
            range_ = str(int(round(detectresult[j],-2))/1000)
            range_ = (5-len(range_))*' ' + range_
            hostilerange = str(int(round(reverseresult[j],-2))/1000)
            hostilerange = hostilerange + (5-len(hostilerange))*' '

            row.append(range_ + ' / ' + hostilerange)

        row = [names[i] ] + row
        
        if ptimport:
            pt.add_row(row)
        else:
            pt.append(row)
    print('Radar Detection Range (km)')
    print('Active Radars: ' + str(det.blocks['radar-active']))
    print('Reactors Running: ' + str(det.blocks['large-reactor']))
    if ptimport:
        print(pt)
    else:
        for row in pt:
            if not row:
                print((12*n_tab-3)*'-')
                continue
            str_ = ''
            for col in row:
                str_ += str(col) + (2 - len(col) // n_tab) * '\t'
            print(str_)

if __name__=='__main__':
    main()

