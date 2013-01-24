Tornado routes
==============

URL routings for tornado web server.

Usage examples:

```python
from tornado import web
from tornado_routes import make_handlers


URL_PREFIX = ''

app = web.Application(make_handlers(URL_PREFIX,
    (r'/(robots\.txt|favicon\.ico)', web.StaticFileHandler, {"path": os.path.join(ROOT, 'static')}),
    (r'/api', include('api')),
    (r'/', include('views')),
))
```

`api.py`:

```python
from tornado import web
from tornado_routes import route

@route('foo')
class FooHandler(web.RequestHandler):
    pass
```

`views.py`:

```python
from tornado import web
from tornado_routes import route

@route('', name='index')
class IndexHandler(web.RequestHandler):
    pass
```

Your could use view names in your templates:

```html
<a href="{{ reverse_url('index') }}">Index</a>
<a href="{{ reverse_url('api.FooHandler') }}">Foo link</a>
```
