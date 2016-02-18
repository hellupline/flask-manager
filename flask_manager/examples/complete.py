from wtforms import form as form_, fields as fields_
from flask import Flask
from flask_manager import (
    controller as controller_,
    crud as crud_,
    display_rules as display_rules_
)


# XXX Do Actions example

FIELD_NAMES = ('integer', 'string', 'boolean')
app = Flask(__name__)


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


class FieldFilter(controller_.ColumnFilter):
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
            (item[self.field], str(item[self.field]).title())
            for item in data_storage.items.values()
        ]


class Controller(controller_.Controller):
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


class Form(form_.Form):
    integer = fields_.IntegerField('Integer')
    string = fields_.StringField('String')
    boolean = fields_.BooleanField('Boolean')


class Crud(crud_.Crud):
    form_class = Form
    controller = Controller(filters={
        'search': SearchFilter(['string']),
        'string': FieldFilter('string'),
        'integer': FieldFilter('integer', coerce=int),
    })
    display_rules = {
        'list': display_rules_.ColumnSet(FIELD_NAMES),
        'create': display_rules_.FormFieldSet(FIELD_NAMES),
        'read': display_rules_.DataFieldSet(FIELD_NAMES),
        'update': display_rules_.FormFieldSet(FIELD_NAMES),
        'delete': display_rules_.DataFieldSetWithConfirm(FIELD_NAMES),
    }


def main():
    for i in range(10):
        data_storage.insert(MagicDict(
            integer=i, string=str(i), boolean=bool(i % 2)))
    for i in range(20, 30):
        data_storage.insert(MagicDict(
            integer=i, string='other {}'.format(i), boolean=bool(i % 2)))

    tree = crud_.Index('Example', url='', items=[
        crud_.Tree('Node - 1', items=[
            Crud(name='SubNode - 1'),
        ])
    ])
    app.register_blueprint(tree.create_blueprint())
    app.config['SECRET_KEY'] = 'super-secret'
    app.run(debug=True)


if __name__ == '__main__':
    main()
