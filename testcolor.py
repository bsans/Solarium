# to test colormaps for sky gradients for solarium 
import PIL
from PIL import Image, ImageDraw
import os
import math
import pprint
# im = Image.open("/Users/Bodhi/Desktop/solarium/whiteimage.jpg")
#draw = ImageDraw.Draw(im)
#draw.line((0, im.size[1], im.size[0], 0), fill=128)
#im.show()
BASENIGHT_COLOR=(3, 6, 15)
BASEDAY_COLOR=(120, 181, 244)
DUSK_COLOR=(180, 154, 127)
#draw.line((0,0) + (200,100), BASEDAY_COLOR)
#draw.arc((0,0,100,100), 0, 90, BASENIGHT_COLOR) 
#image1.show()

def linear_gradient(start_color, end_color, num_steps):
  """
  defines color gradient to use, returning a list of length steps as the values
  colors are taken as 3-tuples.  I.e. a list of 3-tuples is returned
  """
  num_steps = num_steps + 0.0 # making it a float
  color_step_R = (end_color[0] - start_color[0]) / num_steps 
  color_step_G = (end_color[1] - start_color[1]) / num_steps 
  color_step_B = (end_color[2] - start_color[2]) / num_steps
  lin_grad = [start_color] # initialize list
  for i in range(int(num_steps)):
    lin_grad.append((lin_grad[-1][0]+color_step_R, lin_grad[-1][1] + color_step_G,
                    lin_grad[-1][2]+color_step_B))
  return lin_grad

#testout = linear_gradient((0,0,0), (100,100,100), 20)
#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(testout)

def draw_lines(num_lines, line_length, color_list, image):
  """# lines have a length and a color
# eventually "lines" will be a single pixel of a color
  # for now, they have a start and end and color
  color_list and line_length will set the small lines we add up
  """
  # let's say they're vertical for now, and one pixel wide
  # after each, we "move" one to the right
  step_size = line_length / len(color_list)
  draw = ImageDraw.Draw(image)
  line_start = (0,0)
  for line in range(num_lines):
    this_start = line_start
    for color in color_list:
      draw.line(this_start + (this_start[0], this_start[1]+step_size), color)
      this_start = (this_start[0], this_start[1]+step_size)
    
    line_start = (line_start[0]+1, line_start[1])
  
  return image

def interpolate_colormaps(cmap1, time1, cmap2, time2, thistime):
  """
  Takes two colormaps and times (cmap1, time1), and a thistime, and linearly
  interpolates between the two colormaps, given time.  Returns the colormap
  for this time.
  Note that colormaps are assumed to be lists of the same length.
  time1 is assumed to be earlier in time than time2, so that in adding together,
  the interpolation is done by taking the difference in colors, times the weight
  factor, and added to the time1
  """

  # remember that int division results in int quotients, need to make floats
  timediff = time2 - time1 + 0.0
  thistimediff = thistime - time1 + 0.0 # time increment to current time
  weight = thistimediff / timediff
  cmap1_red = [i[0] for i in cmap1]
  cmap1_green = [i[1] for i in cmap1]
  cmap1_blue = [i[2] for i in cmap1]
  cmap2_red = [i[0] for i in cmap2]
  cmap2_green = [i[1] for i in cmap2]
  cmap2_blue = [i[2] for i in cmap2]
  # problem: we have to figure out the max of the two so that we know how to add
  # otherwise, we get extra brightness when we didn't want it

  cinter_red = map(lambda x, y: interp_colors(x, y, weight), cmap1_red, cmap2_red)
  cinter_green = map(lambda x, y: interp_colors(x, y, weight), cmap1_green, cmap2_green)
  cinter_blue = map(lambda x, y: interp_colors(x, y, weight), cmap1_blue, cmap2_blue)
  output = [] # to be filled by 3-tuples for final colormap
  for idx, elem in enumerate(cinter_red):
    output.append((elem, cinter_green[idx], cinter_blue[idx]))

  return output

