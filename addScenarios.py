'''
* Copyright (c) 2019 - 2020 Oscar Bautista
*
* This program is free software; you can redistribute it and/or modify it
* under the terms of the GNU General Public License version 2 as published
* by the Free Software Foundation.
*
* DESCRIPTION:
* Takes one scenario referred to as 'child' and adds mobility information of a 'parent' scenario
* along with and optional offset
*
* AUTHOR: Oscar Bautista <obaut004@fiu.edu>
'''

import sys
from my_utils import fRead

if len(sys.argv) < 3:
    print ("\nUsage:\n python3 addScenarios.py <childScenario> [-p <parentScenario>] [-r] [xoff=...] [yoff=...] [zoff=...]\n")
    print (" <childScenario>\tThe base scenario to be modified.")
    print (" -p <parentScenario>\tParent mobility scenario that child scenario will follow.")
    print (''' -r\t\t\tCoordinates in child scenario are considered relative to parent coordinates.
            \t\t(By default initial position of child scenario is maintained in the mixed scenario)''')
    print (" xoff\t\t\tCustom X offset to be added to child scenario.")
    print (" yoff\t\t\tCustom Y offset to be added to child scenario.")
    print (" zoff\t\t\tCustom Z offset to be added to child scenario.\n")
    sys.exit(1)

xOff = 0
yOff = 0
zOff = 0



#return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]
