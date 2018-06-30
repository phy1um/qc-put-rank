import sys
import requests
from time import sleep
from PIL import Image
from qcapi import QCPlayer
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
    face = Face(FONT_TARGET)
    face.set_char_size(int(size*64))
    place_x, place_y = offsets
    for c in text:
        face.load_char(c, FT_LOAD_DEFAULT)
        glyph = face.glyph.get_glyph()
        blyph = glyph.to_bitmap(FT_RENDER_MODE_NORMAL, Vector(0, 0), True)
        put_blyph(blyph, colour, target, place_x, place_y)
        # print("Advancing x by: " + str(face.glyph.advance.x))
        place_x += face.glyph.advance.x >> 6
        # place_y += face.glyph.advance.y
    # FT_Done_Face(face)
    return place_x


def put_blyph(bl, col, target, offset_x, offset_y):
    bmp = bl.bitmap
    for y in range(bmp.rows):
        for x in range(bmp.width):
            if offset_x + x > target.width or offset_y + y > target.height:
                continue
            v = bmp.buffer[y*bmp.width + x]
            target.putpixel((offset_x + x, offset_y + y),
                            (int(col[0]*v), int(col[1]*v), int(col[2]*v),
                             int(col[3]*v)))
            # print("v={}, col[0]*v={}".format(v, col[0]*v))


def get_delta_fmt(delta):
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


def make_rank_image(name):
    player = QCPlayer.from_name(name)
    rank = player.get_rank_name("duel")
    req = requests.get("https://stats.quake.com/ranks/{}.png".format(rank))
    img = Image.open(BytesIO(req.content))
    img = img.resize((64, 64), Image.ANTIALIAS)

    text = create_target()
    text.paste(img, (0, 0, img.width, img.height))
    offset = put_text(str(player.get_rank("duel")), FONT_SIZE, (1, 1, 1, 1),
                      text, (70, int((TARGET_SIZE[1] - FONT_SIZE)/2)))

    rank_delta = player.get_rank_data("duel")["lastChange"]
    # print("delta = " + str(rank_delta))
    txt, col = get_delta_fmt(rank_delta)
    # print("colour=")
    # print(col)
    put_text(txt, FONT_SIZE * 2/3, col, text,
             (offset+10, int((TARGET_SIZE[1] - FONT_SIZE)/2)))

    text.save("rank.png")


if __name__ == "__main__":
    name = sys.argv[1]
    loop = False
    interval = -1
    if len(sys.argv) > 2:
        if sys.argv[2] == "loop":
            interval = int(sys.argv[3])
            loop = True

    while(loop):
        make_rank_image(name)
        sleep(interval)
    FT_Done_FreeType(library)
