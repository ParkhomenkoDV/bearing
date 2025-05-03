from types import MappingProxyType
import numpy as np
from numpy import pi, array, nan
from scipy import interpolate

# список использованной литературы
REFERENCES = MappingProxyType({
    1: '''Лекции Арбекова''',
    2: '''Подшипники приводов: учебное пособие / 
    [М.М. Ермолаев и др.]; под ред. А.С. Иванова. - 
    Москва: Издательство МГТУ им. Н.Э. Баумана, 2019. - 198, [2] с.: ил''',
    3: '''Детали машин: учебник для вузов /
    [Л.А. Андриенко, Д38 Б.А. Байков, М.Н. Захаров и др.]; под ред. О.А. Ряховского. -
    4-е изд., перераб. и доп. - 
    Москва: Издательство МГТУ им. Н.Э. Баумана, 2014. - 465, [7] с.: ил''',
})


class Bearing:
    """Подшипник"""
    __slots__ = ('__type',)

    BEARING_TYPES = MappingProxyType({
        -1: 'скольжения',
        0: 'радиальный шариковый',
        1: 'радиальный шариковый сферический',
        2: 'радиальный с короткими цилиндрическими роликами',
        3: 'радиальный роликовый сферический',
        4: 'радиальный роликовый игольчатый или роликовый с длинными цилиндрическими роликами',
        5: 'радиальный с витыми роликами',
        6: 'радиально-упорный шариковый',
        7: 'роликовый конический',
        8: 'упорный или упорно-радиальный шариковый',
        9: 'упорный роликовый', })

    def __init__(self, type_: int):
        assert isinstance(type_, (int, np.integer))
        assert -1 <= type_ <= 9

        self.__type = type_  # тип подшипника

    @property
    def type(self) -> tuple[int, str]:
        return self.__type, Bearing.BEARING_TYPES[self.__type]

    def number_rolling_elements(self, d, D) -> tuple[int, str]:
        """Количество тел качения [2, с. 56]"""
        if self.__type == -1: return 0, ''
        number_rolling_elements = pi * self.circumference_diameter_rolling_elements(d, D)
        number_rolling_elements /= self.diameter_rolling_elements(d, D) * array([1.2, 1.6])
        return number_rolling_elements, ''

    def diameter_rolling_elements(self, d, D):
        """Диаметр тел качения [2, с. 56]"""
        if self.__type == -1: return nan
        return 0.305 * (D - d)

    def circumference_diameter_rolling_elements(self, d, D):
        """Диаметр окружности тел качения [2, с. 56]"""
        if self.__type == -1: return nan
        return 0.5 * (d + D)

    def calc(self, d, D):
        """Ориентировочные расчеты [1]"""
        if self.__type in (0, 1, 6, 8):
            b = array([0.40, 0.48]) * (D - d)  # ширина
            Dw = array([0.27, 0.30]) * (D - d)  # диаметр шарика
            z = round(2.9 * (D + d) / (D - d))
        elif self.__type in (2, 3, 4, 5, 7, 9):
            b = array([0.30, 0.49]) * (D - d)  # ширина
            Dw = array([0.20, 0.27]) * (D - d)  # диаметр ролика
            h = array([0.16, 0.25]) * Dw  # высота направляющих буртов
        else:
            raise Exception('Тип подшипника неизвестен')
        return {'b': b, 'Dw': Dw}

    def solve(self, mu, rotation_frequency, d, D, l, e):
        """Радиальная нагрузка масляного слоя в подшипнике скольжения [1]"""
        ksi = (D - d) / d
        eta = e / (D / 2 - d / 2)
        f_m = interpolate.interp1d([1.0, 1.2, 1.5], [0.85, 1.0, 1.1], kind=1, fill_value=(nan, nan))
        m = f_m(l / d)
        C_R = m / (1 - eta) - m
        return mu * rotation_frequency * d * l * C_R / ksi ** 2, 'N'

    def static_load_capacity(self):
        """Статическая грузоподъемность"""

    def dynamic_load_capacity(self):
        """Динамическая грузоподъемность"""


if __name__ == '__main__':
    bearing = Bearing(0)
    print(bearing.calc(d=40, D=60))
    print(bearing.solve(5 * 10 ** -6, 2800, 40, 60, 40, 0.001))
