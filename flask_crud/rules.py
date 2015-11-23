from jinja2 import Markup
from .display import get_render_ctx


class RuleMixin:
    def __call__(self, obj, extra_kwargs=None):
        raise NotImplementedError


# Simple Text
class Text(RuleMixin):
    def __init__(self, text, escape=True):
        self.text = text
        self.escape = escape

    def __call__(self, obj, **kwargs):
        if self.escape:
            return self.text
        return Markup(self.text)


class HTML(Text):
    def __init__(self, html):
        super().__init__(text=html, escape=False)


class Nested(RuleMixin):
    """Nested([DataField(...), DataField(...)])"""

    def __init__(self, rules):
        self.rules = rules

    def __iter__(self):
        return iter(self.rules)

    def __call__(self, obj, **kwargs):
        joined_rules = ''.join(rule(obj) for rule in self.rules)
        return Markup(joined_rules)


class Macro(RuleMixin):
    def __init__(self, macro_name, **kwargs):
        self.macro_name = macro_name
        self.kwargs = kwargs

    def _resolve(self):
        parts = self.macro_name.split('.')
        macro = get_render_ctx().resolve(parts[0])
        if not macro:
            raise ValueError('Cannot find macro {}.'.format(self.macro_name))
        for part in parts[1:]:
            macro = getattr(macro, part)
        return macro

    def __call__(self, obj, **kwargs):
        macro = self._resolve()
        opts = self.kwargs.copy()
        opts.update(kwargs)
        return macro(obj, **opts)


class Container(Macro):
    """Container(Macro('my_macro'), 'h1_tag_macro')()"""

    def __init__(self, child_rule, macro_name, **kwargs):
        super().__init__(macro_name, **kwargs)
        self.child_rule = child_rule

    def __call__(self, obj, **kwargs):
        def caller():
            return get_render_ctx().call(self.child_rule, obj)
        return super().__call__(obj, caller=caller, **kwargs)


# Macros
class Header(Macro):
    """Header('Title')()"""

    def __init__(self, text, macro_name='Utils.header'):
        super().__init__(macro_name=macro_name, text=text)


class SimpleForm(Macro):
    """SimpleForm()(Form())"""

    def __init__(self, macro_name='Forms.simple_form_render'):
        super().__init__(macro_name=macro_name)


# Crud Macros
class DataField(Macro):
    """Render a field in Read/Delete."""

    def __init__(self, field_name, macro_name='Data.render_field'):
        super().__init__(macro_name=macro_name)
        self.field_name = field_name

    def __call__(self, obj):
        field_value = getattr(obj, self.field_name)
        return super().__call__(obj, name=self.field_name, value=field_value)


class CellField(DataField):
    """Render a field in List."""

    def __init__(self, field_name, macro_name='Table.render_field'):
        super().__init__(field_name=field_name, macro_name=macro_name)


class FormField(DataField):
    """Render a form field in Create/Update."""

    def __init__(self, field_name, macro_name='Forms.render_field'):
        super().__init__(field_name=field_name, macro_name=macro_name)


# Containers
class DataFieldSet(Container):
    """DataFieldSet([name for name in model])(Model())"""

    def __init__(self, columns, header=None, macro_name='Data.render_data',
                 field_class=DataField):
        self.columns = columns
        self.rules = [field_class(column) for column in columns]
        if header is not None:
            self.rules.insert(0, Header(header))
        super().__init__(child_rule=Nested(self.rules), macro_name=macro_name)


class ColumnSet(DataFieldSet):
    def __init__(self, columns, header=None, macro_name='Table.render_row',
                 field_class=CellField):
        super().__init__(columns=columns, header=header, macro_name=macro_name,
                         field_class=field_class)


class FormFieldSet(DataFieldSet):
    def __init__(self, columns, header=None, macro_name='Forms.render_form',
                 field_class=FormField):
        super().__init__(columns=columns, header=header, macro_name=macro_name,
                         field_class=field_class)
