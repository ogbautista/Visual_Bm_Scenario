'''
* Copyright (c) 2019 - 2020 Oscar Bautista
*
* This program is free software; you can redistribute it and/or modify it
* under the terms of the GNU General Public License version 2 as published
* by the Free Software Foundation.
*
* DESCRIPTION:
* Takes one scenario referred to as 'child' and adds mobility information of a 'parent' scenario
* along with and optional offset.
*
* AUTHOR: Oscar Bautista <obaut004@fiu.edu>
'''

import sys
from my_utils import fRead
from my_utils.nodeCourse import NodeCourse


if len(sys.argv) < 3:
    print ("\nUsage:\n python3 addScenarios.py <childScenario> [-p <parentScenario>] [-r] [xoff=...] [yoff=...] [zoff=...]\n")
    print (" <childScenario>\tThe base scenario to be modified.")
    print (" -p <parentScenario>\tParent mobility scenario whose first node the child scenario will follow.")
    print (''' -r\t\t\tCoordinates in child scenario are considered relative to parent coordinates.
            \t\t(By default initial position of child scenario is maintained in the mixed scenario)''')
    print (" xoff\t\t\tCustom X offset to be added to child scenario.")
    print (" yoff\t\t\tCustom Y offset to be added to child scenario.")
    print (" zoff\t\t\tCustom Z offset to be added to child scenario.\n")
    sys.exit(1)

op = None   # Used to track -p option when iterating through arguments
rel = False # Relative coordinates
parentScn = None
xOff = 0
yOff = 0
zOff = 0
scn3D = False
# Processing of arguments and options
childScn = sys.argv[1]
for arg in sys.argv[2:]:
    if arg.startswith('-'):
        arg = arg.lstrip('-')
        if op == 'p':
            print("Scenario name expected after '-p' option")
            op = None
        elif arg == 'p':
            op = arg
        elif arg == 'r':
            rel = True
        else:
            print("Unknown option '-{}' ignored".format(arg))
    elif op == 'p':
        parentScn = arg
        op = None
    else:
        argpair = arg.split('=')
        if len(argpair) == 2 and argpair[0] in ["xoff", "yoff", "zoff"]:
            try:
                if argpair[0] == "xoff":
                    xOff = float(argpair[1])
                if argpair[0] == "yoff":
                    yOff = float(argpair[1])
                if argpair[0] == "zoff":
                    zOff = float(argpair[1])
            except ValueError as e:
                print (e, "...ignored")
        else:
            print("Unknown argument '{}' ignored".format(argpair[0]))
# Validation of options
if op == 'p':
    print ("Warning: '-p' option was specified but no parent scenario name was given")
if rel == True:
    if parentScn is None:
        print ("Warning: '-r' option was specified but parent scenario was not given")
    else:
        print("Child scenario coordinates relative to parent node.")
# Read information from scenario files
childtimes, childlocations = fRead.read_bmScenario(childScn + ".movements")
mx_offset = [xOff, yOff, zOff]
if mx_offset[2] != 0:
    scn3D = True
if parentScn is not None:
    parenttimes, parentlocations = fRead.read_bmScenario(parentScn + ".movements")
    if not rel:
        mx_offset[0] -= parentlocations[0][0][0]
        mx_offset[1] -= parentlocations[0][0][1]
        if len(parentlocations[0][0]) == 3:
            mx_offset[2] -= parentlocations[0][0][2]
            scn3D = True
    # Only the first node in the parent scenario (if it contains more than 1 node) is considered
    parent = NodeCourse (parenttimes[0], parentlocations[0])
else:
    parent = NodeCourse ([0], [[0, 0]])
if len(childlocations[0][0]) == 3:
    scn3D = True
# For each node in the child scenario the positions at each new waypoint are calculated
newchildtimes = []
newchildlocations =[]
for n in range(len(childtimes)):
    child = NodeCourse (childtimes[n], childlocations[n])
    mx_times = sorted (set (child.get_wptimes() + parent.get_wptimes()))
    mx_locations = []
    for t in mx_times:
        childlocation = child.get_location(t)
        parentlocation = parent.get_location(t)
        # This is a compensation when 2D and 3D scenarios are added
        if (len(childlocation) == 2) and scn3D:
            childlocation.append(0)
        if (len(parentlocation) == 2) and scn3D:
            parentlocation.append(0)
        newlocation = []
        for d in range (len(childlocation)):
            newlocation.append(childlocation[d] + parentlocation[d] + mx_offset[d])
        mx_locations.append(newlocation)
    newchildtimes.append(mx_times)
    newchildlocations.append(mx_locations)
print ("child scenario update completed")
try:
    with open(childScn + "_mx.movements", 'w') as newScenarioFile:
        if scn3D:
            newScenarioFile.write("#3D\n")
        for nodetimes, nodelocations in zip (newchildtimes, newchildlocations):
            line = ""
            for time, location in zip (nodetimes, nodelocations):
                line += f"{time} {location[0]} {location[1]} "
                if scn3D:
                    line += f"{location[2]} "
            line = line.strip()+'\n'
            newScenarioFile.write(line)
    print ("Successfully created {}\n".format(childScn + "_mx.movements"))
except:
    print("Error while writing to file {}: {}, {}".format(childScn + "_mx.movements", sys.exc_info()[0], sys.exc_info()[1]))
