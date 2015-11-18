from wtforms_alchemy import ModelForm

from flask_crud import crud as crud_, display as display_, rules as rules_
from flask_crud.ext.sqlalchemy import controller as controller_, utils


def build_crud(model_class, db_session, crud_class=crud_.Crud,
               form_class=None, form_args=None,
               display=None, display_args=None,
               controller=None, filters=None, actions=None):
    if form_class is None:
        if form_args is None:
            form_args = {}
        form_class = build_form(
            model_class=model_class, db_session=db_session, **form_args)

    if display is None:
        if display_args is None:
            display_args = {}
        display = build_display(
            model_class=model_class, **display_args)

    if controller is None:
        controller = controller_.SQLAlchemyController(
            model_class=model_class, db_session=db_session,
            form_class=form_class, filters=filters, actions=actions)

    name = utils.get_model_name(model_class)
    return crud_class(name=name, controller=controller, display=display)


def build_form(model_class, db_session, inlines=None,
               base_class=ModelForm, meta_args=None):
    body = utils.get_rel_fields(model_class, db_session, inlines or [])
    meta_args = meta_args or {}

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


def build_display(model_class, **kwargs):
    model_columns = utils.get_columns(model_class)
    columns_rules = rules_.ColumnSet(model_columns)
    data_rules = rules_.DataFieldSet(model_columns)
    form_rules = rules_.SimpleForm()
    return display_.Display(
        list=kwargs.get('list', columns_rules),
        create=kwargs.get('create', form_rules),
        read=kwargs.get('read', data_rules),
        update=kwargs.get('update', form_rules),
        delete=kwargs.get('delete', data_rules),
    )
