from math import cos, sin, pi, sqrt


def _circle_point(center, radius, angle, limit):
    x = int(round(center[0] + (radius * cos((pi * angle) / 180))))
    y = int(round(center[1] + (radius * sin((pi * angle) / 180))))

    if x < limit[0]:
        x = limit[0]
    if y < limit[0]:
        y = limit[0]
    if x > limit[1]:
        x = limit[1]
    if y > limit[1]:
        y = limit[1]

    return x, y


def _ellipse_eq(a, b, x):

    a2 = a * a
    x2 = x * x

    if a2 < x2 or a == 0:
        print(a2, x2, a)
        raise ValueError('ellipse point out of bound')

    else:
        return -(abs(b / a) * sqrt(a2 - x2))


def _angle_compensation(number_of_lines, b_value=0.1):
    angles = []
    nn = (number_of_lines - 1) / 2

    if number_of_lines % 2 == 0:
        a_value = (number_of_lines - 2) / 4
        minus_start = -(number_of_lines - 1) / 2
        minus_center = minus_start + (number_of_lines - 2) / 4
        minus_stop = minus_start + (number_of_lines - 2) / 2

    else:
        a_value = (number_of_lines - 1) / 4
        minus_start = -(number_of_lines - 1) / 2
        minus_center = minus_start + (number_of_lines - 1) / 4
        minus_stop = minus_start + (number_of_lines - 1) / 2

    plus_center = -minus_center

    for i in range(number_of_lines):

        x = i - nn

        if i == 0 and number_of_lines % 2 == 1:
            el_y = _ellipse_eq(a_value, b_value, x + plus_center) + (2 * b_value)
        elif i == number_of_lines - 1 and number_of_lines % 2 == 1:
            el_y = _ellipse_eq(a_value, b_value, x + minus_center) + (2 * b_value)
        elif x <= minus_center:
            el_y = _ellipse_eq(a_value, b_value, x + plus_center) + b_value
        elif x <= minus_stop:
            el_y = -(_ellipse_eq(a_value, b_value, x + plus_center) + b_value)
        elif x <= plus_center:
            el_y = -(_ellipse_eq(a_value, b_value, x + minus_center) + b_value)
        else:
            el_y = _ellipse_eq(a_value, b_value, x + minus_center) + b_value

        # print(i, el_y)

        angles.append(el_y)

    return angles


class ConeEmitter:
    def __init__(self, image_shape, emitter_count, emitter_range, iteration_count, angle_compensation=0.1):
        x, y = image_shape
        self.limit = (0, x - 1)
        if x != y or x < 0 or emitter_count < 0 or iteration_count < 0 or emitter_range < 0 or emitter_range > 360:
            raise ValueError('wrong input format')

        self._range = emitter_range / 2
        self._iteration_count = iteration_count
        self._emitter_count = emitter_count

        self._circle_radius = int(round(x / 2))
        self._circle_center = (self._circle_radius, self._circle_radius)

        self._current_angle = 0
        self._current_point = _circle_point(self._circle_center, self._circle_radius, self._current_angle, self.limit)

        self._angle_delta = 360 / self._iteration_count

        self._point_angle_delta = (self._range / (self._emitter_count + 1)) * 2

        self._iteration_num = 0
        self._emitter_num = 0

        self._current_point_angle = self._current_angle + self._range - self._point_angle_delta + 180

        self._angle_compensator = _angle_compensation(emitter_count, angle_compensation)

    def __iter__(self):
        return self

    def __next__(self):  # Python 2: next(self)
        if self._iteration_num != self._iteration_count:

            if self._emitter_num != self._emitter_count:
                second_point = _circle_point(self._circle_center, self._circle_radius, self._current_point_angle,
                                             self.limit)

                self._current_point_angle -= (self._point_angle_delta + self._angle_compensator[self._emitter_num])
                self._emitter_num += 1

                return self._current_point, second_point

            else:
                self._iteration_num += 1
                self._emitter_num = 0

                if self._iteration_num != self._iteration_count:
                    self._current_angle += self._angle_delta
                    self._current_point = _circle_point(self._circle_center, self._circle_radius, self._current_angle,
                                                        self.limit)

                    self._current_point_angle = self._current_angle + self._range - self._point_angle_delta + 180

                    second_point = _circle_point(self._circle_center, self._circle_radius, self._current_point_angle,
                                                 self.limit)

                    self._current_point_angle -= (self._point_angle_delta + self._angle_compensator[self._emitter_num])
                    self._emitter_num += 1

                    return self._current_point, second_point
                else:
                    raise StopIteration
        else:
            raise StopIteration


class ParallelEmitter:
    def __init__(self, image_shape, emitter_count, emitter_range, iteration_count, angle_compensation=0.1):
        x, y = image_shape
        self._limit = (0, x - 1)
        if x != y or x < 0 or emitter_count < 0 or iteration_count < 0 or emitter_range < 0 or emitter_range > 180:
            raise ValueError('wrong input format')

        self._range = emitter_range / 2
        self._iteration_count = iteration_count
        self._emitter_count = emitter_count

        self._circle_radius = int(round(x / 2))
        self._circle_center = (self._circle_radius, self._circle_radius)

        self._current_angle = 0

        self._angle_delta = 180 / self._iteration_count

        self._point_angle_delta = (self._range / (self._emitter_count + 1)) * 2

        self._iteration_num = 0
        self._emitter_num = 0

        self._first_angle = self._current_angle + self._range - self._point_angle_delta
        self._second_angle = self._current_angle - self._range + self._point_angle_delta + 180

        self._angle_compensator = _angle_compensation(emitter_count, angle_compensation)

    def __iter__(self):
        return self

    def __next__(self):  # Python 2: next(self)
        if self._iteration_num != self._iteration_count:

            if self._emitter_num != self._emitter_count:
                first_point = _circle_point(self._circle_center, self._circle_radius, self._first_angle, self._limit)
                second_point = _circle_point(self._circle_center, self._circle_radius, self._second_angle, self._limit)

                self._first_angle -= (self._point_angle_delta + self._angle_compensator[self._emitter_num])
                self._second_angle += (self._point_angle_delta + self._angle_compensator[self._emitter_num])

                self._emitter_num += 1

                return first_point, second_point

            else:
                self._iteration_num += 1
                self._emitter_num = 0

                if self._iteration_num != self._iteration_count:
                    self._current_angle += self._angle_delta

                    self._first_angle = self._current_angle + self._range - self._point_angle_delta
                    self._second_angle = self._current_angle - self._range + self._point_angle_delta + 180

                    first_point = _circle_point(self._circle_center, self._circle_radius, self._first_angle,
                                                self._limit)
                    second_point = _circle_point(self._circle_center, self._circle_radius, self._second_angle,
                                                 self._limit)

                    self._first_angle -= (self._point_angle_delta + self._angle_compensator[self._emitter_num])
                    self._second_angle += (self._point_angle_delta + self._angle_compensator[self._emitter_num])

                    self._emitter_num += 1

                    return first_point, second_point

                else:
                    raise StopIteration
        else:
            raise StopIteration

# for i in ConeEmitter(np.zeros([1000, 1000]).shape, 100, 180, 1000):
#    print(i)
