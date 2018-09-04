# Updated 09/04/2018
# omnisciendus@gmail.com
# Cheetah's Radar Mod:
# https://steamcommunity.com/sharedfiles/filedetails/?id=907384096


import math

ptimport = False
try:
    from prettytable import PrettyTable
    ptimport = True
except ImportError:
    pass

TERMINAL_TABWIDTH = 8 # number of spaces equal to a full tab
DETECTOR_RADARS = 1 # number of active radars on a detector ship

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
        s.blocks['radar-active'] = DETECTOR_RADARS
        s.blocks['large-reactor'] = s.blocks['radar-active']/6
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
    firstrow = ['Target', 'Turret', 'Active', 'Passive', 'Heat', 'Gravity',
                'Net Range', 'Mass (T)', 'Length (m)', 'Blocks']
    if ptimport:
        pt = PrettyTable(firstrow)
    else:
        for i in range(1,7):
            firstrow[i] = ((13 - len(firstrow[i]))//2)*' ' + firstrow[i]
        pt = [firstrow, None]


    for i, tar in enumerate(targets):
        detectresult = Grid.detect(det, tar)
        (gdrrange, arrange, prrange, heatrange, gravrange) = detectresult
        detectresult = detectresult + (max(detectresult),)
        
        reverseresult = Grid.detect(tar, det)
        (gdrrev, arrev, prrev, heatrev, gravrev) = reverseresult
        reverseresult = reverseresult + (max(reverseresult),)


        row = []
        for j in range(len(detectresult)):
            range_ = str(int(round(detectresult[j],-2))/1000)
            range_ = (5-len(range_))*' ' + range_
            hostilerange = str(int(round(reverseresult[j],-2))/1000)
            hostilerange = hostilerange + (5-len(hostilerange))*' '

            row.append(range_ + ' / ' + hostilerange)

        row = [names[i]] + row

        row += [str(int(tar.M/1000)), str(int(tar.boundingradius*2))]

        
        tar_blocks = [str(round(v,2)) + ' ' + k.replace('-',' ')
                      for k,v in tar.blocks.items() if v > 0]

        tar_blocks = ', '.join(tar_blocks)

        row += [tar_blocks]
        
        if ptimport:
            pt.add_row(row)
        else:
            pt.append(row)
    print('Radar Detection Range')
    print('Max Range to Target / Max Hostile Detection Range')
    print('Active Radars: ' + str(det.blocks['radar-active']))

    print('Large Reactors Running: '
          + str(round(det.blocks['large-reactor'],4)))
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

