from django.db import models


class BbaState(models.Model):
    """Same storage model as Node SQLite bba_state (id + JSON document)."""

    id = models.IntegerField(primary_key=True)
    data = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bba_state"
