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
    print ("  <childScenario>\tThe base scenario to be modified.")
    print ("  -p <parentScenario>\tParent mobility scenario whose first node the child scenario will follow.")
    print ('''  -r\t\t\tCoordinates in child scenario are considered relative to parent coordinates.
            \t\t (By default initial position of child scenario is maintained in the joint scenario)\n''')
    print (" Some transforms can be pre-applied to child scenario or even without being added to a parent scenario:")
    print ("  xoff\t\t\tCustom X offset to be added to child scenario.")
    print ("  yoff\t\t\tCustom Y offset to be added to child scenario.")
    print ("  zoff\t\t\tCustom Z offset to be added to child scenario.")
    print (" These options override zoff option (if both are given):")
    print ("  zmin\t\t\tScales the child scenario to have the specified minimim Z value.")
    print ("  zmax\t\t\tScales the child scenario to have the specified maximum Z value.\n")
    sys.exit(1)

op = None   # Used to track -p option when iterating through arguments
rel = False # Relative coordinates
parentScn = None
xOff = 0
yOff = 0
zOff = 0
zMin = None
zMax = None
scn3D = False
scaling = False
# Processing of arguments and options
childScn = sys.argv[1]
for arg in sys.argv[2:]:
    if arg.startswith('-'):
        arg = arg.lstrip('-')
        if op == 'p':
            print("scenario name expected after '-p' option")
            op = None
        elif arg == 'p':
            op = arg
        elif arg == 'r':
            rel = True
        else:
            print("unknown option '-{}' ignored".format(arg))
    elif op == 'p':
        parentScn = arg
        op = None
    else:
        argpair = arg.split('=')
        if len(argpair) == 2 and argpair[0] in ["xoff", "yoff", "zoff", "zmin", "zmax"]:
            try:
                if argpair[0] == "xoff":
                    xOff = float(argpair[1])
                if argpair[0] == "yoff":
                    yOff = float(argpair[1])
                if argpair[0] == "zoff":
                    zOff = float(argpair[1])
                if argpair[0] == "zmin":
                    zMin = float(argpair[1])
                if argpair[0] == "zmax":
                    zMax = float(argpair[1])
            except ValueError as e:
                print (e, "...ignored")
        else:
            print("unknown argument '{}' ignored".format(argpair[0]))
if zMin is not None or zMax is not None:
    scaling = True
# Validation of options
if op == 'p':
    print ("warning: '-p' option was specified but no parent scenario name was given")
if rel == True:
    if parentScn is None:
        print ("warning: '-r' option was specified but parent scenario was not given")
    else:
        print("child scenario coordinates relative to parent node.")
if zOff!=0 and scaling:
    print("Z-Offset overridden by Z-Min and/or Z-Max scaling values.")

# Read information from scenario files
# A joint scenario is considered 3D when the child scenario is 3D or the parent scenario is 3D or an zOffset is given
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

# If scaling is to be performed, we need to first find the Z-Min and Z-Max values in child scenario:
if scaling:
    if len (childlocations[0][0]) < 3:
        print("child scenario is 2-dimensional, Z-scaling is not applicable")
        scaling = False
    else:
        child_zMin = None
        child_zMax = None
        for node in childlocations:
            for location in node:
                if child_zMin is None:
                    child_zMin = location[2]
                    child_zMax = child_zMin
                else:
                    if location[2] < child_zMin:
                        child_zMin = location[2]
                    if location[2] > child_zMax:
                        child_zMax = location[2]
        if child_zMin == child_zMax:
            print("child scenario contained in plane Z=" + str(child_zMin) + ", Z-scaling is not applicable")
            scaling = False
        else:
            # we calculate the scaling values s_a and s_b in: z2 = s_a*z1 + s_b
            if zMax is None:
                zMax = child_zMax
            if zMin is None:
                zMin = child_zMin
            s_a = (zMax - zMin)/(child_zMax-child_zMin)
            s_b = zMin - s_a * child_zMin
            print("child scenario's Z-Min was:",child_zMin)
            print("child scenario's Z-Max was:",child_zMax)
            # we make sure that if Z-Offset exist, it is overridden
            if len(mx_offset) == 3:
                mx_offset[2] = 0

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
        for d in range (len(childlocation)): # For each dimension X, Y and (if applicable) Z
            if scaling and d == 2:
                newlocation.append(childlocation[d]*s_a + parentlocation[d] + s_b + mx_offset[d])
            else:
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
    print ("successfully created {}\n".format(childScn + "_mx.movements"))
except:
    print("error while writing to file {}: {}, {}".format(childScn + "_mx.movements", sys.exc_info()[0], sys.exc_info()[1]))
