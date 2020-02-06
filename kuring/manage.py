#!/usr/bin/env python
import os
import sys


def main():

    # Adapted to support separate PRODUCTION and DEVELOPMENT configuration files
    # > For a development environment, set the environment variable '__DJ_DEVPROD' to 'dev'
    # > For a production environment, do nothing.

    if '__DJ_DEVPROD' in os.environ and os.environ['__DJ_DEVPROD'] == 'dev':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuring.settings.development')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuring.settings.production')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
