from functools import partial
from math import ceil
from flask import request, url_for

from le_crud.base import Component, Roles


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
    Urls, Name

Each Component receive:
    Controller, Display, Roles, Success_url ( for POST Method )
    and a possible a form class ( Overwrite Display form class )
"""


class List(Component):
    role = Roles.list
    urls = ['list/', 'list/<int:page>/', '']
    name = 'List'
    template_name = 'admin/list.html'

    def get(self, page=1):
        order_by = request.args.get('order_by')
        items, total = self.controller.get_items(
            page, order_by, filters=request.args)
        context = {
            'filter_form': self.controller.get_filter_form()(request.args),
            'action_form': self.controller.get_action_form()(),
            'order_by': order_by,
            'url_generator': partial(
                url_for, request.url_rule.endpoint, **request.args),
            'items': items,
            'total': total,
            'page': page,
            'pages': ceil(total/self.controller.per_page),
        }
        return self.get_context(context)

    def post(self):
        self.controller.execute_action(request.form)
        return self.success_url, self.get_context({})


class Create(Component):
    role = Roles.create
    urls = ['create/']
    name = 'Create'
    template_name = 'admin/create.html'

    def get(self):
        form = self.get_form()
        context = {'form': form}
        return self.get_context(context)

    def post(self):
        form = self.get_form(request.form)
        success_url = ''
        if form.validate():
            self.controller.create_item(form)
            success_url = self.success_url
        context = {'form': form}
        return success_url, self.get_context(context)


class Read(Component):
    role = Roles.read
    urls = ['read/<int:pk>/']
    name = 'Read'
    template_name = 'admin/read.html'

    def get(self, pk):
        item = self.get_item(pk)
        context = {'item': item}
        return self.get_context(context)


class Update(Component):
    role = Roles.update
    urls = ['update/<int:pk>/']
    name = 'Update'
    template_name = 'admin/update.html'

    def get(self, pk):
        item = self.get_item(pk)
        form = self.get_form(obj=item)
        context = {'item': item, 'form': form}
        return self.get_context(context)

    def post(self, pk):
        item = self.get_item(pk)
        form = self.get_form(request.form)
        success_url = ''
        if form.validate():
            self.controller.update_item(item, form)
            success_url = self.success_url
        context = {'item': item, 'form': form}
        return success_url, self.get_context(context)


class Delete(Component):
    role = Roles.delete
    urls = ['delete/<int:pk>/']
    name = 'Delete'
    template_name = 'admin/delete.html'

    def get(self, pk):
        item = self.get_item(pk)
        context = {'item': item}
        return self.get_context(context)

    def post(self, pk):
        item = self.get_item(pk)
        self.controller.delete_item(item)
        return self.success_url, self.get_context()
