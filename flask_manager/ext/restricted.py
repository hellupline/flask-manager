from flask_login import current_user, login_required
from flask_manager import tree


class RestrictedControllerMixin:
    decorators = [login_required]

    def get_roles(self):
        try:
            if current_user.is_superuser():
                return super().get_roles()
        except AttributeError:
            pass
        user_roles = current_user.get_roles()
        roles = super().get_roles()
        return {
            key: list(set(values) & set(user_roles))
            for key, values in roles.items()
        }


class RestrictedIndex(tree.Index):
    decorators = [login_required]

    def endpoints(self):
        if current_user.is_superuser():
            return super().endpoints()
        user_roles = current_user.get_roles()
        endpoints = super().endpoints()
        return self._filter(endpoints, user_roles)

    def _filter(self, menu, user_roles):
        try:
            name, endpoint, children = menu
        except TypeError:
            return
        children = [self._filter(child, user_roles) for child in children]
        if endpoint is None or endpoint.strip('.') in user_roles:
            return name, endpoint, list(filter(None.__ne__, children))
