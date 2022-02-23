from matplotlib.patches import Wedge, Arc
import matplotlib.pyplot as plt
from random import random, randint
from math import fmod
import colorsys
import datetime

from .recaman import recaman


def create_recaman_image(buf, r_size, light=False):
    """
    Creates a square image of a part of the visualisation of the recamán's sequence. The style for the visualization
    is taken from a Numberphile video https://www.youtube.com/watch?v=FGC5TdIiT9U

    :param buf: Buffer to store the image data
    :param r_size: How long is the sequence
    :param light: Should the visualization be light colored (defaults to False)
    """
    print("Creating recamán, r_size: ", r_size, ", light: ", light)
    hue = random()  # Randomize the hue we use for the visualization

    p_rgb = colorsys.hsv_to_rgb(fmod(0.05 + hue, 1.0), 1, 1)  # Primary Color
    f_hue = fmod(0.1 + hue, 1.0)

    if light:
        c_rgb = colorsys.hsv_to_rgb(hue, 0.1, 1)     # Complementary Color
        f_rgb = colorsys.hsv_to_rgb(f_hue, 1, 0.56)  # Font Color
    else:
        c_rgb = colorsys.hsv_to_rgb(hue, 1, 0.18)
        f_rgb = colorsys.hsv_to_rgb(f_hue, 0.45, 1)

    fig = plt.figure(figsize=(10, 10), dpi=64, facecolor=c_rgb)
    ax = fig.add_axes([0, 0, 1, 1], frameon=False, aspect=1)

    s = recaman(r_size)
    max_value = 0

    # Using two for loops for this is unnecessary and I need to find a better solution later
    # This is a workaround for the fact that Arcs can't have fills in matplotlib
    for i in range(1, len(s)):
        if s[i] > max_value:
            max_value = s[i]
        mid_point = (s[i - 1] + s[i]) / 2
        if i % 2 == 0:
            t1 = 0
            t2 = 180
        else:
            t1 = 180
            t2 = 360

        wedge = Wedge(
            (mid_point, 0),
            r=i / 2,
            theta1=t1,
            theta2=t2,
            fc=(p_rgb[0], p_rgb[1], p_rgb[2], 0.1)
        )
        ax.add_patch(wedge)

    for i in range(1, len(s)):
        mid_point = (s[i - 1] + s[i]) / 2
        if i % 2 == 0:
            t1 = 0
            t2 = 180
        else:
            t1 = 180
            t2 = 360

        arc = Arc(
            (mid_point, 0),
            height=i,
            width=i,
            angle=0,
            theta1=t1,
            theta2=t2,
            ec=(p_rgb[0], p_rgb[1], p_rgb[2], 1)
        )
        ax.add_patch(arc)

    # Remove all markings
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_yticks([])
    ax.set_xticks([])

    plt.plot([0, 0], [0, 1], color=c_rgb)  # This is so we get patches to show

    # Figuring out where we should zoom in the sequence
    side_length = randint(10, r_size)
    # These max values try to make sure we don't end up with an image with none of the sequence showing
    x_max = randint(side_length, max_value)
    y_max = randint(0, int(r_size / 2))
    plt.axis([x_max - side_length, x_max, y_max - side_length, y_max])

    # Set the text to the center of the cover image
    month_string = datetime.date.today().strftime("%b\n%Y")
    plt.text(
        x_max - side_length / 2,
        y_max - side_length / 2,
        month_string,
        ha='center',
        va='center',
        color=f_rgb,
        family='monospace',
        fontsize=110
    )

    plt.gca().set_aspect('equal')  # This makes sure that the Arcs and Wedges show up as half-circles as intended
    plt.savefig(buf, format='jpg')
    buf.seek(0)
