# -*- coding: utf-8 -*-
"""Solve equations"""
from decimal import Decimal, getcontext


def round_complex(_x: complex):
    """
    ...
    :param _x:
    :return:
    """
    return complex(round(_x.real, 6), round(_x.imag, 6))


def linear(_a: float, _b: float) -> dict:
    """
    Solve linear equations
    :param _a: Coefficient of x
    :param _b: Constant value
    """
    return {'root': round((-_b) / _a, 6)}


def quadratic(_a: float, _b: float, _c: float) -> dict:
    """
    Solve quadratic equations
    :param _a: Coefficient of x^2
    :param _b: Coefficient of x
    :param _c: Constant value
    """
    getcontext().prec = 6
    _a, _b, _c = Decimal(_a), Decimal(_b), Decimal(_c)
    discriminant = (_b ** 2) - (4 * _a * _c)
    sor = float((-_b) / _a)
    por = float(_c / _a)
    vertex = (float((-_b) / (2 * _a)), float((-discriminant) / (4 * _a)))
    if discriminant < 0:
        _a, _b, _c, discriminant = float(_a), float(_b), float(_c), float(discriminant)
        root_1 = round_complex((-_b + pow(discriminant, 0.5)) / (2 * _a))
        root_2 = round_complex((-_b - pow(discriminant, 0.5)) / (2 * _a))

    else:
        root_1 = float((-_b + pow(discriminant, Decimal(0.5))) / (2 * _a))
        root_2 = float((-_b - pow(discriminant, Decimal(0.5))) / (2 * _a))
    discriminant = float(discriminant)
    return {
        'root_1': root_1,
        'root_2': root_2,
        'sor': sor,
        'por': por,
        'discriminant': discriminant,
        'vertex': vertex,
    }


if __name__ == '__main__':
    print(quadratic(1, 5, 6))
