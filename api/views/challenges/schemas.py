import marshmallow as ma
from marshmallow_sqlalchemy import field_for

from api.extensions.api import Schema, AutoSchema, TopLevelSchema
from common.models.challenges import Challenge

class ChallengeSchema(AutoSchema):
    unique_id = field_for(Challenge, "unique_id")

    class Meta(AutoSchema.Meta):
        table = Challenge.__table__


class ChallengeQueryArgsSchema(Schema):
    unique_id = ma.fields.Str()
    hostname = ma.fields.Str()

class BatchOfChallengeSchema(TopLevelSchema):
    _toplevel = ma.fields.Nested(
        ChallengeSchema,
        required=True,
        many=True
    )

class BatchOfChallengeQueryArgsSchema(Schema):
    hostname = ma.fields.Str()
