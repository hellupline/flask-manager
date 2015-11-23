from functools import partial
from math import ceil
from flask import request, url_for

from flask_crud.base import Component, Roles


"""
A SIMPLE CRUD STRUCTURE.
LIST:
    GET:
        return a context ( items )
    POST:
        execute action
        return a success_url and a context
CREATE:
    GET:
        return a context ( form )
    POST:
        save obj
        return a success_url and a context ( form, errors )
READ:
    GET:
        receive a pk
        fetch obj
        return a context ( item )
UPDATE:
    GET:
        receive a pk
        fetch obj
        return a context ( item, form )
    POST:
        receive a pk
        fetch obj
        update obj
        return a success_url and a context ( item, form, errors )
DELETE:
    GET:
        receive a pk
        fetch obj
        return a context ( item )
    POST:
        receive a pk
        delete obj
        return a success_url and a context
"""
"""
Each Component have:
    Permission, Template_name
    Url, Name

Each Component receive:
    Controller, Display, Roles, Success_url ( for POST Method )
    and a possible a form class ( Overwrite Display form class )
"""


class List(Component):
    role = Roles.list
    url = 'list/'
    name = 'List'
    template_name = 'crud/list.html'

    def get(self, page=1):
        order_by = request.args.get('order_by')
        items, total = self.controller.get_items(
            page, order_by, filters=request.args)
        filter_form = self.controller.get_filter_form()(request.args)
        action_form = self.controller.get_action_form()()
        return self.get_context({
            'filter_form': filter_form,
            'show_filter_form': self.controller.filters is not None,
            'action_form': action_form,
            'show_action_form': self.controller.actions is not None,
            'order_by': order_by,
            'url_generator': partial(
                url_for, request.url_rule.endpoint, **request.args),
            'items': items,
            'total': total,
            'page': page,
            'pages': ceil(total/self.controller.per_page),
        })

    def post(self):
        self.controller.execute_action(self.get_form_data())
        return self.get_success_url(), self.get_context({})


class Create(Component):
    role = Roles.create
    url = 'create/'
    name = 'Create'
    template_name = 'crud/create.html'

    def get(self):
        form = self.get_form(self.get_form_data())
        return self.get_context({'form': form})

    def post(self):
        form = self.get_form(self.get_form_data())
        success_url = None
        if form.validate():
            item = self.controller.create_item(form)
            success_url = self.get_success_url(self.get_form_data(), item)
        return success_url, self.get_context({'form': form})


class Read(Component):
    role = Roles.read
    url = 'read/<int:pk>/'
    name = 'Read'
    template_name = 'crud/read.html'

    def get(self, pk):
        item = self.get_item(pk)
        return self.get_context({'item': item})


class Update(Component):
    role = Roles.update
    url = 'update/<int:pk>/'
    name = 'Update'
    template_name = 'crud/update.html'

    def get(self, pk):
        item = self.get_item(pk)
        form = self.get_form(self.get_form_data(), obj=item)
        return self.get_context({'item': item, 'form': form})

    def post(self, pk):
        item = self.get_item(pk)
        form = self.get_form(self.get_form_data(), obj=item)
        success_url = None
        if form.validate():
            self.controller.update_item(item, form)
            success_url = self.get_success_url(self.get_form_data())
        return success_url, self.get_context({'item': item, 'form': form})


class Delete(Component):
    role = Roles.delete
    url = 'delete/<int:pk>/'
    name = 'Delete'
    template_name = 'crud/delete.html'

    def get(self, pk):
        item = self.get_item(pk)
        return self.get_context({'item': item})

    def post(self, pk):
        item = self.get_item(pk)
        self.controller.delete_item(item)
        return url_for(self.success_url), self.get_context()
