import os
import re
from urllib.parse import urlparse, parse_qs, urlencode


EMPTY_ANNOTATION_FILE = ('<?xml version="1.0" encoding="UTF-8" ?>'
                         '<document><annotations></annotations></document>')


def sanitize_identifier(identifier, replacement='-'):
    return re.sub(r'[^\w-]', replacement, identifier)


def get_itemname(infodict):
    # Remove illegal characters in identifier
    return sanitize_identifier('%s-%s' % (
        infodict.get('extractor'),
        infodict.get('display_id', infodict.get('id')),
    ))


def check_is_file_empty(filepath):
    """
    Check whether file is empty or not.

    :param filepath:  Path of a file that will be checked.
    :return:          True if the file empty.
    """
    if os.path.exists(filepath):
        return os.stat(filepath).st_size == 0
    else:
        raise FileNotFoundError("Path '%s' doesn't exist" % filepath)


def strip_ip_from_url(url):
    """
    Strip occurence of IP address as found in path segments like in /ip/1.2.3.4/
    or in an "ip" query-parameter, like in ?ip=1.2.3.4
    """
    u = urlparse(url)
    u = u._replace(path=re.sub(r'/ip/[^/]+', r'/ip/REDACTED', u.path))
    if u.query != '':
        qs = parse_qs(u.query)
        try:
            del (qs['ip'])
            u = u._replace(query=urlencode(qs, True))
        except KeyError:
            pass
    return u.geturl()


def strip_ip_from_meta(meta):
    modified = False
    if 'url' in meta:
        redacted_url = strip_ip_from_url(meta['url'])
        if redacted_url != meta['url']:
            meta['url'] = redacted_url
            modified = True

    for _format in meta['formats']:
        for field in ['manifest_url', 'fragment_base_url', 'url']:
            if field in _format:
                redacted_url = strip_ip_from_url(_format[field])
                if redacted_url != _format[field]:
                    _format[field] = redacted_url
                    modified = True

    return modified, meta
