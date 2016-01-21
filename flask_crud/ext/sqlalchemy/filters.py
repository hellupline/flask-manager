from itertools import chain

import wtforms
from sqlalchemy import or_

from flask_crud.controller import Filter


class SearchFilter(Filter):
    def __init__(self, columns):
        self.columns = columns

    def filter(self, query, value):
        clauses = [column.contains(value) for column in self.columns]
        return query.filter(or_(*clauses))

    def get_form_field(self, key, query):
        return wtforms.TextField()


class ColumnFilter(Filter):
    def __init__(self, column):
        self.column = column

    def filter(self, query, value):
        return query.filter(self.column == value)

    def get_values(self, query):
        # values = query.with_entities(self.column).distinct()
        values = query.session.query(self.column).distinct()
        return set(chain.from_iterable(values))

    def get_form_field(self, key, query):
        choices = [('', 'All')]
        for value in self.get_values(query):
            title = str(value).capitalize()
            if isinstance(value, bool):
                value = str(int(value))
            choices.append((value, title))
        return wtforms.SelectField(key.title(), choices=choices)


class JoinColumnFilter(ColumnFilter):
    def __init__(self, column, joined_tables):
        self.joined_tables = joined_tables
        super().__init__(column=column)

    def joined_query(self, query):
        return query.join(*self.joined_tables)

    def filter(self, query, value):
        return super().filter(self.joined_query(query), value)
