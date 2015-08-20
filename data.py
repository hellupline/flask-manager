from wtforms import fields, validators, Form  # , FormField, FieldList

from sqlalchemy import create_engine, orm, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import as_declarative

from le_crud import SQLAlchemyController, Display
from le_crud.display import rules

engine = create_engine('postgresql://mucca:oiuy0987@localhost/shop')
metadata = MetaData(bind=engine)
metadata.reflect()
Session = scoped_session(sessionmaker(bind=engine))


@as_declarative(metadata=metadata)
class Base:
    __abstract__ = True
    query = Session.query_property()


class Tag:
    pass


class TagForm(Form):
    name = fields.StringField('name', validators=[validators.input_required()])
    rules = fields.StringField('rules', validators=[validators.optional()])


orm.mapper(Tag, metadata.tables['tag'])
tag_controller = SQLAlchemyController(model_class=Tag, db_session=Session)
tag_display = Display(
    form_class=TagForm,
    rules=rules.FieldSet(['name', 'rules'], header='Form'),
    list=rules.ColumnSet(['id', 'name', 'rules']),
    create=rules.FormFieldSet(['name', 'rules'], header='Form'),
    read=rules.FieldSet(['name', 'rules'], header='Form'),
    update=rules.FormFieldSet(['name', 'rules'], header='Form'),
    delete=rules.FieldSet(['name', 'rules'], header='Form'),
)
