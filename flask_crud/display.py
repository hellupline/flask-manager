from jinja2 import contextfunction
from flask import g


@contextfunction
def store_context(context):
    """
        Resolve current Jinja2 context and store it for general consumption.
    """
    g.le_admin_render_ctx = context


def get_render_ctx():
    """
        Get view template context.
    """
    return g.le_admin_render_ctx


class Display:
    RULES_NAMES = (
        'list',
        'create',
        'read',
        'update',
        'delete',
    )
    store_context = staticmethod(store_context)

    def __init__(self, **kwargs):
        self.rules = {
            key: kwargs[key]
            for key in self.RULES_NAMES
            if key in kwargs
        }

    def get_rules(self, name):
        return self.rules.get(name)
