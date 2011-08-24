# to test colormaps for sky gradients for solarium 
import PIL
from PIL import Image, ImageDraw
import os
import sys
import math
import pprint
import pickle
# im = Image.open("/Users/Bodhi/Desktop/solarium/whiteimage.jpg")
#draw = ImageDraw.Draw(im)
#draw.line((0, im.size[1], im.size[0], 0), fill=128)
#im.show()

# Constant color values used for colormap making
BASENIGHT_COLOR=(3, 6, 15)
BASEDAY_COLOR=(120, 181, 244)
DUSK_COLOR=(180, 154, 127)
SKYBLUE2 = (1, 50, 109)
SKYBLUE1 = (17, 106, 188)
PREDAWN_HORIZON = (61, 57, 52)
PREDAWN_HORIZ_2 = (23, 38, 54)
PREDAWN_HORIZ_3 = (8, 16, 35)
PREDAWN_ZENITH = (4, 7, 14)
BLACK = (0, 0, 0)
GRAYSCALE_20 = (20, 20, 20)
GRAYSCALE_50 = (50, 50, 50)
GRAYSCALE_100 = (100, 100, 100)
GRAYSCALE_150 = (150, 150, 150)
GRAYSCALE_200 = (200, 200, 200)
GRAYSCALE_255 = (255, 255, 255)

def linear_gradient(start_color, end_color, num_steps):
  """
  defines color gradient to use, returning a list of length steps as the values
  colors are taken as 3-tuples.  I.e. a list of 3-tuples is returned.
  casting to int is not done yet because the math will not work if so. It must 
  be done later before drawing the image, or making final colormap.
  """
  num_steps = num_steps + 0.0 # making it a float
  color_step_R = (end_color[0] - start_color[0]) / num_steps 
  color_step_G = (end_color[1] - start_color[1]) / num_steps 
  color_step_B = (end_color[2] - start_color[2]) / num_steps
  lin_grad = [start_color] # initialize list
  for i in range(int(num_steps)):
    val1 = lin_grad[-1][0] + color_step_R
    val2 = lin_grad[-1][1] + color_step_G
    val3 = lin_grad[-1][2] + color_step_B
    # thresholding negative colors to be black
    if val1 < 0:
      val1 = 0
    if val2 < 0:
      val2 = 0
    if val3 < 0:
      val3 = 0
    lin_grad.append((val1, val2, val3))
  return lin_grad


def multi_step_gradient(colors, col_list_pos):
  """
  Takes a list of colors, with an equal length list of positions where those
  colors are supposed to be positioned in the entire colormap.  Calculates
  the values for the entire colormap using linear gradient steps between each
  pair of color values.
  """

  # assume first color is at col_list_pos equal to pixel 1
  # also assume last color is at col_list_pos equal to last pixel (181)
  colormap = []
  for idx in range(len(colors) - 1):
    steps = col_list_pos[idx + 1] - col_list_pos[idx]
    colormap = colormap + linear_gradient(colors[idx], colors[idx + 1], steps)
  colormap = colormap[0:180]
  return colormap

def int_cast(cmap):
  """
  Necessary casting of all colormap values to int in order to make usable by
  downstream consumers.
  """
  int_red = [int(x[0]) for x in cmap]
  int_green = [int(x[1]) for x in cmap]
  int_blue = [int(x[2]) for x in cmap]
  output = []
  for idx, elem in enumerate(int_red):
    output.append((elem, int_green[idx], int_blue[idx]))
  return output

def draw_lines(num_lines, line_length, color_list, image):
  """
  lines have a length and a color
  eventually "lines" will be a single pixel of a color
  for now, they have a start and end and color
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
  have (0, 0, 0) values outside of the sun, and these are disregarded.  """
  cmapout = []
  lastindex = 0
  for idx, rgb in enumerate(suncmap):
    if rgb != (0, 0, 0):
      cmapout.append(rgb)
      lastindex = idx # indicates last index where suncmap had a nonzero rgb
  for i in othercmap[(lastindex + 1): len(othercmap) - 1]:
    cmapout.append(i)

  return cmapout

def output_cmap(thiscmap):
  """
  Need to spit out 3-tuple lists in a nice format for importing to C as an include
  """
  newcmap = thiscmap
  for idx, i in enumerate(newcmap):
    newcmap[idx] = '/'.join([str(x) for x in i]) 
  output = ", ".join([str(x) for x in newcmap])
  return output

def output_to_file(cmap):
  """
  Uses output_cmap to write to command line argument specified file.
  """
  f = open(sys.argv[1], 'w')
  #pickle.dump(output_cmap(cmap), f)
  output = output_cmap(cmap)
  print "writing the following to file:"
  print
  print output
  f.write(output)
  f.close()


image1 = Image.new("RGB", (181, 181), BASENIGHT_COLOR)
image2 = Image.new("RGB", (181, 181), BASENIGHT_COLOR)
image3 = Image.new("RGB", (181, 181), BASENIGHT_COLOR)
cmaptest1 = linear_gradient(BASEDAY_COLOR, DUSK_COLOR, 180)
cmaptest2 = linear_gradient(BASEDAY_COLOR, BASENIGHT_COLOR, 180)
cmaptest3 = linear_gradient(DUSK_COLOR, BASENIGHT_COLOR, 180)
noon_cmap1 = linear_gradient(SKYBLUE1, SKYBLUE2, 180)
#mid_morning_cmap1 = 
testinterout = interpolate_colormaps(cmaptest2, 0, cmaptest1, 3, 2)
pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(testinterout)
#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(newcolors)
#image1output = draw_lines(181, 181, cmaptest1, image3)
#image1output.show()
#image2output = draw_lines(181, 181, cmaptest2, image3)
#image2output.show()
#interoutput = draw_lines(181, 181, testinterout, image3)
#interoutput.show()

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
#image4output.show()
#csv_writer = lambda rows: "\n".join([", ".join([x for x in row]) for row in rows])
#print output_cmap(suntestcmap)
dawncmap = linear_gradient(PREDAWN_HORIZON, PREDAWN_ZENITH, 180)

# testing multi_step_gradient
mycolors = [PREDAWN_HORIZON, PREDAWN_HORIZ_2, PREDAWN_HORIZ_3, PREDAWN_ZENITH]
mycolorpos = [0, 20, 50, 180]
multicmap = multi_step_gradient(mycolors, mycolorpos)
#pp.pprint(multicmap)
#image6 = Image.new("RGB", (181, 181), SKYBLUE1)
#dawntest = draw_lines(181, 181, multicmap, image6)
#dawntest.show()
#print output_cmap(multicmap)
#pp.pprint(dawncmap)
#image7 = Image.new("RGB", (181, 181), SKYBLUE1)
#control = draw_lines(181, 181, dawncmap, image6)
#control.show()
gray100cmap = int_cast(linear_gradient(BLACK, GRAYSCALE_100, 180))
image8 = Image.new("RGB", (181, 181), BLACK)
gray100 = draw_lines(181, 181, gray100cmap, image8)

# take care....can only do one of the prints, not both! weird char replication
output_to_file(gray100cmap)
print
print len(gray100cmap)
gray100.show()