def interp_colors(val1, val2, weight):
  """
  Takes two color values (an R, or a G, or a B) and a weight factor, checks 
  which is the greater, and thus knows how to do the interpolation to get a
  proper value
  """
  greater = max([val1, val2])
  lesser = min([val1, val2])
  return ((greater - lesser) * weight) + lesser

def add_colormaps(cmap1, cmap2):
  """
  Stupidly adds RGB (3-tuples) values for the two complete colormaps.
  """
  cmap1_red = [i[0] for i in cmap1]
  cmap1_green = [i[1] for i in cmap1]
  cmap1_blue = [i[2] for i in cmap1]
  cmap2_red = [i[0] for i in cmap2]
  cmap2_green = [i[1] for i in cmap2]
  cmap2_blue = [i[2] for i in cmap2]
  csum_red = map(lambda x, y: x + y, cmap1_red, cmap2_red)
  csum_green = map(lambda x, y: x + y, cmap1_green, cmap2_green)
  csum_blue = map(lambda x, y: x + y, cmap1_blue, cmap2_blue)
  output = [] # to be filled by 3-tuples for final colormap
  for idx, elem in enumerate(cinter_red):
    output.append((elem, cinter_green[idx], cinter_blue[idx]))

  return output

def add_sun(suncmap, othercmap):
  """
  The sun colormap is intended to be RGB values (3-tuples) which *replace*
  the corresponding RGB values in the other colormap.  Not adding RGBs, but
  replacing the ones in the other colormap.  The suncmap is also assumed to
  have (0, 0, 0) values outside of the sun, and these are disregarded.
  """
  cmapout = []
  lastindex = 0
  for idx, rgb in enumerate(suncmap):
    if rgb != (0, 0, 0):
      cmapout.append(rgb)
      lastindex = idx # indicates last index where suncmap had a nonzero rgb
  for i in othercmap[(lastindex + 1): len(othercmap) - 1]:
    cmapout.append(i)

  return cmapout

def output_cmap(cmap):
  """
  Need to spit out 3-tuple lists in a nice format for importing to C as an include
  """
  for idx, i in enumerate(cmap):
    cmap[idx] = "/".join([str(x) for x in i])
  output = ", ".join([str(x) for x in cmap])
  return output

image1 = Image.new("RGB", (181, 181), BASENIGHT_COLOR)
image2 = Image.new("RGB", (181, 181), BASENIGHT_COLOR)
image3 = Image.new("RGB", (181, 181), BASENIGHT_COLOR)
cmaptest1 = linear_gradient(BASEDAY_COLOR, DUSK_COLOR, 180)
cmaptest2 = linear_gradient(BASEDAY_COLOR, BASENIGHT_COLOR, 180)
cmaptest3 = linear_gradient(DUSK_COLOR, BASENIGHT_COLOR, 180)
testinterout = interpolate_colormaps(cmaptest2, 0, cmaptest1, 3, 2)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(testinterout)
#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(newcolors)
image1output = draw_lines(181, 181, cmaptest1, image3)
image1output.show()
image2output = draw_lines(181, 181, cmaptest2, image3)
image2output.show()
interoutput = draw_lines(181, 181, testinterout, image3)
interoutput.show()

testaddsun = []
for i in range(40):
  testaddsun.append((255, 255, 255))
cmaplength = 181
a = range(cmaplength)
for i in a[40:len(a)-1]:
  testaddsun.append((0, 0, 0))
image4 = Image.new("RGB", (181, 181), BASEDAY_COLOR)
addsuntestbase = []
for i in range(181):
  addsuntestbase.append(BASEDAY_COLOR)
suntestcmap = add_sun(testaddsun, addsuntestbase)
image4output = draw_lines(181, 181, suntestcmap, image4)
image4output.show()
#csv_writer = lambda rows: "\n".join([", ".join([x for x in row]) for row in rows])
print output_cmap(suntestcmap)
