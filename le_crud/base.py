from enum import Enum

from flask import request, abort, redirect, url_for, render_template, views
from werkzeug.exceptions import MethodNotAllowed


def concat_urls(*urls):
    """Concat Urls
    Args:
        *args: (str)

    Returns:
        str: urls starting and ending with / merged with /
    """
    normalized_urls = [url.strip('/') for url in urls]
    joined_urls = '/'.join(normalized_urls)
    normalized_joined_urls = joined_urls.strip('/')
    return '/{}/'.format(normalized_joined_urls)


def slugify(value):
    """Simple Slugify."""
    return value.lower().replace(' ', '_')


class Tree:
    """Implement a parent-child relationship for urls.

    Args:
        name (str): the name of the Node,
        url (Optional[str]): the base_url for the children,
            default to slugify(name).
        items (Optional[iterable]): a iterable with children.

    Examples:
        >>> Tree('Parent', url='parent-example', items=[Tree('Child')])
        <Tree: name="Parent", url="parent-example">
    """
    parent = None
    items = None

    def __init__(self, name, url=None, items=None):
        self.name = name
        self.url = url or slugify(name)
        self.register_items(items)

    def __repr__(self):
        return '<{}: name="{}", url="{}">'.format(
            self.__class__.__name__, self.name, self.url)

    def __str__(self):
        return self.name

    def register_item(self, item):
        """Register the item with its parent.

        Args:
            item (Tree): another node which will become child of ``self``.
        """
        item.set_parent(self)
        self.items.append(item)

    def set_parent(self, parent):
        """Set parent node.
        This method does not add ``self`` to ``parent.items``.

        Args:
            parent (Tree): another node which will become parent of ``self``
        """
        if parent is not None:
            self.parent = parent

    def register_items(self, items):
        """Bulk ``register_item``.

        Args:
            items (iterable[Tree]): sequence of nodes to be
                registered as childrens.

        """
        if items is None:
            return
        if self.items is None:
            self.items = []
        for item in items:
            item.set_parent(self)
        self.items.extend(item for item in items)

    def is_root(self):
        """Check if ``self`` do not have a parent ( is root node ).
        Returns:
            bool: True if no parent, False otherwise.
        """
        return self.parent is None

    def absolute_url(self):
        """Get the absolute url of ``self``.

        Returns:
            str: the absolute url.
        """
        if self.is_root():
            return self.url
        return concat_urls(self.parent.absolute_url(), self.url)

    def absolute_name(self):
        """Get the absolute name of ``self``.

        Returns:
            str: the absolute name.
        """
        if self.is_root() or self.parent.is_root():
            return slugify(self.name)
        return '-'.join([self.parent.absolute_name(), slugify(self.name)])

    def endpoints(self):
        """All endpoints under ``self``."""
        raise NotImplementedError

    def get_tree_endpoints(self):
        """Get the entire tree endpoints."""
        if self.is_root():
            return self.endpoints()
        else:
            return self.parent.get_tree_endpoints()

    def iter_items(self):
        """Iterate over all items under ``self``."""
        for item in self.items:
            yield from item.iter_items()


class TemplateView(views.View):
    def __init__(self, template_name=None, success_url=None):
        if template_name is not None:
            self.template_name = template_name
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

    def get_context(self, external_ctx):
        """Format input to render."""
        return external_ctx

    def render_response(self, context):
        """Render the context to a response."""
        return render_template(self.template_name, **context)


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
                 urls=None, name=None, template_name=None):
        self.controller = controller
        self.display = display
        self.roles = roles
        self.tree = tree

        if urls is not None:
            self.urls = urls
        if name is not None:
            self.name = name
        super().__init__(success_url=success_url, template_name=template_name)

    def get_success_url(self, params, item=None):
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

    # Form
    def get_form(self, *args, **kwargs):
        return self.controller.form_class(*args, **kwargs)

    def get_item(self, pk):
        item = self.controller.get_item(pk)
        if item is None:
            abort(404)
        return item
