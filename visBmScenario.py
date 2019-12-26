'''
* Copyright (c) 2019 - 2020 Oscar Bautista
*
* This program is free software; you can redistribute it and/or modify it
* under the terms of the GNU General Public License version 2 as published
* by the Free Software Foundation.
*
* DESCRIPTION:
* Generates an matplotlib animation of the nodes in a mobility scenario created using BonnMotion
*
* AUTHOR: Oscar Bautista <obaut004@fiu.edu>
'''
import math, sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from my_utils import fRead
from my_utils.netSimUtils import getPlotMargins, calculateFigDimensions, calculateZlim

'GLOBAL VARIABLES'
g_interval = 0.5
g_currentFT = 0.0
g_scnName = None
g_scn3D = None
g_drawLabel = False

'DEFINITION OF FUNCTIONS'
# Calculates the velocity vector of a node given an initial and final locations and corresponding times
def calculateNodeVelocity(nodeTimes, nodeLocations, nVelocity):
    nVelocity.clear()
    if len(nodeTimes) == 1:
        nVelocity.extend([0, 0, 0] if g_scn3D else [0, 0])
    else:
        try:
            timeSpan = nodeTimes[1] - nodeTimes[0]
            xVel = (nodeLocations[1][0] - nodeLocations[0][0])/timeSpan
            nVelocity.append(xVel)
            yVel = (nodeLocations[1][1] - nodeLocations[0][1])/timeSpan
            nVelocity.append(yVel)
            if g_scn3D:
                zVel = (nodeLocations[1][2] - nodeLocations[0][2])/timeSpan
                nVelocity.append (zVel)
        except ZeroDivisionError:
            nVelocity.extend([0, 0, 0] if g_scn3D else [0, 0])

# Definition of Generator Function, provides node locations every 'interval' given the times and locationss vector
def locationGenerator(times, locations, g_interval):
    currentTime = times[0][0] # Assumed to be the same for all nodes
    endTime = times[0][-1] # Assumed to be the same for all nodes
    velocities = []
    # Calculation of initial Velocity of each node
    for nodeTimes, nodeLocations in zip (times, locations):
        currentNodeVelocity = []
        calculateNodeVelocity (nodeTimes, nodeLocations, currentNodeVelocity)
        velocities.append(currentNodeVelocity)
    # Generation of X, Y, Z Vectors containing location coordinates of all nodes at the current frame
    for f in range(0, math.ceil(endTime/g_interval)+1):
        X = []
        Y = []
        if g_scn3D:
            Z = []
        for nodeTimes, nodeLocations, nVelocity in zip(times, locations, velocities):
            if len(nodeTimes) == 1:
                X.append(nodeLocations[0][0])
                Y.append(nodeLocations[0][1])
                if g_scn3D:
                    Z.append(nodeLocations[0][2])
                continue
            while currentTime >= nodeTimes[1]:
                # Use 'del' to modify the same list that will update the times and locations variables
                del nodeTimes[0]
                del nodeLocations[0]
                if (len(nodeTimes) == 1) or (currentTime < nodeTimes[1]):
                    calculateNodeVelocity(nodeTimes, nodeLocations, nVelocity)
                if len(nodeTimes) == 1:
                    break
            t = currentTime - nodeTimes[0]
            x = nodeLocations[0][0] + nVelocity[0]*t
            y = nodeLocations[0][1] + nVelocity[1]*t
            X.append(x)
            Y.append(y)
            if g_scn3D:
                z = nodeLocations[0][2] + nVelocity[2]*t
                Z.append(z)
        if g_scn3D:
            yield X, Y, Z
        else:
            yield X, Y
        currentTime += g_interval

