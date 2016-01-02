from cached_property import cached_property
from flask import Blueprint

from flask_crud.utils import concat_urls, slugify


class Tree:
    """Implement a parent-child relationship for urls.

    Args:
        name (str): the name of the Node,
        url (Optional[str]): the base_url for the children,
            default to slugify(name).
        items (Optional[iterable]): a iterable with children.
    """
    parent = None
    items = None

    name = None
    url = None
    endpoint = None

    def __init__(self, name=None, url=None, items=None):
        self.items = []
        if name is not None:
            self.name = name
        if url is not None:
            self.url = url
        else:
            self.url = slugify(self.name)
        if items is not None:
            self.register_items(items)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return '<{}: name="{}" url="{}">'.format(cls_name, self.name, self.url)

    def __iter__(self):
        """Iterate over all items under ``self``."""
        for item in self.items:
            yield from item

    def register_items(self, items):
        """Bulk ``register_item``.

        Args:
            items (iterable[Tree]): sequence of nodes to be
                registered as childrens.

        """
        for item in items:
            item.set_parent(self)
        self.items.extend(items)

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

    @cached_property
    def absolute_name(self):
        """Get the absolute name of ``self``.

        Returns:
            str: the absolute name.
        """
        if self.is_root() or self.parent.is_root():
            return slugify(self.name)
        return '-'.join([self.parent.absolute_name, slugify(self.name)])

    @cached_property
    def absolute_url(self):
        """Get the absolute url of ``self``.

        Returns:
            str: the absolute url.
        """
        if self.is_root():
            return self.url
        return concat_urls(self.parent.absolute_url, self.url)

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

    def is_root(self):
        """Check if ``self`` do not have a parent ( is root node ).
        Returns:
            bool: True if no parent, False otherwise.
        """
        return self.parent is None

    def get_blueprint(self, template_folder='templates',
                      static_folder='static',
                      static_url_path='crud/static'):
        bp = Blueprint(
            slugify(self.name.lower()),
            __name__,
            url_prefix=concat_urls(self.url),

            template_folder=template_folder,
            static_folder=static_folder,
            static_url_path=static_url_path,
        )
        return self.set_urls_to_blueprint(bp)

    def set_urls_to_blueprint(self, blueprint):
        # remove parent url
        absolute_url_len = len(concat_urls(self.absolute_url))
        for url, name, view in self:
            url = url[absolute_url_len:]
            blueprint.add_url_rule(
                url, name.lower(), view, methods=['GET', 'POST'])
        return blueprint
