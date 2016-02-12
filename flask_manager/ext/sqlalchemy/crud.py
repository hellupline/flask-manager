from cached_property import cached_property
from wtforms_alchemy import ModelForm
import sqlalchemy as sa

from flask_manager import crud, rules as rules_
from flask_manager.ext.sqlalchemy import controller as controller_


def get_model_name(model_class):
    return sa.inspect(model_class).entity.__name__


def get_columns(model_class):
    columns = sa.inspect(model_class).columns
    return [
        key for key, column in columns.items()
        if not (column.primary_key or column.foreign_keys)
    ]


class SQLAlchemyCrud(crud.Crud):
    db_session = None
    model = None
    extra_rules = {}
    actions = None
    filters = None

    def __init__(self, *args, **kwargs):
        self.name = get_model_name(self.model)
        super().__init__(*args, **kwargs)

    @cached_property
    def controller(self):
        return controller_.SQLAlchemyController(
            db_session=self.db_session, model_class=self.model,
            filters=self.filters, actions=self.actions,
        )

    @cached_property
    def form_class(self):
        class Form(ModelForm):
            @classmethod
            def get_session(cls):
                return self.db_session

            class Meta:
                model = self.model
        return Form

    @cached_property
    def rules(self):
        model_columns = get_columns(self.model)

        columns_rules = rules_.ColumnSet(model_columns)
        data_rules = rules_.DataFieldSet(model_columns)
        delete_rules = rules_.DataFieldSetWithConfirm(model_columns)

        form_rules = self.extra_rules.get('form', rules_.SimpleForm())
        return {
            'list': self.extra_rules.get('list', columns_rules),
            'create': self.extra_rules.get('create', form_rules),
            'read': self.extra_rules.get('read', data_rules),
            'update': self.extra_rules.get('update', form_rules),
            'delete': self.extra_rules.get('delete', delete_rules),
        }