# Function to plot a frame containing nodes in the figure
def update(loctns):
    global g_currentFT, g_currentSet, g_labelList
    g_currentSet.remove()
    ax.set_xlabel("x-axis | time:{:7.2f}s".format(g_currentFT))
    if g_scn3D:
        g_currentSet = ax.scatter(loctns[0], loctns[1], loctns[2], s= 10, c = 'b')
        if g_drawLabel:
            if g_currentFT == 0:
                for i in range (len (loctns[0])):
                    g_labelList.append(ax.text(loctns[0][i]+5, loctns[1][i]+5, loctns[2][i], '%s' % (str(i)), zdir='x', size=8, color='k'))
            else:
                for i in range (len (loctns[0])):
                    g_labelList[i].set_x(loctns[0][i]+5)
                    g_labelList[i].set_y(loctns[1][i]+5)
                    g_labelList[i].set_3d_properties(z=loctns[2][i], zdir='x')
    else:
        g_currentSet = ax.scatter(loctns[0], loctns[1], s= 10, c = 'b')
        if g_drawLabel:
            if g_currentFT == 0:
                for i in range (len (loctns[0])):
                    g_labelList.append(ax.text(loctns[0][i]+5, loctns[1][i]+5, '%s' % (str(i)), size=8, color='k'))
            else:
                for i in range (len (loctns[0])):
                    g_labelList[i].set_x(loctns[0][i]+5)
                    g_labelList[i].set_y(loctns[1][i]+5)
    g_currentFT+= g_interval

'MAIN CODE BODY STARTS HERE'
print("")
# print("\t****************************************************************")
print("\t\t*****  BonnMotion Scenario Visualization  *****\n")
# print("\t****************************************************************\n")

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg.startswith('-') and arg[1:] == 'l':
            g_drawLabel = True
            print("show nodes' labels")
        else:
            g_scnName = arg
if g_scnName is None:
    g_scnName = input("Scenario name: ")
# Read the BonnMotion scenario file and returns times and locations lists
times, locations = fRead.read_bmScenario(g_scnName + ".movements")
figParams = fRead.read_bmParams(g_scnName + ".params")

if len(times) == 0 or 'x' not in figParams or 'y' not in figParams:
    print('')
    quit()
if 'J' in figParams:
    g_scn3D = True if figParams['J'] == '3D' else False
# If J value .params file is forced 2D even when 3D data is available, allows to plot a 2D view of the data
g_scn3D = (len(locations[0][0]) == 3) if g_scn3D is True else False
# Writer = animation.writers['ffmpeg']
# writer = Writer(fps=20, metadata=dict(artist='Me'), bitrate=1800)

# PREPARING THE FIGURE
xyRelation, sizeMultiplier = calculateFigDimensions(figParams['x'], figParams['y'])
if g_scn3D:
    fig = plt.figure(figsize=(10,4.8))
    plt.subplots_adjust(left= -0.05, bottom = 0.02, right= 1, top = 0.92)
else:
    fig = plt.figure(figsize=plt.figaspect(xyRelation)*sizeMultiplier)
    plt.subplots_adjust(**getPlotMargins(xyRelation))
fig.canvas.set_window_title("Drone Mobility Scenario Visualization")
ax = fig.gca(projection= '3d' if g_scn3D else None)
if g_scn3D:
    ax.view_init (elev= 25, azim= -75)
ax.set_xlim(0, figParams['x'])
ax.set_ylim(0, figParams['y'])
ax.set_xlabel('x-axis')
ax.set_ylabel('y-axis')
if g_scn3D:
    zlim = calculateZlim(figParams['x'], figParams['y'], figParams['z'])
    ax.set_zlim(0, zlim)
    ax.set_zlabel('z-axis')
else:
    ax.grid()
    ax.set_axisbelow(True)
    ax.minorticks_on()
    ax.grid(which='major', linewidth=0.4)
if 'model' in figParams:
    ax.title.set_text(f"{g_scnName} ({figParams['model']})")
else:
    ax.title.set_text(f"{g_scnName}")

# Global variable initialized with proper object type:
g_currentSet = ax.scatter(0,0)
g_labelList = []
# print(plt.rcParams)
locationFrame = locationGenerator(times, locations, g_interval)
# The matplotlib animation function:
anim = animation.FuncAnimation(fig, update, frames=locationFrame, interval=g_interval*100, save_count=400, repeat_delay= 1000, repeat=False)
# anim.save(f"{g_scnName}.gif", writer='imagemagick', fps=20, dpi=75, extra_args=None)
# anim.save(f"{g_scnName}.gif", writer='ffmpeg', fps=20, dpi=80)
# anim.save(f"{g_scnName}.gif", writer=writer)
print("Displaying mobility from {}:".format(g_scnName+".movements"))
print("\t{} scenario".format("3D" if g_scn3D else "2D"))
print("\t{} nodes".format(len(times)))
plt.show()
print('')
