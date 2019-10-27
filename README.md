# Visualize BonnMotion 2D and 3D scenarios
### About
This scritp takes the .movements and .params output files from a BonnMotion mobility scenario and show it using matplotlib

Tested in python 3.6, just execute
```{r}
python3 visBmScenario.py [-l] [scenario]
```
if scenario is not specified, the program will prompt to input a scenario name. 

### Options
`
[-l]  show node labels (node numbers)
`

Upcoming:
- Accept cmd line parameters to modify the real time frame interval and the visualization speed
- save command to save to a gif file instead of showing in the display

### Notes
Find fRead.py and netSimUtils.py in my NS3_auto_tests repository.
