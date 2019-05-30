#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Create by 王思勇 on 2019/2/28
"""
import os
import shutil
import pathlib
import platform


if platform.system() == 'Windows':
    source_dir = r'D:\workspace\github\smartlamp_core_refactor\apps'
else:
    source_dir = '/usr/share/smartlamp_core/apps'
# source_dir = r'D:\workspace\github\smartlamp-core-v3.0'


def remove_migrations(source_dir):
    source_dir = pathlib.Path(source_dir)
    for migrations in source_dir.rglob('*'):
        if migrations.name != 'migrations':
            continue
        # migrations文件目录
        for i in migrations.iterdir():
            if i.name == '__init__.py':
                continue
            print(i)
            if i.is_file():
                os.remove(i)
            elif i.is_dir():
                shutil.rmtree(i)


if __name__ == '__main__':
    remove_migrations(source_dir)

