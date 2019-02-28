#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/28
"""
import os
import pathlib


source_dir = r'E:\workspace\github\smartlamp_core_refactor\apps'

def remove_migrations(source_dir):
    source_dir = pathlib.Path(source_dir)
    for migrations in source_dir.rglob('*'):
        if migrations.name != 'migrations':
            continue
        # migrations文件目录
        for i in migrations.iterdir():
            if i.name == '__init__.py':
                continue
            os.remove(i)
            # print(i)


if __name__ == '__main__':
    remove_migrations(r'E:\workspace\github\smartlamp_core_refactor\apps')

