from cached_property import cached_property
from wtforms_alchemy import ModelForm

from flask_crud import crud as crud_, display as display_, rules as rules_
from flask_crud.ext.sqlalchemy import controller as controller_, utils


class SQLAlchemyCrud(crud_.Crud):
    rules = {}

    def __init__(self):
        super(name=utils.get_model_name(self.model))

    @cached_property
    def controller(self):
        return controller_.SQLAlchemyController(
            db_session=self.db_session,
            model_class=self.model,
            filters=self.filters,
            actions=self.actions,
            form_class=self.form_class,
        )

    @cached_property
    def form_class(self):
        return build_form(
            db_session=self.db_session,
            model_class=self.model,
        )

    @cached_property
    def display(self):
        model_columns = utils.get_columns(self.model)
        columns_rules = rules_.ColumnSet(model_columns)
        form_rules = self.rules_.get('form', rules_.SimpleForm())
        data_rules = rules_.DataFieldSet(model_columns)
        delete_rules = rules_.DataFieldSetWithConfirm(model_columns)

        return display_.Display(
            list=self.rules.get('list', columns_rules),
            create=self.rules.get('create', form_rules),
            read=self.rules.get('read', data_rules),
            update=self.rules.get('update', form_rules),
            delete=self.rules.get('delete', delete_rules),
        )


def build_form(model_class, db_session,
               inline_field_names=None,
               exclude_relationships=None,
               base_class=ModelForm,
               meta_args=None):
    if meta_args is None:
        meta_args = {}
    body = utils.get_rel_fields(
        model_class, db_session,
        inline_field_names,
        exclude_relationships,
    )

    class Form(base_class):
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
