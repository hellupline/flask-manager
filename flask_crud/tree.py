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

    def __init__(self, name, url=None, items=None):
        self.items = []
        if items is not None:
            self.register_items(items)

        if url is None:
            self.url = slugify(name)
        else:
            self.url = url
        self.name = name

    def __repr__(self):
        cls_name = self.__class__.__name__
        return '<{}: name="{}" url="{}">'.format(cls_name, self.name, self.url)

    def register_items(self, items):
        """Bulk ``register_item``.

        Args:
            items (iterable[Tree]): sequence of nodes to be
                registered as childrens.

        """
        for item in items:
            item.set_parent(self)
        self.items.extend(item for item in items)

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

    def absolute_name(self):
        """Get the absolute name of ``self``.

        Returns:
            str: the absolute name.
        """
        if self.is_root() or self.parent.is_root():
            return slugify(self.name)
        return '-'.join([self.parent.absolute_name(), slugify(self.name)])

    def absolute_url(self):
        """Get the absolute url of ``self``.

        Returns:
            str: the absolute url.
        """
        if self.is_root():
            return self.url
        return concat_urls(self.parent.absolute_url(), self.url)

    def get_tree_endpoints(self):
        """Get the entire tree endpoints."""
        if self.is_root():
            return list(self.endpoints())
        return self.parent.get_tree_endpoints()

    def endpoints(self):
        """All endpoints under ``self``."""
        raise NotImplementedError

    def is_root(self):
        """Check if ``self`` do not have a parent ( is root node ).
        Returns:
            bool: True if no parent, False otherwise.
        """
        return self.parent is None

    def iter_items(self):
        """Iterate over all items under ``self``."""
        for item in self.items:
            yield from item.iter_items()

    def get_blueprint(self, template_folder='templates',
                      static_folder='static',
                      static_url_path='crud/static'):
        bp = Blueprint(
            self.name.lower(), __name__,
            url_prefix=concat_urls(self.url),
            template_folder=template_folder,
            static_folder=static_folder,
            static_url_path=static_url_path,
        )
        return self.set_urls_to_blueprint(bp)

    def set_urls_to_blueprint(self, blueprint):
        # remove parent url
        absolute_url_len = len(concat_urls(self.absolute_url()))
        for url, name, view in self.iter_items():
            url = url[absolute_url_len:]
            blueprint.add_url_rule(
                url, name.lower(), view, methods=['GET', 'POST'])
        return blueprint
