from functools import partial

from wtforms.ext.sqlalchemy.fields import (
    QuerySelectField, QuerySelectMultipleField)
from wtforms import FormField
from wtforms_alchemy import ModelForm, ModelFieldList, ModelFormField

import sqlalchemy as sa

RELATIONSHIP_DIRECTION_FIELDS = {
    'MANYTOMANY': QuerySelectMultipleField,
    'MANYTOONE': QuerySelectField,
}


def get_model_name(model_class):
    return sa.inspect(model_class).entity.__name__


def get_columns(model_class):
    columns = sa.inspect(model_class).columns
    return [
        key for key, column in columns.items()
        if not (column.primary_key or column.foreign_keys)
    ]


def build_form(model_class, db_session,
               extra_fields=None,
               relationship_exclude=None,
               meta_args=None):
    if extra_fields is None:
        extra_fields = {}
    if meta_args is None:
        meta_args = {}
    body = get_rel_fields(model_class, db_session, relationship_exclude)
    body.update(extra_fields)

    class Form(ModelForm):
        @classmethod
        def get_session(cls):
            return db_session

        for key, value in body.items():
            vars()[key] = value
            del key, value

        class Meta:
            for key, value in meta_args.items():
                vars()[key] = value
                del key, value
            model = model_class

    return Form


# relationships
def get_rel_fields(model_class, db_session, exclude=None):
    if exclude is None:
        exclude = ()

    fields = {}
    for key, rel in sa.inspect(model_class).relationships.items():
        if key in exclude:
            continue
        field = relationship_field(rel, db_session)
        if field is not None:
            fields[key] = field
    return fields


def relationship_field(relationship, db_session):
    query_factory = partial(db_session.query, relationship.mapper.entity)
    column = relationship.local_remote_pairs[0][0]
    try:
        field = RELATIONSHIP_DIRECTION_FIELDS[relationship.direction.name]
    except KeyError:
        return None
    return field(query_factory=query_factory, allow_blank=column.nullable)


def relationship_field_inline(relationship):
    remote_model = relationship.mapper.entity

    class InlineForm(ModelForm):
        class Meta:
            model = remote_model
    if relationship.direction.name == 'ONETOMANY':
        return ModelFieldList(FormField(InlineForm))
    return ModelFormField(InlineForm)
