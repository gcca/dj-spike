from django.db import models


class PostgreSQLEnumField(models.CharField):
    """CharField that maps to a native PostgreSQL ENUM type."""

    def __init__(self, enum_name, **kwargs):
        self.enum_name = enum_name
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["enum_name"] = self.enum_name
        return name, path, args, kwargs

    def db_type(self, connection):
        if connection.vendor == "postgresql":
            return self.enum_name
        return super().db_type(connection)
