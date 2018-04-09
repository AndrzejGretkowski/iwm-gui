import math
import numpy as np
import skimage.io as sio


class Probe:
    img = None
    pixels_visited = None

    def __init__(self, img_name):
        self.img = sio.imread(img_name, as_grey=True)
        self.pixels_visited = np.zeros(int(math.ceil(self.img.shape[0] * math.sqrt(2))))

    def shape(self):
        return self.img.shape

    def probe(self, start_point, end_point):
        x1, y1 = start_point
        x2, y2 = end_point
        x, y = x1, y1
        i = 0

        xi = int(math.copysign(1, x2 - x1))
        yi = int(math.copysign(1, y2 - y1))

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        self.pixels_visited[i] = self.img[x][y]
        i += 1

        if dx > dy:
            ai = (dy - dx) * 2
            bi = dy * 2
            d = bi - dx

            while x != x2:
                if d >= 0:
                    y += yi
                    d += ai

                else:
                    d += bi

                x += xi
                self.pixels_visited[i] = self.img[x][y]
                i += 1

        else:
            ai = (dx - dy) * 2
            bi = dx * 2
            d = bi - dy

            while y != y2:
                if d >= 0:
                    x += xi
                    d += ai

                else:
                    d += bi

                y += yi
                self.pixels_visited[i] = self.img[x][y]
                i += 1

        return np.mean(self.pixels_visited[:i])

    def raycast(self, data, value, start_point, end_point):
        x1, y1 = start_point
        x2, y2 = end_point
        x, y = x1, y1

        xi = int(math.copysign(1, x2 - x1))
        yi = int(math.copysign(1, y2 - y1))

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        data[x][y] += value

        if dx > dy:
            ai = (dy - dx) * 2
            bi = dy * 2
            d = bi - dx

            while x != x2:
                if d >= 0:
                    y += yi
                    d += ai

                else:
                    d += bi

                x += xi
                data[x][y] += value

        else:
            ai = (dx - dy) * 2
            bi = dx * 2
            d = bi - dy

            while y != y2:
                if d >= 0:
                    x += xi
                    d += ai

                else:
                    d += bi

                y += yi
                data[x][y] += value
