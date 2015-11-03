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
    #  Class Form(base_class):
    #      for key, relationship in get_relationships(model_class):
    #          vars()[key] = convert_relationship(relationship, db_session)
    #      class Meta:
    #          model = model_class
    #          ** meta_args
    class_name = '{}Form'.format(utils.get_model_name(model_class))
    meta_body = {'model': model_class}
    if meta_args is not None:
        meta_body.update(meta_args)
    body = utils.get_relationships_fields(
        model_class, db_session, inlines or [])
    body['Meta'] = type('Meta', (), meta_body)
    return type(class_name, (base_class,), body)


def build_display(model_class=None, columns=None, **kwargs):
    if columns is None:
        if model_class is None:
            raise ValueError('model_class or columns is required.')
        columns = utils.get_columns(model_class)
    columns = rules_.ColumnSet(columns)
    form_rules = [rules_.Form()]
    return display_.Display(
        list=kwargs.get('list', columns),
        create=kwargs.get('create', form_rules),
        read=kwargs.get('read', columns),
        update=kwargs.get('update', form_rules),
        delete=kwargs.get('delete', columns),
    )
