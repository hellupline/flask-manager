from jinja2 import Markup
from .display import get_render_ctx


class RuleMixin:
    def __call__(self, obj, extra_kwargs=None):
        raise NotImplementedError


# simple text
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


# jinja2 macros
class Macro(RuleMixin):
    def __init__(self, macro_name, **kwargs):
        self.macro_name = macro_name
        self.default_kwargs = kwargs

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
        opts = self.default_kwargs.copy()
        opts.update(kwargs)
        return macro(obj, **opts)


class Container(Macro):
    def __init__(self, macro_name, child_rule, **kwargs):
        self.child_rule = child_rule
        super().__init__(macro_name, **kwargs)

    def __call__(self, obj, **kwargs):
        def caller():
            return get_render_ctx().call(self.child_rule, obj)

        return super().__call__(obj, caller=caller)


class Form(Macro):
    def __init__(self, macro_name='utils.render_form'):
        super().__init__(macro_name=macro_name)


class Header(Macro):
    def __init__(self, text, macro_name='utils.render_header'):
        super().__init__(macro_name=macro_name, text=text)


class Field(Macro):
    def __init__(self, field_name, macro_name='utils.render_field'):
        self.field_name = field_name
        super().__init__(macro_name=macro_name, field_name=field_name)

    def __call__(self, obj, **kwargs):
        field_value = getattr(obj, self.field_name)
        return super().__call__(obj, field_value=field_value)


class CellField(Field):
    def __init__(self, field_name, macro_name='table.field'):
        super().__init__(field_name=field_name, macro_name=macro_name)


class FormField(Field):
    def __init__(self, field_name, macro_name='utils.render_form_field'):
        super().__init__(field_name=field_name, macro_name=macro_name)


# nested
class NestedRule(RuleMixin):
    def __init__(self, rules):
        # avoid generator consumption
        self.rules = list(rules)

    def __iter__(self):
        return iter(self.rules)

    def __call__(self, obj, **kwargs):
        return Markup(''.join(rule(obj) for rule in self.rules))


class FieldSet(NestedRule):
    def __init__(self, fields, header=None, field_class=Field):
        rules = [field_class(field) for field in fields]
        if header is not None:
            rules.insert(0, Header(header))
        super().__init__(rules=rules)


class ColumnSet(FieldSet):
    def __init__(self, columns, field_class=CellField):
        self.columns = columns
        super().__init__(fields=columns, field_class=field_class)


class FormFieldSet(FieldSet):
    def __init__(self, fields, header=None, field_class=FormField):
        super().__init__(fields=fields, header=header, field_class=field_class)
