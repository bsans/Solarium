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
  Note that colormaps are assumed to be lists of the same length
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
  cinter_red = map(lambda x, y: (x + y) * weight, cmap1_red, cmap2_red)
  cinter_green = map(lambda x, y: (x + y) * weight, cmap1_green, cmap2_green)
  cinter_blue = map(lambda x, y: (x + y) * weight, cmap1_blue, cmap2_blue)
  output = [] # to be filled by 3-tuples for final colormap
  for idx, elem in enumerate(cinter_red):
    output.append((elem, cinter_green[idx], cinter_blue[idx]))

  return output
  
image1 = Image.new("RGB", (181, 181), BASENIGHT_COLOR)
image2 = Image.new("RGB", (181, 181), BASENIGHT_COLOR)
image3 = Image.new("RGB", (181, 181), BASENIGHT_COLOR)
cmaptest1 = linear_gradient(BASEDAY_COLOR, DUSK_COLOR, 180)
cmaptest2 = linear_gradient(BASEDAY_COLOR, BASENIGHT_COLOR, 180)
cmaptest3 = linear_gradient(DUSK_COLOR, BASENIGHT_COLOR, 180)
testinterout = interpolate_colormaps(cmaptest1, 0, cmaptest2, 3, 1)
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


