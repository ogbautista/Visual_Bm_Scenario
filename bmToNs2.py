'''
* Copyright (c) 2019 - 2020 Oscar Bautista
*
* This program is free software; you can redistribute it and/or modify it
* under the terms of the GNU General Public License version 2 as published
* by the Free Software Foundation.
*
* DESCRIPTION:
* Converts a BonnMotion 2D or 3D scenario to NS2 mobility format.
* Written as an alternative to BM 3.0.1 conversion tool which has some bugs when converting 3D scenarios.
*
* AUTHOR: Oscar Bautista <obaut004@fiu.edu>
'''

import sys, math

# Function to calculate distance between two coordinates
def calculate_distance (origin, destination):
    sum = 0
    for i in range(len (origin)):
        sum += (destination[i] - origin[i])**2
    return math.sqrt(sum)

# Verify that the source filename is given, if not, then the BonnMotion scenario name is requested
if len(sys.argv) >= 2:
    bmScenario = sys.argv[1]
else:
    bmScenario = input ("BonnMotion Scenario: ")

if len(bmScenario) == 0:
    sys.exit("no filename was given, exiting now...\n")

if "." in bmScenario:
    bmFilename = bmScenario
else:
    bmFilename = bmScenario + ".movements"
ns2Filename = bmScenario.split(".")[0] + ".ns_movements"

# Open BonnMotion Scenario for conversion and creates output ns2 mobility file
try:
    with open (bmFilename, 'r') as bmFile, open (ns2Filename, 'w') as ns2file:
        wpSize = 3
        scn3D = False
        bmLine = bmFile.readline()
        if bmLine.strip() == "#3D":
            scn3D = True
            wpSize = 4
            bmLine = bmFile.readline()
        n = -1
        n_ns2 = 0
        while (bmLine):
            if bmLine.strip().startswith('#'):
                bmLine=bmFile.readline()
                continue
            n += 1
            tokens = bmLine.split()
            if (len(tokens) % (wpSize)) != 0:
                print ("error at node {}: line does not contain correct number of values ({})...node skipped".format(n, len(tokens)) )
                bmLine = bmFile.readline()
                continue
            # create times and locations vectors for the current node
            times = []
            locations = []
            for i in range(0, len(tokens), wpSize):
                try:
                    times.append(float (tokens[i]) )
                    location= []
                    for d in range (1, wpSize):
                        location.append(float (tokens[i+d]) )
                    locations.append(location)
                except ValueError:
                    print ("error at node {}: invalid number:{}...waypoint skipped".format(n, str(sys.exc_info()[1]).split(':')[-1] ) )
                    if len (times) > len (locations):
                        times = times[:-1]
                    bmLine = bmFile.readline()
                    continue
            # process and generate ns2 mobility for the current node
            location = locations[0]
            ns2file.write("$node_({}) set X_ {}\n".format(n_ns2, location[0]))
            ns2file.write("$node_({}) set Y_ {}\n".format(n_ns2, location[1]))
            if scn3D:
                ns2file.write("$node_({}) set Z_ {}\n".format(n_ns2, location[2]))
            for i in range (len (times) - 1):
                time = times[i+1] - times[i]
                origin = locations[i]
                destination = locations[i+1]
                if time == 0:
                    print("warning at node {}: two waypoints with same time".format(n))
                    if destination[0] != origin[0]:
                        ns2file.write("$ns_ at {} \"$node_({}) set X_ {}\"\n".format(times[i], n_ns2, destination[0]))
                    if destination[1] != origin[1]:
                        ns2file.write("$ns_ at {} \"$node_({}) set Y_ {}\"\n".format(times[i], n_ns2, destination[1]))
                    if scn3D and (destination[2] != origin[2]):
                        ns2file.write("$ns_ at {} \"$node_({}) set Z_ {}\"\n".format(times[i], n_ns2, destination[2]))
                    continue
                elif time < 0:
                    print("warning at node {}: trying to insert a waypoint with a past timestamp...".format(n))
                    print("...the resulting ns2mobility could experience an unexpected pattern")
                    continue
                speed = calculate_distance(origin, destination)/time
                if scn3D:
                    outputLine = "$ns_ at {} \"$node_({}) setdest {} {} {} {}\"\n".format(times[i], n_ns2, destination[0], destination[1], destination[2], speed)
                else:
                    outputLine = "$ns_ at {} \"$node_({}) setdest {} {} {}\"\n".format(times[i], n_ns2, destination[0], destination[1], speed)
                if origin == destination:
                    outputLine = "# " + outputLine
                ns2file.write (outputLine)
            n_ns2 += 1
            bmLine = bmFile.readline()
    print("\nBonnMotion to Ns2mobility conversion completed:")
    print("\t{} scenario".format("3D" if scn3D else "2D"))
    print("\t{} out of {} nodes' mobility converted".format(n_ns2, n+1))
    print("\n{} created successfully\n".format(ns2Filename))
except FileNotFoundError:
    sys.exit(str(sys.exc_info()[1])+'\n')
except:
    print ("error while processing {}: {}, {}".format(bmFilename, sys.exc_info()[0], sys.exc_info()[1]), '\n')
