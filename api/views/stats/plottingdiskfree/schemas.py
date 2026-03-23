import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from api.extensions.api import Schema, AutoSchema, TopLevelSchema
from common.models.stats import StatPlottingDiskFree

class StatPlottingDiskFreeSchema(AutoSchema):
    id = field_for(StatPlottingDiskFree, "id")

    class Meta(AutoSchema.Meta):
        table = StatPlottingDiskFree.__table__


class StatPlottingDiskFreeQueryArgsSchema(Schema):
    id = ma.fields.Str()
    hostname = ma.fields.Str()

class BatchOfStatPlottingDiskFreeSchema(TopLevelSchema):
    _toplevel = ma.fields.Nested(
        StatPlottingDiskFreeSchema,
        required=True,
        many=True
    )

class BatchOfStatPlottingDiskFreeQueryArgsSchema(Schema):
    hostname = ma.fields.Str()
