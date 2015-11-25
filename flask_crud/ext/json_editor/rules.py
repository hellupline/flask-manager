from flask_crud import rules


class JavaScript(rules.Macro):
    def __init__(self, macro_name='JsonField.javascript'):
        super().__init__(macro_name=macro_name)


class JsonField(rules.Macro):
    macro_name = 'JsonField.editor'

    def __init__(self, field, schema_url=None):
        super().__init__(field=field, schema_url=schema_url)


class JsonFieldSet(rules.Nested):
    field_class = JsonField

    def __init__(self, schemas):
        rules = [
            JsonField(field=field, schema_url=schema_url)
            for field, schema_url in schemas.items()
        ]
        rules.insert(0, JavaScript())
        super().__init__(rules=rules)
