from peewee import *

DATABASE = 'report.db'
db = SqliteDatabase(DATABASE, pragmas={'foreign_keys': 1})


class BaseModel(Model):
    class Meta:
        database = db


class Driver(BaseModel):
    abbr = CharField()
    name = CharField()
    org = CharField()

    class Meta:
        indexes = (
            (('abbr',), True),
        )


class RacingReport(BaseModel):
    driver = ForeignKeyField(Driver, backref='driver')
    lap_time = CharField()

    class Meta:
        indexes = (
            (('driver',), True),
        )
