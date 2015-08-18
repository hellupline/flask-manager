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
        'rules_list',
        'rules_create',
        'rules_read',
        'rules_update',
        'rules_delete',
    )
    store_context = staticmethod(store_context)

    def __init__(self, form_class, rules, **kwargs):
        self.rules = {'rules': rules}
        for key in self.RULES_NAMES:
            if key in kwargs:
                self.rules[key] = kwargs[key]
        self.form_class = form_class

    def get_rules(self, name='rules'):
        return self.rules.get(name, self.rules['rules'])
