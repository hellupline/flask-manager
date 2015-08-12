from wtforms import fields, validators, Form, FormField  # , FieldList
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import as_declarative

from le_new_admin import SQLAlchemyController, Display
from le_new_admin.display import rules

engine = sqlalchemy.create_engine('sqlite:////tmp/le_new_admin.db', echo=True)
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
    pass


model1_controller = SQLAlchemyController(
    model_class=Model1, db_session=Session
)
model1_display = Display(
    form_class=Model1Form,
    rules=rules.NestedRule([
        rules.Text('Hello Nurse'),
        rules.HTML('<h1>Hello Nurse</h1>'),
        rules.Macro('utils.test_macro'),
        rules.Header('Hello Nurse'),
        rules.Field('field1'),
        rules.Container('utils.form_tag', rules.Text('Hello Nurse')),
        rules.NestedRule([
            rules.Text('Hello Nurse'),
            rules.Text('Hello Nurse'),
        ], separator='\n'),
        rules.FieldSet(['field1', 'field2'], header='Hello Nurse'),
    ])
)
