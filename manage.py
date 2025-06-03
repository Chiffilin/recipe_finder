#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    try:
        import django
        from django.core.management import execute_from_command_line

        django.setup()

        from django.core.management import call_command

        call_command("makemigrations", interactive=False)
        call_command("migrate", interactive=False)

    except Exception as e:
        print("Не вдалося застосувати міграції:", e)

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
