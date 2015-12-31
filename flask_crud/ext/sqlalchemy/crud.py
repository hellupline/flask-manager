from cached_property import cached_property

from flask_crud import crud, rules as rules_
from flask_crud.ext.sqlalchemy import utils, controller as controller_


class SQLAlchemyCrud(crud.Crud):
    db_session = None
    model = None
    extra_rules = {}
    actions = None
    filters = None

    @cached_property
    def name(self):
        return utils.get_model_name(self.model)

    @cached_property
    def controller(self):
        return controller_.SQLAlchemyController(
            db_session=self.db_session, model_class=self.model,
            filters=self.filters, actions=self.actions,
        )

    @cached_property
    def form_class(self):
        return utils.build_form(
            db_session=self.db_session, model_class=self.model)

    @cached_property
    def rules(self):
        model_columns = utils.get_columns(self.model)

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
