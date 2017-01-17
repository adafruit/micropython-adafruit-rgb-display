import utime
import ustruct
import framebuf


def color565(r, g, b):
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3


class DummyPin:
    """A fake gpio pin for when you want to skip pins."""
    def init(self, *args, **kwargs):
        pass

    def low(self):
        pass

    def high(self):
        pass


class Display:
    _PAGE_SET = None
    _COLUMN_SET = None
    _RAM_WRITE = None
    _RAM_READ = None
    _INIT = ()
    _ENCODE_PIXEL = ">H"
    _ENCODE_POS = ">HH"
    _DECODE_PIXEL = ">BBB"

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.init()

    def init(self):
        """Run the initialization commands."""
        for command, data in self._INIT:
            self._write(command, data)

    def _block(self, x0, y0, x1, y1, data=None):
        """Read or write a block of data."""
        self._write(self._COLUMN_SET, self._encode_pos(x0, x1))
        self._write(self._PAGE_SET, self._encode_pos(y0, y1))
        if data is None:
            size = ustruct.calcsize(self._DECODE_PIXEL)
            return self._read(self._RAM_READ,
                              (x1 - x0 + 1) * (y1 - y0 + 1) * size)
        self._write(self._RAM_WRITE, data)

    def _encode_pos(self, a, b):
        """Encode a postion into bytes."""
        return ustruct.pack(self._ENCODE_POS, a, b)

    def _encode_pixel(self, color):
        """Encode a pixel color into bytes."""
        return ustruct.pack(self._ENCODE_PIXEL, color)

    def _decode_pixel(self, data):
        """Decode bytes into a pixel color."""
        return color565(*ustruct.unpack(self._DECODE_PIXEL, data))

    def pixel(self, x, y, color=None):
        """Read or write a pixel."""
        if color is None:
            return self._decode_pixel(self._block(x, y, x, y))
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return
        self._block(x, y, x, y, self._encode_pixel(color))

    def fill_rectangle(self, x, y, width, height, color):
        """Draw a filled rectangle."""
        x = min(self.width - 1, max(0, x))
        y = min(self.height - 1, max(0, y))
        w = min(self.width - x, max(1, width))
        h = min(self.height - y, max(1, height))
        self._block(x, y, x + w - 1, y + h - 1, b'')
        chunks, rest = divmod(w * h, 512)
        pixel = self._encode_pixel(color)
        if chunks:
            data = pixel * 512
            for count in range(chunks):
                self._write(None, data)
        self._write(None, pixel * rest)

    def fill(self, color=0):
        """Fill whole screen."""
        self.fill_rectangle(0, 0, self.width, self.height, color)

    def hline(self, x, y, width, color):
        """Draw a horizontal line."""
        self.fill_rectangle(x, y, width, 1, color)

    def vline(self, x, y, height, color):
        """Draw a vertical line."""
        self.fill_rectangle(x, y, 1, height, color)

    def blit_buffer(self, buffer, x, y, width, height):
        x = min(self.width - 1, max(0, x))
        y = min(self.height - 1, max(0, y))
        w = min(self.width - x, max(1, width))
        h = min(self.height - y, max(1, height))
        self._block(x, y, x + w - 1, y + w - 1, buffer)

    def text(self, text, x=0, y=0, color=0xffff, background=0x0000):
        x = min(self.width - 1, max(0, x))
        y = min(self.height - 1, max(0, y))
        w = self.width - x
        h = min(self.height - y, 8)
        buffer = bytearray(self.width * h * 2)
        fb = framebuf.FrameBuffer(buffer, w, h, framebuf.RGB565)
        for line in text.split('\n'):
            fb.fill(background)
            fb.text(line, 0, 0, color)
            self.blit_buffer(buffer, x, y, w, h)
            y += 8;
            if y >= self.height:
                break


class DisplaySPI(Display):
    def __init__(self, spi, dc, cs, rst=None, width=1, height=1):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        if self.rst:
            self.rst.init(self.rst.OUT, value=0)
            self.reset()
        super().__init__(width, height)

    def reset(self):
        self.rst.low()
        utime.sleep_ms(50)
        self.rst.high()
        utime.sleep_ms(50)

    def _write(self, command=None, data=None):
        if command is not None:
            self.dc.low()
            self.cs.low()
            self.spi.write(bytearray([command]))
            self.cs.high()
        if data is not None:
            self.dc.high()
            self.cs.low()
            self.spi.write(data)
            self.cs.high()

    def _read(self, command=None, count=0):
        self.dc.low()
        self.cs.low()
        if command is not None:
            self.spi.write(bytearray([command]))
        if count:
            data = self.spi.read(count)
        self.cs.high()
        return data

