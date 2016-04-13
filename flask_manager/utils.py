import re


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def concat_urls(*urls):
    """Concat Urls
    Args:
        *args: (str)

    Returns:
        str: urls starting and ending with / merged with /
    """
    normalized_urls = filter(bool, [url.strip('/') for url in urls])
    joined_urls = '/'.join(normalized_urls)
    if not joined_urls:
        return '/'
    return '/{}/'.format(joined_urls)


def slugify(value):
    """Simple Slugify."""
    s1 = first_cap_re.sub(r'\1_\2', value)
    s2 = all_cap_re.sub(r'\1_\2', s1)
    return s2.lower().replace(' _', '_').replace(' ', '_')
