from cached_property import cached_property

from flask_crud import crud as crud_, display as display_, rules as rules_
from flask_crud.ext.sqlalchemy import controller as controller_, utils


class SQLAlchemyCrud(crud_.Crud):
    db_session = None
    model = None
    actions = None
    filters = None

    rules = {}

    def __init__(self, name=None, url=None):
        if name is None:
            name = utils.get_model_name(self.model)
        super().__init__(name=name, url=url)

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
        return utils.build_form(
            db_session=self.db_session,
            model_class=self.model,

        )

    @cached_property
    def display(self):
        model_columns = utils.get_columns(self.model)
        columns_rules = rules_.ColumnSet(model_columns)
        form_rules = self.rules.get('form', rules_.SimpleForm())
        data_rules = rules_.DataFieldSet(model_columns)
        delete_rules = rules_.DataFieldSetWithConfirm(model_columns)

        return display_.Display(
            list=self.rules.get('list', columns_rules),
            create=self.rules.get('create', form_rules),
            read=self.rules.get('read', data_rules),
            update=self.rules.get('update', form_rules),
            delete=self.rules.get('delete', delete_rules),
        )
