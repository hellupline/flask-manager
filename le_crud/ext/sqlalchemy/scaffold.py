from functools import partial

import wtforms_alchemy
import sqlalchemy as sa
from wtforms import FormField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from le_crud import crud, display, rules
from le_crud.ext.sqlalchemy import controller


RELATIONSHIP_TYPES_TO_FIELD = {
    # 'ONETOMANY': QuerySelectMultipleField,
    'MANYTOMANY': QuerySelectMultipleField,
    'MANYTOONE': QuerySelectField,
}


def build_crud(model_class, db_session,
               filters=None, actions=None, inlines=None):
    name = get_model_name(model_class)
    form_class = build_form(
        model_class=model_class, db_session=db_session, inlines=inlines)
    crud_controller = controller.SQLAlchemyController(
        db_session=db_session,
        model_class=model_class,
        form_class=form_class,
        filters=filters,
        actions=actions,
    )
    crud_display = build_display(model_class=model_class)
    return crud.Crud(
        name=name, controller=crud_controller, display=crud_display,
    )


def build_form(model_class, db_session, form_base_class=wtforms_alchemy.ModelForm,
               inlines=None):
    #  The code below does something like this:
    #  Class Form(form_base_class):
    #      for key, relationship in get_relationships(model_class):
    #          __dict__[key] = convert_relationship(relationship, db_session)
    #      class Meta:
    #          model = model_class
    body = get_relationships_fields(model_class, db_session, inlines or [])
    body['Meta'] = type('Meta', (), {'model': model_class})
    name = '{}Form'.format(get_model_name(model_class))
    return type(name, (form_base_class,), body)


def build_display(model_class=None, columns=None):
    if columns is None:
        if model_class is None:
            raise ValueError('model_class or columns is required.')
        columns = get_columns(model_class)
    return display.Display(
        list=rules.ColumnSet(columns),
        create=[rules.Form()],
        read=rules.FieldSet(columns),
        update=[rules.Form()],
        delete=rules.FieldSet(columns),
    )


def get_model_name(model_class):
    return sa.inspect(model_class).entity.__name__

def get_columns(model_class):
    def is_data_column(column):
        return not (column.primary_key or column.foreign_keys)

    columns = sa.inspect(model_class).columns
    return [key for key, column in columns.items() if is_data_column(column)]


# relationships
def get_relationships_fields(model_class, db_session, inlines):
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
    class InlineForm(wtforms_alchemy.ModelForm):
        class Meta:
            model = remote_model
    if relationship.direction.name == 'ONETOMANY':
        return wtforms_alchemy.ModelFieldList(FormField(InlineForm))
    return wtforms_alchemy.ModelFormField(InlineForm)



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
