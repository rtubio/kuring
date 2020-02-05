#!/usr/bin/env python
import os
import sys


def main():

    # Minor modification: permits loading different settings for PRODUCTION and for DEVELOPMENT
    # > For development: add 'dev' as the last argument of the call
    # > For production: do nothing

    if sys.argv[-1] == 'dev':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuring.settings.development')
        args = list(sys.argv[0:-1])
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuring.settings.production')
        args = list(sys.argv)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(args)


if __name__ == '__main__':
    main()
