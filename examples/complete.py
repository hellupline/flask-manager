from wtforms import form as form_, fields as fields_, validators
from flask import Flask
from flask_manager import (
    controller as controller_,
    tree as tree_,
    components as components_,
    display_rules as display_rules_
)


FIELD_NAMES = ('integer', 'string', 'boolean')


class MagicDict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__
    __delattr__ = dict.__delitem__


class DataStorage:
    next_pk = 0
    items = {}

    def insert(self, item):
        self.items[self.next_pk] = item
        item['id'] = self.next_pk
        self.next_pk += 1


data_storage = DataStorage()


class Form(form_.Form):
    integer = fields_.IntegerField('Integer')
    string = fields_.StringField('String')
    boolean = fields_.BooleanField('Boolean')


class Form2(form_.Form):
    integer = fields_.IntegerField('Integer', validators=[
        validators.Required()
    ])
    string = fields_.StringField('String', validators=[
        validators.Required()
    ])
    boolean = fields_.BooleanField('Boolean')


class UpdateCustonForm(components_.Update):
    def get_form(self, *args, **kwargs):
        return Form2(*args, **kwargs)


class SearchFilter(controller_.SearchFilter):
    def __init__(self, fields):
        self.fields = fields

    def filter(self, items, value):
        return [
            item
            for item in items
            for field_value in [
                item[field] for field in self.fields]
            if value in field_value
        ]


class FieldFilter(controller_.FieldFilter):
    def __init__(self, field, coerce=str):
        self.field = field
        self.coerce = coerce

    def filter(self, items, value):
        return [
            item
            for item in items
            if item[self.field] == self.coerce(value)
        ]

    def get_choices(self):
        return [
            (item.get(self.field), str(item.get(self.field)).title())
            for item in data_storage.items.values()
        ]


class Controller(controller_.Controller):
    components = (
        components_.Index,
        components_.Create,
        UpdateCustonForm,
        components_.Delete,
    )
    form_class = Form
    actions = {
        'print': print,
    }
    filters = {
        'search': SearchFilter(['string']),
        'string': FieldFilter('string'),
        'integer': FieldFilter('integer', coerce=int),
    }
    display_rules = {
        'list': display_rules_.ColumnSet(FIELD_NAMES),
        'create': display_rules_.FormFieldSet(FIELD_NAMES),
        'read': display_rules_.DataFieldSet(FIELD_NAMES),
        'update': display_rules_.SimpleForm(),
        'delete': display_rules_.DataFieldSetWithConfirm(FIELD_NAMES),
    }

    def get_items(self, page=1, order_by=None, filters=None):
        items = data_storage.items.values()
        for filter_, value in self.get_filters(filters):
            items = filter_.filter(items, value)
        return items, len(data_storage.items)

    def get_item(self, pk):
        return data_storage.items[int(pk)]

    def create_item(self, form):
        item = MagicDict()
        data_storage.insert(item)
        return self.update_item(item, form)

    def update_item(self, item, form):
        form.populate_obj(item)
        return item

    def delete_item(self, item):
        del data_storage.items[int(item.id)]


def main():
    for i in range(10):
        data_storage.insert(MagicDict(
            integer=i, string=str(i), boolean=bool(i % 2)))
    for i in range(20, 30):
        data_storage.insert(MagicDict(
            integer=i, string='other {}'.format(i), boolean=bool(i % 2)))

    tree = tree_.Root('Example', url='', items=[
        tree_.Tree('Node - 1', items=[
            Controller(name='SubNode - 1'),
        ])
    ])
    app = Flask(__name__)
    app.register_blueprint(tree.create_blueprint())
    app.config['SECRET_KEY'] = 'super-secret'
    app.run(debug=True)


if __name__ == '__main__':
    main()
