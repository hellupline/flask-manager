from cached_property import cached_property
from wtforms_alchemy import ModelForm
import sqlalchemy as sa

from flask_manager import crud, display_rules as display_rules_
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
    extra_display_rules = {}
    db_session = None
    model = None
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
    def display_rules(self):
        fields = get_columns(self.model)
        return {
            **{
                'list': display_rules_.ColumnSet(fields),
                'create': display_rules_.SimpleForm(),
                'read': display_rules_.DataFieldSet(fields),
                'update': display_rules_.SimpleForm(),
                'delete': display_rules_.DataFieldSetWithConfirm(fields),
            },
            **{
                key: self.extra_display_rules['form']
                for key in ('create', 'update')
                if 'form' in self.extra_display_rules
            },
            **self.extra_display_rules,
        }
