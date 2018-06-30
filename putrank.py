import sys
import requests
from time import sleep
from PIL import Image
from qcapi import QCPlayer
from qcapi import get_rank_name
from qcapi import QCImages
from io import BytesIO
from freetype import *
from colorsys import hsv_to_rgb


TARGET_SIZE = (680, 64)
FONT_SIZE = 64
FONT_TARGET = ".\\fonts\\Audiowide-Regular.ttf"
library = FT_Library()


def create_target():
    return Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))


def put_text(text, size, colour, target, offsets):
    """write text to a position in target image

        Args:
            text: string to write
            size: font size in pt
            colour: 4-tuple of flaots in [0,1] RGBA
            target: target PIL image to write to (although other images may 
             support putpixel)
            offsets: (x,y) offset in pixels from top-left
    """
    face = Face(FONT_TARGET)
    face.set_char_size(int(size*64))
    place_x, place_y = offsets
    for c in text:
        # load character in freetype
        face.load_char(c, FT_LOAD_DEFAULT)
        # convert glyph to bitmap we can copy
        glyph = face.glyph.get_glyph()
        blyph = glyph.to_bitmap(FT_RENDER_MODE_NORMAL, Vector(0, 0), True)
        # put "blyph" in target
        put_blyph(blyph, colour, target, place_x, place_y)
        # advance x in pixels
        place_x += face.glyph.advance.x >> 6
        # NOTE: no advance y, as we assume this is short (1-line of text)
    return place_x


def put_blyph(bl, col, target, offset_x, offset_y):
    """copy glyph (character) bitmap data to target image
    """
    bmp = bl.bitmap
    for y in range(bmp.rows):
        for x in range(bmp.width):
            # copy in n^2 individual pixels
            # this could be improved if we could "batch" rows/etc
            if offset_x + x > target.width or offset_y + y > target.height:
                continue
            v = bmp.buffer[y*bmp.width + x]
            target.putpixel((offset_x + x, offset_y + y),
                            (int(col[0]*v), int(col[1]*v), int(col[2]*v),
                             int(col[3]*v)))


def get_delta_fmt(delta):
    """arbitrary colour formatting of rank delta
    more red for bigger losses, more green for bigger gains
    """
    col = (0, 0, 0, 255)
    n = abs(delta)
    s = delta
    if delta < 0:
        sat = min(n/200 + 0.2, 1)
        r, g, b = hsv_to_rgb(0, sat, 1)
        col = (r, g, b, 1)
    else:
        s = "+"+str(n)
        sat = min(n/100 + 0.2, 1)
        r, g, b = hsv_to_rgb(1/3, sat, 1)
        col = (r, g, b, 1)
    return "(" + str(s) + ")", col


def make_rank_image(name, mode, file_name="rank.png"):
    """write image containing rank number, icon and delta to a file

        Args:
            name: string name of QC player target
            mode: gametype to get rank for (duel/tdm)
            file: output
    """
    player = QCPlayer.from_name(name)
    rank_data = player.get_rank_data(mode)
    # get name of rank from number (eg Gold_01 etc)
    rank_name = get_rank_name(player.get_rank_value(mode))
    # get image data for rank
    rank_bytes = QCImages.get_rank_bytes(rank_name)
    img = Image.open(BytesIO(rank_bytes))
    # scale rank icon up 2x
    img = img.resize((64, 64), Image.ANTIALIAS)

    text = create_target()
    # put rank image
    text.paste(img, (0, 0, img.width, img.height))
    # put rank number
    offset = put_text(str(player.get_rank_value(mode)), FONT_SIZE, (1, 1, 1, 1),
                      text, (70, int((TARGET_SIZE[1] - FONT_SIZE)/2)))

    # put delta
    rank_delta = rank_data.model.lastChange
    txt, col = get_delta_fmt(rank_delta)
    put_text(txt, FONT_SIZE * 2/3, col, text,
             (offset+10, int((TARGET_SIZE[1] - FONT_SIZE)/2)))

    text.save(file_name)


if __name__ == "__main__":
    name = sys.argv[1]
    loop = False
    interval = -1
    if len(sys.argv) > 2:
        if sys.argv[2] == "loop":
            interval = int(sys.argv[3])
            loop = True

    once = True
    while(loop or once):
        if not once:
            sleep(interval)
        make_rank_image(name, "duel")
        once = False
    FT_Done_FreeType(library)
