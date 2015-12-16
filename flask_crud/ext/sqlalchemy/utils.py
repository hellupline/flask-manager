from functools import partial

from wtforms.ext.sqlalchemy.fields import (
    QuerySelectField, QuerySelectMultipleField)
from wtforms import FormField
from wtforms_alchemy import ModelForm, ModelFieldList, ModelFormField

import sqlalchemy as sa


RELATIONSHIP_TYPES_TO_FIELD = {
    'MANYTOMANY': QuerySelectMultipleField,
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
def get_rel_fields(model_class, db_session,
                   inline_field_names=None,
                   exclude_relationships=None):
    if exclude_relationships is None:
        exclude_relationships = set()
    if inline_field_names is None:
        inline_field_names = ()

    relationships = set(sa.inspect(model_class).relationships.items())
    fields = {}
    for key, relationship in relationships:
        if key in exclude_relationships:
            continue
        use_inline_form = key in inline_field_names
        field = relationship_field(
            relationship, db_session,
            use_inline_form=use_inline_form
        )
        if field is not None:
            fields[key] = field
    return fields


def relationship_field(relationship, db_session, use_inline_form=False):
    if use_inline_form:
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
