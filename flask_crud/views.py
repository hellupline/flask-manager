from enum import Enum

from werkzeug.exceptions import MethodNotAllowed
from werkzeug.datastructures import CombinedMultiDict
from flask import request, abort, redirect, url_for, render_template, views


class View(views.View):
    template_name = None
    sucess_url = None
    view_name = None

    def __init__(self, view_name=None, success_url=None, template_name=None):
        """
        Args:
            view_name (str): is the name of the view,
                used to create a custom template name.
            success_url (str): is the url returned by ``post``
                if form is valid.
            template_name (tuple[str]): template nams for render_template
        """
        if template_name is not None:
            self.template_name = template_name
        if success_url is not None:
            self.success_url = success_url
        if view_name is not None:
            self.view_name = view_name

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

        Args:
            *args, **kwargs: the same args from dispatch_request

        Returns:
            (dict): Context for template
        """
        raise NotImplementedError

    def post(self, *args, **kwargs):
        """Handle the processing of data.

        Args:
            *args, **kwargs: the same args from dispatch_request

        Returns:
            (tuple): tuple containing:
                sucess_url (str): a url to return when form is valid,
                    if None, render template with the second value of the tuple
                (dict): Context for template, if success_url is None
        """
        raise MethodNotAllowed(valid_methods=['GET'])

    def get_template_name(self):
        """Return a tuple of template names for ``render_template``"""
        return ('crud/{}.html'.format(self.view_name), ) + self.template_name

    def context(self, external_ctx=None):
        """Called by ``get`` or ``post``, get the context for render_tamplate.

        Args:
            injected_context (dict): vars for template.

        Returns:
            (dict): the ``injected_context`` merged with a base context

        """
        if external_ctx is not None:
            return external_ctx
        return {}

    def render_response(self, context):
        """Render the context to a response."""
        return render_template(self.get_template_name(), **context)


class LandingView(View):
    template_name = ('crud/landing.html', )

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super().__init__(*args, **kwargs)

    def get(self):
        return {'tree': self.parent.tree_endpoints()}


class Roles(Enum):
    list = 1
    create = 2
    read = 3
    update = 4
    delete = 5


class Component(View):
    role = None
    url = None
    view_name = None

    def __init__(self, crud, urls=None, *args, **kwargs):
        """
        Args:
            crud(Crud) the crud who manages this component
        """
        self.crud = crud

        if urls is not None:
            self.urls = urls
        super().__init__(*args, **kwargs)

    def get_success_url(self, params=None, item=None):
        if params is None:
            return url_for(self.success_url)

        crud_roles = self.crud.get_roles()
        if '_add_another' in params:
            return url_for(crud_roles[Roles.create.name][0][1])
        elif '_continue_editing' in params and item is not None:
            return url_for(crud_roles[Roles.update.name][0][1], pk=item.id)
        return url_for(self.success_url)

    # Permissions
    def is_allowed(self):
        return self.view_name in self.crud.get_roles().get(self.role.name, ())

    # View
    def dispatch_request(self, *args, **kwargs):
        if not self.is_allowed():
            abort(401)
        return super().dispatch_request(*args, **kwargs)

    def context(self, external_ctx=None):
        ctx = {
            'controller': self.crud.controller,
            'display': self.crud.display,
            'roles': self.crud.get_roles(),
            'tree': self.crud.tree_endpoints(),
            'rules': self.crud.display.get_rules(self.role.name),
        }
        if external_ctx is not None:
            ctx.update(external_ctx)
        return super().context(ctx)

    # form convenience
    def get_form_data(self):
        return CombinedMultiDict([request.form, request.files])

    # controller convenience
    def get_form(self, *args, **kwargs):
        return self.crud.controller.form_class(*args, **kwargs)

    def get_item(self, pk):
        item = self.crud.controller.get_item(pk)
        if item is None:
            abort(404)
        return item
