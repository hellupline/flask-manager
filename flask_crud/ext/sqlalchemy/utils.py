from functools import partial

from wtforms.ext.sqlalchemy.fields import (
    QuerySelectField, QuerySelectMultipleField)
from wtforms import FormField
from wtforms_alchemy import ModelForm, ModelFieldList, ModelFormField

import sqlalchemy as sa


RELATIONSHIP_TYPES_TO_FIELD = {
    # 'MANYTOMANY': QuerySelectMultipleField,
    'MANYTOONE': QuerySelectField,
}


def get_model_name(model_class):
    return sa.inspect(model_class).entity.__name__


def get_columns(model_class):
    def is_data_column(column):
        return not (column.primary_key or column.foreign_keys)

    columns = sa.inspect(model_class).columns
    return [key for key, column in columns.items() if is_data_column(column)]


# relationships
def get_rel_fields(model_class, db_session, inlines):
    relationships = sa.inspect(model_class).relationships.items()
    return {
        key: relationship_field(rel, db_session, inline=key in inlines)
        for key, rel in relationships
    }


def relationship_field(relationship, db_session, inline=False):
    if inline:
        return relationship_field_inline(relationship)
    return relationship_field_simple(relationship, db_session)


def relationship_field_inline(relationship):
    remote_model = relationship.mapper.entity

    class InlineForm(ModelForm):
        class Meta:
            model = remote_model
    if relationship.direction.name == 'ONETOMANY':
        return ModelFieldList(FormField(InlineForm))
    return ModelFormField(InlineForm)


def relationship_field_simple(relationship, db_session):
    remote_model = relationship.mapper.entity
    column = relationship.local_remote_pairs[0][0]

    try:
        field = RELATIONSHIP_TYPES_TO_FIELD[relationship.direction.name]
    except KeyError:
        return None
    return field(
        query_factory=partial(db_session.query, remote_model),
        allow_blank=column.nullable
    )
