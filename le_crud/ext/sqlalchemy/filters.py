from itertools import chain

import wtforms

from le_crud.controller import Filter


class ColumnFilter(Filter):
    def __init__(self, column):
        self.column = column

    def filter(self, query, value):
        return query.filter(self.column == value)

    def get_values(self, query):
        values = query.with_entities(self.column)
        return set(chain.from_iterable(values))

    def get_form_field(self, key, query):
        choices = [
            (value, str(value).title())
            for value in self.get_values(query)
        ]
        choices.insert(0, ('', ''))
        return wtforms.SelectField(key.title(), choices=choices)


class JoinColumnFilter(ColumnFilter):
    def __init__(self, column, joined_table):
        self.joined_table = joined_table
        super().__init__(column=column)

    def join_query(self, query):
        return query.join(self.joined_table)

    def filter(self, query, value):
        return super().filter(self.join_query(query), value)

    def get_values(self, query):
        return super().get_values(self.join_query(query))
