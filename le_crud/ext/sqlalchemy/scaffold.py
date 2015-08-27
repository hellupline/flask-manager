from functools import partial

import wtforms_alchemy
import sqlalchemy as sa
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from le_crud import display, rules, crud
from . import controller


RELATIONSHIP_TYPES_TO_FIELD = {
    # 'ONETOMANY': QuerySelectMultipleField,
    'MANYTOMANY': QuerySelectMultipleField,
    'MANYTOONE': QuerySelectField,
}


def build_crud(model_class, db_session):
    crud_controller = build_controller(
        model_class=model_class, db_session=db_session)
    crud_display = build_display(model_class=model_class)
    name = sa.inspect(model_class).entity.__name__
    return crud.Crud(
        name=name,
        controller=crud_controller,
        display=crud_display,
    )


def build_controller(model_class, db_session, filters=None, actions=None):
    form_class = build_form(model_class=model_class, db_session=db_session)
    return controller.SQLAlchemyController(
        db_session=db_session,
        model_class=model_class,
        form_class=form_class,
        filters=filters,
        actions=actions,
    )


def build_form(model_class, db_session, form_base_class=wtforms_alchemy.ModelForm):
    """
        The code below does something like this:
        Class Form(form_base_class):
            for key, relationship in get_relationships(model_class):
                __dict__[key] = convert_relationship(relationship, db_session)
            class Meta:
                model = model_class
    """
    body = {
        key: convert_relationship(relationship, db_session)
        for key, relationship in get_relationships(model_class)
    }
    body['Meta'] = type('Meta', (), {'model': model_class})
    return type('Form', (form_base_class,), body)


def get_relationships(model_class):
    relationships = sa.inspect(model_class).relationships
    return [(key, rel) for key, rel in relationships.items()]


def convert_relationship(relationship, db_session):
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


def build_display(model_class):
    columns = get_columns(model_class)
    return display.Display(
        list=rules.ColumnSet(columns),
        create=[rules.Form()],
        read=rules.FieldSet(columns),
        update=[rules.Form()],
        delete=rules.FieldSet(columns),
    )


def get_columns(model_class):
    def is_data_column(column):
        return not (column.primary_key or column.foreign_keys)

    columns = sa.inspect(model_class).columns
    return [key for key, column in columns.items() if is_data_column(column)]
