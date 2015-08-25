from enum import Enum

from flask import request, abort, redirect, render_template
from werkzeug.exceptions import MethodNotAllowed


def concat_urls(*urls):
    normalized_urls = [url.strip('/') for url in urls]
    joined_urls = '/'.join(normalized_urls)
    normalized_joined_urls = joined_urls.strip('/')
    return '/{}/'.format(normalized_joined_urls)


def slugify(value):
    return value.lower().replace(' ', '_')


class Tree:
    parent = None
    items = None

    def __init__(self, name, url=None, items=None):
        self.name = name
        self.url = url or slugify(name)
        self.register_items(items)

    def register_item(self, item):
        item.register_parent(self)
        self.items.append(item)

    def register_parent(self, parent):
        if parent is not None:
            self.parent = parent

    def register_items(self, items):
        if items is None:
            return
        if self.items is None:
            self.items = []
        for item in items:
            item.register_parent(self)
        self.items.extend(item for item in items)

    def is_root(self):
        return self.parent is None

    def absolute_url(self):
        if self.is_root():
            return self.url
        return concat_urls(self.parent.absolute_url(), self.url)

    def absolute_name(self):
        if self.is_root() or self.parent.is_root():
            return slugify(self.name)
        return '-'.join([self.parent.absolute_name(), slugify(self.name)])

    def endpoints(self):
        raise NotImplementedError

    def get_tree_endpoints(self):
        if self.is_root():
            return self.endpoints()
        else:
            return self.parent.endpoints()

    def iter_items(self):
        for item in self.items:
            yield from item.iter_items()


class View:
    def __init__(self, template_name, success_url=None):
        self.template_name = template_name
        self.success_url = success_url

    def dispatch_request(self, *args, **kwargs):
        if request.method in ('POST', 'PUT'):
            return_url, context = self.post(*args, **kwargs)
            if return_url:
                return redirect(return_url)
        elif request.method == 'GET':
            context = self.get(*args, **kwargs)
        return self.render_response(context)

    def get(self, *args, **kwargs):
        """Handle the exibition of data.

        Returns:
            dict: The context.
                {
                    'display': Display(),
                    'item': item,
                    'form': Form(),
                }
        """
        raise NotImplementedError

    def post(self, *args, **kwargs):
        """Handle the processing of data.

        Returns:
            tuple: The return url (str) and the context (dict).
                ('/', {'item': item})
        """
        raise MethodNotAllowed(['GET'])

    def get_context(self, external_ctx):
        """Format input to render."""
        return external_ctx

    def get_template_name(self):
        return self.template_name

    def render_response(self, context):
        return render_template(self.get_template_name(), **context)


class Roles(Enum):
    list = 1
    create = 2
    read = 3
    update = 4
    delete = 5


class Component(View):
    role = None
    urls = None
    name = None

    def __init__(self, controller, display, roles, tree, success_url,
                 urls=None, name=None, template_name=None):
        # from crud
        self.controller = controller
        self.display = display
        self.roles = roles
        self.tree = tree

        if urls is not None:
            self.urls = urls
        if name is not None:
            self.name = name
        super().__init__(success_url=success_url, template_name=template_name)

    # Permissions
    def is_allowed(self):
        roles = [
            name for name, __ in self.roles.get(self.role.name, ())
        ]
        return self.name in roles

    # View
    def dispatch_request(self, *args, **kwargs):
        if not self.is_allowed():
            abort(401)
        return super().dispatch_request(*args, **kwargs)

    def get_context(self, external_ctx=None):
        ctx = {
            'controller': self.controller,
            'display': self.display,
            'roles': self.roles,
            'tree': self.tree,
            'rules': self.display.get_rules(self.role.name),
        }
        if external_ctx is not None:
            ctx.update(external_ctx)
        return super().get_context(ctx)

    # Form
    def get_form(self, *args, **kwargs):
        return self.controller.form_class(*args, **kwargs)

    def get_item(self, pk):
        item = self.controller.get_item(pk)
        if item is None:
            abort(404)
        return item
