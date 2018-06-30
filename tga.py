from enum import Enum


class ImageType(Enum):
    NoData = 0,
    UncompressedColourMap = 1,
    UncompressedTrueColour = 2,
    UncompressedGrayscale = 3,
    RunLengthColourMap = 9,
    RunLengthTrueColour = 10,
    RunLengthGrayscale = 11


class ColourMapType(Enum):
    NoMap = 0,
    MapPresent = 1,


class PixelMap(object):
    def __init__(self, width, height, format):
        self.width = width
        self.height = height
        self.format = format
        self.bps = len(format)*8
        self._in_filter = self._default_filter
        self._out_filter = lambda x: (x[2], x[1], x[0], x[3])
        self.pixel_data = [(0, 0, 0, 255)] * (width*height)

    def put_pixel(self, x, y, px):
        row_offset = y*self.width
        filtered_px = self._in_filter(px)
        self.pixel_data[row_offset + x] = filtered_px

    def get_pixel(self, x, y):
        row_offset = y*self.width
        raw = self.pixel_data[row_offset + x]
        return self._out_filter(raw)

    def get_byte_array(self):
        bytes_per_pixel = int(self.bps / 8)
        out = bytearray(self.width*self.height*bytes_per_pixel)
        for i in range(len(self.pixel_data)):
            p = self._out_filter(self.pixel_data[i])
            byte_array_index = i*bytes_per_pixel
            for i in range(len(p)):
                out[byte_array_index + i] = p[i]
        return out

    def _default_filter(self, x):
        return x

    def set_in_filter(self, f):
        self._in_filter = f

    def set_out_filter(self, f):
        self._out_filter = f


class TGAImage:

    def __init__(self, width, height, fmt, type):
        self.image_type = type
        self.pixels = PixelMap(width, height, fmt)

    def _make_header(self):
        header = bytes([
            0,  # idLength
            0,  # col map type
            self.image_type.value[0],  # image map type
            0, 0,  # col map first index
            0, 0,  # col map length
            0,  # colour map depth
            0, 0,  # origin x
            0, 0,  # origin y
            self.pixels.width & 0xff,
            (self.pixels.width & 0xff00) >> 8,  # image width
            self.pixels.height & 0xff,
            (self.pixels.height & 0xff00) >> 8,  # image height
            self.pixels.bps,  # image bps
            0x20  # image direction/format (top right)
        ])
        return header

    def _make_img_data(self):
        return self.pixels.get_byte_array()

    def get_binary_data(self):
        return self._make_header() + self._make_img_data()


if __name__ == "__main__":
    test = TGAImage(100, 100, 'rgba', ImageType.UncompressedTrueColour)
    test.pixels.put_pixel(5, 5, (255, 0, 0, 255))
    test.pixels.put_pixel(6, 6, (0, 255, 0, 177))
    test.pixels.put_pixel(7, 7, (0, 0, 255, 40))
    test.pixels.put_pixel(99, 99, (0, 0, 0, 0))
    with open('test.tga', 'wb') as f:
        f.write(test.get_binary_data())
    print("Done")
