#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/3/14
"""
# import numpy


def hasPath(matrix, rows, cols, path):
    record = [[0 for i in range(cols)] for j in range(rows)]
    def is_path(i, j, index, record):
        a = matrix[i*rows + j]
        if i < 0 or i >= rows or j < 0 or j >= cols or record[i][j] or matrix[i*cols + j] != path[index]:
            return False
        if index == len(path) - 1:
            return True
        index += 1
        record[i][j] = 1

        flag = any([
            is_path(i + 1, j, index, record),
            is_path(i - 1, j, index, record),
            is_path(i, j + 1, index, record),
            is_path(i, j - 1, index, record)]
        )
        if not flag:
            index -= 1
            record[i][j] = 0
        return flag

    for i in range(rows):
        for j in range(cols):
            index = 0
            if is_path(i, j, index, record):
                return True

    return False


def my_generator():
    print('start')
    yield 1
    print('work')
    yield 2
    print('work')
    yield 3
    print('done')


if __name__ == '__main__':
    # a = hasPath('ABCESFCSADEE', 3, 4, 'ABCCED')
    # a = hasPath('ABCESFCSADEE', 3, 4, 'AB')
    # print(a)
    for i in my_generator():
        print(i)
