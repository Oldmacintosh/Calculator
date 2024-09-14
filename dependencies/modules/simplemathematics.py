# -*- coding: utf-8 -*-
"""
Performs basic math operations without python float pointing problem
Main use for simple calculator
"""
import locale
from decimal import Decimal, getcontext, DivisionByZero, InvalidOperation, Overflow

locale.setlocale(locale.LC_NUMERIC, '')


def add_commas(number: str) -> str:
    """
    Add commas to a number in form of a string according to the local
    System
    """
    try:
        float(number)
    except ValueError:
        return number
    decimal_part = ''
    number = number.split('.')
    if len(number) == 2:
        decimal_part = f'.{number[1]}'
    getcontext().prec = 16
    return f'{Decimal(number[0]):n}{decimal_part}'


def remove_commas(number: str) -> str:
    """Remove commas from a number"""
    formatted_number = ''.join([element for element in number if not element == ','])
    try:
        float(formatted_number)
        return formatted_number
    except ValueError:
        return number


def remove_extra_zeroes(number: str) -> str:
    """Removes unnecessary trailing decimal zeroes"""
    try:
        if float(number) == 0:
            return '0'
        if '.' not in number:
            raise ValueError
    except ValueError:
        return number
    number = number.split('.')
    decimal_part = f'.{number[1]}'
    if eval(decimal_part) == 0:
        decimal_part = ''
    return f'{number[0]}{decimal_part}'


def eval_expression(num_1: str, operator: str, num_2: str) -> str:
    """Performs basic math operations without any long floats"""
    try:
        getcontext().prec = 16
        num_1, num_2 = remove_commas(num_1), remove_commas(num_2)  # noqa
        result = \
            remove_extra_zeroes(str(float((eval(f'Decimal(num_1) {operator} Decimal(num_2)')))))
        return 'Infinity' if result == 'inf' else result
    except DivisionByZero:
        return 'Not Defined'
    except Overflow:
        return 'Infinity'
    except InvalidOperation:
        return 'Invalid Input'


if __name__ == '__main__':
    print('Using this module 1.1+2.2=', eval_expression('1.1', '+', '2.2'))
    print('Using python 1.1+2.2=', 1.1 + 2.2)
