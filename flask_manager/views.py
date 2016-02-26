from werkzeug.exceptions import MethodNotAllowed
from flask import request, redirect, render_template, views


class View(views.View):
    template_name = None
    sucess_url = None

    def __init__(self, view_name, success_url=None):
        """A Basic View with template.

        Args:
            view_name (str): The name of the view,
                used to create a custom template name.
            success_url (str): The url returned by ``post`` if form is valid.
        """
        if success_url is not None:
            self.success_url = success_url
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
        return self.render_response(self.context(context))

    def get(self, *args, **kwargs):
        """Handle the exibition of data.

        Args:
            *args, **kwargs: the same args from dispatch_request.

        Returns:
            (dict): Context for template.
        """
        raise NotImplementedError

    def post(self, *args, **kwargs):
        """Handle the processing of data.

        Args:
            *args, **kwargs: The same args from dispatch_request.

        Returns:
            (tuple): tuple containing:
                sucess_url (str): Url to return if form is valid,
                    if None, render template with the dict.
                (dict): Context for template, if success_url is None.
        """
        raise MethodNotAllowed(valid_methods=['GET'])

    def context(self, external_ctx=None):
        """Called by ``dispatch_request``, non request template context

        Args:
            external_ctx (dict): Context for template

        Returns:
            (dict): The base context merged with ``external_ctx``.

        """
        ctx = {}
        if external_ctx is not None:
            ctx.update(external_ctx)
        return ctx

    def get_template_name(self):
        """Return a tuple of template names for ``render_template``."""
        return ('crud/{}.html'.format(self.view_name), *self.template_name)

    def render_response(self, context):
        """Render the context to a response.

        Args:
            context (dict): Vars for template.

        Returns:
            (str): Template rendered with the context.

        """
        return render_template(self.get_template_name(), **context)


class LandingView(View):
    template_name = ('crud/landing.html', )

    def __init__(self, parent, *args, **kwargs):
        """A simple landing view, template may be overwriten to customize.

        Args:
            parent (Group): ``Group`` host of ``self``.
        """
        self.parent = parent
        super().__init__(*args, **kwargs)

    def get(self):
        return self.context({'tree': self.parent.endpoints_tree()})
