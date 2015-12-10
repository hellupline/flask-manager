from enum import Enum

from werkzeug.exceptions import MethodNotAllowed
from werkzeug.datastructures import CombinedMultiDict
from flask import request, abort, redirect, url_for, render_template, views


class TemplateView(views.View):
    def __init__(self, template_name=None, full_name=None, success_url=None):
        if template_name is not None:
            self.template_name = template_name
        self.full_name = full_name
        self.success_url = success_url

    def dispatch_request(self, *args, **kwargs):
        """Dispatch the request.
        Its the actual ``view`` flask will use.
        """
        if request.method in ('POST', 'PUT'):
            return_url, context = self.post(*args, **kwargs)
            if return_url is not None:
                return redirect(return_url)
        elif request.method in ('GET', 'HEAD'):
            context = self.get(*args, **kwargs)
        return self.render_response(context)

    def get(self, *args, **kwargs):
        """Handle the exibition of data.

        Returns:
            dict: The context.
            eg:
                {'form': Form()}
        """
        raise NotImplementedError

    def post(self, *args, **kwargs):
        """Handle the processing of data.

        Returns:
            tuple:
                The return url (str or None),
                the context (dict).
                eg:
                    ('/', {'item': item})
        """
        raise MethodNotAllowed(['GET'])

    def get_template_name(self):
        if self.full_name is None:
            return self.template_name
        return ('crud/{}.html'.format(self.full_name), ) + self.template_name

    def get_context(self, external_ctx):
        """Format input to render."""
        return external_ctx

    def render_response(self, context):
        """Render the context to a response."""
        return render_template(self.get_template_name(), **context)


class Roles(Enum):
    list = 1
    create = 2
    read = 3
    update = 4
    delete = 5


class Component(TemplateView):
    role = None
    urls = None
    name = None

    def __init__(self, controller, display, roles, tree, success_url,
                 urls=None, name=None, template_name=None, full_name=None):
        self.controller = controller
        self.display = display
        self.roles = roles
        self.tree = tree

        if urls is not None:
            self.urls = urls
        if name is not None:
            self.name = name
        super().__init__(
            success_url=success_url,
            template_name=template_name,
            full_name=full_name,
        )

    def get_success_url(self, params=None, item=None):
        if params is None:
            return url_for(self.success_url)
        if '_add_another' in params:
            return url_for(self.roles[Roles.create.name][0][1])
        elif '_continue_editing' in params and item is not None:
            return url_for(self.roles[Roles.update.name][0][1], pk=item.id)
        return url_for(self.success_url)

    # Permissions
    def is_allowed(self):
        roles = [name for name, __ in self.roles.get(self.role.name, ())]
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

    def get_form_data(self):
        return CombinedMultiDict([request.form, request.files])

    # controller convenience
    def get_form(self, *args, **kwargs):
        return self.controller.form_class(*args, **kwargs)

    def get_item(self, pk):
        item = self.controller.get_item(pk)
        if item is None:
            abort(404)
        return item
