from flask import request

from .base import Component


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
        return a success_url and a context ( form )
READ:
    GET:
        return a context ( item )
UPDATE:
    GET:
        receive a pk
        fetch obj to form
        return a context ( item, form )
    POST:
        receive a pk
        save obj
        return a success_url and a context ( item, form )
DELETE:
    GET:
        receive a pk
        return a context ( item )
    POST:
        receive a pk
        delete obj
        return a success_url and a context
"""


class List(Component):
    urls = ['list/', 'list/<int:page>/', '']
    name = 'List'
    template_name = 'admin/list.html'

    def get(self, page=1):
        items = self.controller.get_items(page)
        return self.get_context({'items': items})

    def post(self):
        # XXX
        action = request.form['action']
        return self.success_url, self.get_context({'action': action})


class Create(Component):
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
    urls = ['read/<int:pk>/']
    name = 'Read'
    template_name = 'admin/read.html'

    def get(self, pk):
        item = self.get_item(pk)
        context = {'item': item}
        return self.get_context(context)


class Update(Component):
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
