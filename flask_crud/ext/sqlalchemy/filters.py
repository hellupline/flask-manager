from itertools import chain

import wtforms
from sqlalchemy import or_

from flask_crud.controller import Filter


class SearchFilter(Filter):
    def __init__(self, columns):
        self.columns = columns

    def filter(self, query, value):
        return query.filter(or_(*[
            column.contains(value) for column in self.columns
        ]))

    def get_form_field(self, key, query):
        return wtforms.TextField()


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
    def __init__(self, column, *joined_tables):
        self.joined_tables = joined_tables
        super().__init__(column=column)

    def join_query(self, query):
        return query.join(*self.joined_tables)

    def filter(self, query, value):
        return super().filter(self.join_query(query), value)

    def get_values(self, query):
        return super().get_values(self.join_query(query))
