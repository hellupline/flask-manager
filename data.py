from wtforms import fields, validators, Form  # , FormField, FieldList
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import as_declarative

from le_crud import SQLAlchemyController, Display
from le_crud.display import rules

engine = sqlalchemy.create_engine('sqlite:////tmp/le_crud.db', echo=False)
metadata = sqlalchemy.MetaData(bind=engine)
Session = scoped_session(sessionmaker(bind=engine))


@as_declarative(metadata=metadata)
class Base:
    __abstract__ = True
    query = Session.query_property()


class Model1(Base):
    __tablename__ = 'model_1'
    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, index=True, unique=True)
    field1 = sqlalchemy.Column(sqlalchemy.String(255))
    field2 = sqlalchemy.Column(sqlalchemy.String(255))
    field3 = sqlalchemy.Column(sqlalchemy.String(255))


class Model1Form(Form):
    field1 = fields.StringField(
        'field1', validators=[validators.input_required()])
    field2 = fields.StringField('field2', validators=[validators.optional()])
    field3 = fields.StringField('field3', validators=[validators.optional()])


model1_controller = SQLAlchemyController(
    model_class=Model1, db_session=Session
)
model1_display = Display(
    form_class=Model1Form,
    rules=rules.FieldSet(['field1', 'field2', 'field3'], header='Form'),
    create=rules.FormFieldSet(['field1', 'field2', 'field3'], header='Form'),
    update=rules.FormFieldSet(['field1', 'field2', 'field3'], header='Form'),
    delete=rules.FormFieldSet(['field1', 'field2', 'field3'], header='Form'),
)
