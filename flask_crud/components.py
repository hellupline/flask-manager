from functools import partial
from math import ceil
from flask import request, url_for

from flask_crud.views import Component, Roles


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
    Controller, Roles, Success_url ( for POST Method )
    and a possible a form class ( Overwrite Display form class )
"""


class List(Component):
    role = Roles.list
    url = 'list/'
    template_name = ('crud/list.html', )

    def get(self):
        order_by = request.args.get('order_by')
        page = int(request.args.get('page', 1))
        items, total = self.crud.controller.get_items(
            page, order_by, filters=request.args)
        filter_form = self.crud.controller.get_filter_form()(request.args)
        action_form = self.crud.controller.get_action_form()()
        return self.context({
            'filter_form': filter_form,
            'show_filter_form': self.crud.controller.filters is not None,
            'action_form': action_form,
            'show_action_form': self.crud.controller.actions is not None,
            'order_by': order_by,
            'url_generator': partial(
                url_for, request.url_rule.endpoint, **request.args),
            'items': items,
            'total': total,
            'page': page,
            'pages': ceil(total/self.crud.controller.per_page),
        })

    def post(self):
        self.crud.controller.execute_action(self.get_form_data())
        return self.get_success_url(), self.context({})


class Create(Component):
    role = Roles.create
    url = 'create/'
    template_name = ('crud/form.html', 'crud/create.html')

    def get(self):
        form = self.get_form(self.get_form_data())
        return self.context({'form': form})

    def post(self):
        form = self.get_form(self.get_form_data())
        success_url = None
        if form.validate():
            item = self.crud.controller.create_item(form)
            success_url = self.get_success_url(self.get_form_data(), item)
        return success_url, self.context({'form': form})


class Read(Component):
    role = Roles.read
    url = 'read/<int:pk>/'
    template_name = ('crud/read.html', )

    def get(self, pk):
        item = self.get_item(pk)
        return self.context({'item': item})


class Update(Component):
    role = Roles.update
    url = 'update/<int:pk>/'
    template_name = ('crud/form.html', 'crud/update.html')

    def get(self, pk):
        item = self.get_item(pk)
        form = self.get_form(self.get_form_data(), obj=item)
        return self.context({'item': item, 'form': form})

    def post(self, pk):
        item = self.get_item(pk)
        form = self.get_form(self.get_form_data(), obj=item)
        success_url = None
        if form.validate():
            self.crud.controller.update_item(item, form)
            success_url = self.get_success_url(self.get_form_data())
        return success_url, self.context({'item': item, 'form': form})


class Delete(Component):
    role = Roles.delete
    url = 'delete/<int:pk>/'
    template_name = ('crud/read.html', 'crud/delete.html')

    def get(self, pk):
        item = self.get_item(pk)
        return self.context({'item': item})

    def post(self, pk):
        item = self.get_item(pk)
        self.crud.controller.delete_item(item)
        return url_for(self.success_url), self.context()
