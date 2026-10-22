from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from bba.store import import_from_legacy_sqlite


class Command(BaseCommand):
    help = "Node better-sqlite3 data/bba.sqlite dan Django bazasiga import."

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            nargs="?",
            default=str(settings.BASE_DIR / "data" / "bba.sqlite"),
            help="Manba SQLite fayl (default: loyiha data/bba.sqlite)",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.is_file():
            raise CommandError(f"Fayl topilmadi: {path}")
        count = import_from_legacy_sqlite(str(path))
        self.stdout.write(self.style.SUCCESS(f"{count} qator import qilindi."))
