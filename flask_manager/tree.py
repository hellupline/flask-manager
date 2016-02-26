from cached_property import cached_property
from flask import Blueprint

from flask_manager import views, utils


class Tree:
    """Implement a parent-child relationship for urls.

    Args:
        name (str): the name of the Node,
        url (Optional[str]): the base_url for the children,
            default to utils.slugify(name).
        items (Optional[iterable]): a iterable with children.
    """
    parent = None
    items = None
    name = None
    url = None
    endpoint = None

    def __init__(self, name=None, url=None, items=None):
        self.items = []
        if items is not None:
            self.register_items(items)
        if name is not None:
            self.name = name
        if url is not None:
            self.url = url
        else:
            self.url = utils.slugify(self.name)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return '<{}: name="{}" url="{}">'.format(cls_name, self.name, self.url)

    # {{{ Tree interface
    def register_items(self, items):
        """Bulk ``register_item``.

        Args:
            items (iterable[Tree]):
                Sequence of nodes to be registered as children.
        """
        for item in items:
            item.set_parent(self)
        self.items.extend(items)

    def set_parent(self, parent):
        """Set parent node.
        This method does not add ``self`` to ``parent.items``.

        Args:
            parent (Tree): another node which will become parent of ``self``
        """
        if parent is not None:
            self.parent = parent

    def is_root(self):
        """Check if ``self`` do not have a parent ( is root node ).
        Returns:
            bool: True if no parent, False otherwise.
        """
        return self.parent is None
    # }}} Tree interface

    # {{{ Menu interface
    def endpoints_tree(self):
        """Get the entire tree endpoints."""
        if self.is_root():
            return self.endpoints()
        return self.parent.endpoints_tree()

    def endpoints(self):
        """
        Get all the endpoints under this node in a tree like structure.

        Returns:
            (tuple):
                name (str): This node's name.
                endpoint (str): Endpoint name relative to root.
                children (list): ``child.endpoints for each child

        """
        children = [item.endpoints() for item in self.items]
        return self.name, self.endpoint, children

    def all_endpoints(self):
        for item in self.items:
            yield from item.all_endpoints()
        try:
            yield self.endpoint.strip('.')
        except AttributeError:
            pass
    # }}} Menu interface

    # {{{ Blueprint interface
    def get_nodes(self):
        for item in self.items:
            yield from item.get_nodes()

    @cached_property
    def absolute_name(self):
        """Get the absolute name of ``self``.

        Returns:
            str: the absolute name.
        """
        if self.is_root() or self.parent.is_root():
            return utils.slugify(self.name)
        return ':'.join([self.parent.absolute_name, utils.slugify(self.name)])

    @cached_property
    def absolute_url(self):
        """Get the absolute url of ``self``.

        Returns:
            str: the absolute url.
        """
        if self.is_root():
            return utils.concat_urls(self.url)
        return utils.concat_urls(self.parent.absolute_url, self.url)
    # }}} Blueprint interface


class Index(Tree):
    view_class = views.LandingView
    decorators = ()

    @cached_property
    def endpoint(self):
        return '.{}'.format(self._view_name())

    def get_nodes(self):
        yield from super().get_nodes()
        yield self._get_view()

    # {{{ Helpers
    def _view_name(self):
        if self.is_root():
            return 'home'
        return self.absolute_name

    def _decorate_view(self, view):
        for decorator in self.decorators:
            view = decorator(view)
        return view

    def _get_view(self):
        url = utils.concat_urls(self.absolute_url)
        name = self._view_name()
        view = self.view_class.as_view(
            name, parent=self, view_name=name)
        return url, name, self._decorate_view(view)
    # }}}

    # {{{ Blueprint
    def create_blueprint(self,
                         template_folder='templates/foundation',
                         static_folder='static/foundation',
                         static_url_path='crud/static'):
        blueprint = Blueprint(
            utils.slugify(self.name), __name__,
            url_prefix=utils.concat_urls(self.url),
            template_folder=template_folder,
            static_folder=static_folder,
            static_url_path=static_url_path,
        )
        self.set_urls(blueprint)
        return blueprint

    def set_urls(self, blueprint):
        # remove parent url
        absolute_url_len = len(utils.concat_urls(self.absolute_url))
        for url, name, view in self.get_nodes():
            url = url[absolute_url_len:]
            blueprint.add_url_rule(
                url, name.lower(), view,
                methods=['GET', 'POST']
            )
        return blueprint
    # }}}
