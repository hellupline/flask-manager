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
    return value.lower().replace(' ', '_')
