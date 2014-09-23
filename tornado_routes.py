# -*- coding: utf-8 -*-
#
# Author: Pavel Reznikov <pashka.reznikov@gmail.com>
#
# Created: 23/01/13
#
# Id: $Id$

from pprint import pformat
import operator
import re
from tornado import web
from tornado.web import URLSpec
import logging
import six


logger = logging.getLogger(__name__)


__ALL__ = ('make_handlers', 'include', 'route', 'routes', )


def handler_repr(cls):
    return re.search("'(.+)'", repr(cls)).groups()[0]


class HandlersList(object):

    def __init__(self, prefix, items):
        self.prefix = prefix
        self.items = items

    def get_handler_name(self, handler, r):
        name = getattr(handler, 'url_name', None)
        if name:
            return name
        if hasattr(handler, 'get_url_name'):
            name = handler.get_url_name(*r)
        if name:
            return name
        if len(r) == 3 and 'url_name' in r[2]:
            name = r[2].pop('url_name')
        if name:
            return name
        return handler_repr(handler)

    def build(self, prefix=None):
        prefix = prefix or self.prefix or ''

        res = []
        for r in self.items:
            route = '/' + '/'.join([prefix.strip('/')] + r[0].strip('/').split('/')).strip('/')

            if isinstance(r[1], HandlersList):
                res += r[1].build(route)
            elif isinstance(r[1], six.string_types):
                m = r[1].split('.')
                ms, m, h = '.'.join(m[:-1]), m[-2], m[-1]
                m = __import__(ms, fromlist=[m], level=0)
                handler = getattr(m, h)[0]
                d = {'name': self.get_handler_name(handler, r)}
                d.update(r[2:])
                res.append(URLSpec(route, handler, **d))
            else:
                handler = r[1:][0]
                d = {'name': self.get_handler_name(handler, r)}
                if len(r) == 3:
                    d['kwargs'] = r[2]
                res.append(URLSpec(route, handler, **d))

        return res


def make_handlers(prefix, *args):
    res = tuple(HandlersList(prefix, args).build())

    rr = [(x.regex.pattern, x.handler_class, x.kwargs, x.name) for x in res]
    logger.debug('\n' + pformat(sorted(rr, key=operator.itemgetter(0)), width=200))

    return res


def include(module):
    def load_module(m):
        m = m.split('.')
        ms, m = '.'.join(m), m[-1]
        m = __import__(ms, fromlist=[m], level=0)
        return m

    if isinstance(module, six.string_types):
        module = load_module(module)

    routes = []
    for member in dir(module):
        member = getattr(module, member)
        if isinstance(member, type) and issubclass(member, web.RequestHandler) and hasattr(member, 'routes'):
            i = 1
            for route_path, route_params in member.routes:
                route_path.strip('/')
                if not route_params:
                    route_params = {}
                if 'url_name' not in route_params:
                    route_params['url_name'] = '%s~%d' % (handler_repr(member), i)
                routes.append((route_path, member, route_params))
                i += 1
        elif isinstance(member, type) and issubclass(member, web.RequestHandler) and hasattr(member, 'route_path'):
            route_path, route_params = member.route_path, member.route_params

            route_path.strip('/')
            if route_params:
                routes.append((route_path, member, route_params))
            else:
                routes.append((route_path, member))
        elif isinstance(member, type) and issubclass(member, web.RequestHandler) and hasattr(member, 'rest_route_path'):
            route_path, route_params = member.rest_route_path, member.route_params

            route_path.strip('/')
            if route_params:
                routes.append((route_path, member, route_params))
                routes.append((route_path + r'/([0-9]+)', member, route_params))
            else:
                routes.append((route_path, member))
                routes.append((route_path + r'/([0-9]+)', member))
    return HandlersList(None, routes)


route_classes = {}


def route(path, params=None, name=None):
    params = params or {}

    def decorator(cls):
        if repr(cls) in route_classes:
            raise Exception('Cannot bind route "%s" to %s. It already has route to "%s".' %
                            (path, cls, route_classes[repr(cls)]))
        route_classes[repr(cls)] = path
        cls.route_path = path
        cls.route_params = params
        url_name = params.pop('url_name', name)
        cls.url_name = url_name
        return cls
    return decorator


def routes(*routes):
    def decorator(cls):
        cls.routes = routes
        return cls
    return decorator
