Flask-Manager
=============

A CRUD like manager for Flask.

Is Flexible
```````````

Save in a hello.py:

.. code:: python

    from flask import Flask
    from flask_manager import crud, controller, rules as rules_

    all_items = {
        i: {'id': i, 'title': 'Title - {}'.format(i)}
        for i in range(100)
    }
    next_id = 100

    class Controller(controller.Controller):
        def get_items(self, page=1, order_by=None, filters=None):
            return all_items, len(all_items)

        def get_item(self, pk):
            return all_items[pk]

        def create_item(self, form):
            # wtforms does not support dicts :( (I think:P)
            global next_id
            all_items[next_id] = {
                'id': next_id, 'title': 'Title - {}'.format(next_id)}
            next_id += 1

        def update_item(self, item, form):
            # wtforms does not support dicts :( (I think:P)
            pass

        def delete_item(self, pk):
            del all_items[pk]


    class Crud(crud.Crud):
        controller = Controller()
        # you may merge read/update to "form" if using the same columns
        rules = {
            'list': rules.ColumnSet(['title']),
            'create': rules.FormFieldSet(['title']),
            'read': rules.DataFieldSet(['title']),
            'update': rules.FormFieldSet(['title']),
            'delete': rules.DataFieldSetWithConfirm(['title']),
        }

    if __name__ == '__main__':
        app = Flask(__name__)
        admin = crud.Index('My Admin', url='', items=[
            Crud('My Crud'),
        ])
        app.register_blueprint(admin.create_blueprint())


Then execute:

.. code:: bash

    $ pip install flask-manager
    $ python hello.py
