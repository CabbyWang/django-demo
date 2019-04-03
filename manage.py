#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartlamp.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)


def check_files_is_exists():
    """检查文件是否存在, 不存在则创建"""
    # log文件
    from django.conf import settings
    log_dir = settings.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    crontab_log = os.path.join(settings.LOG_DIR, 'django_crontab.log')
    smartlamp_log = os.path.join(settings.LOG_DIR, 'smartlamp.log')
    with open(crontab_log, 'w'), open(smartlamp_log, 'w'):
        pass

    # media文件
    for i in ('asset', 'audio', 'inspection', 'workorder'):
        media_dir = os.path.join(settings.MEDIA_ROOT, i)
        os.makedirs(media_dir, exist_ok=True)
    for i in ('cbox', 'lamp', 'pole'):
        assert_dir = os.path.join(settings.MEDIA_ROOT, 'assert', i)
        os.makedirs(assert_dir, exist_ok=True)
