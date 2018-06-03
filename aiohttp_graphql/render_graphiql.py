import os
import json
import re

from aiohttp import web


GRAPHIQL_VERSION = '0.11.11'
MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(MAIN_DIR, 'static/index.jinja2')


with open(TEMPLATE_PATH) as template_file:
    TEMPLATE = template_file.read()


def escape_js_value(value):
    quotation = False
    if value.startswith('"') and value.endswith('"'):
        quotation = True
        value = value[1:len(value)-1]

    value = value.replace('\\\\n', '\\\\\\n').replace('\\n', '\\\\n')
    if quotation:
        value = '"' + value.replace('\\\\"', '"').replace('\"', '\\\"') + '"'

    return value


def process_var(template, name, value, jsonify=False):
    pattern = r'{{\s*' + name + r'(\s*|[^}]+)*\s*}}'
    if jsonify and value not in ['null', 'undefined']:
        value = json.dumps(value)
        value = escape_js_value(value)

    return re.sub(pattern, value, template)


def simple_renderer(template, **values):
    replace = ['graphiql_version', 'subscriptions', ]
    replace_jsonify = ['query', 'result', 'variables', 'operation_name', ]

    for rep in replace:
        template = process_var(template, rep, values.get(rep, ''))

    for rep in replace_jsonify:
        template = process_var(template, rep, values.get(rep, ''), True)

    return template


async def render_graphiql(
        jinja_env=None,
        graphiql_version=None,
        graphiql_template=None,
        params=None,
        result=None,
        subscriptions=None,
    ):
    graphiql_version = graphiql_version or GRAPHIQL_VERSION
    template = graphiql_template or TEMPLATE
    template_vars = {
        'graphiql_version': graphiql_version,
        'query': params and params.query,
        'variables': params and params.variables,
        'operation_name': params and params.operation_name,
        'result': result,
        'subscriptions': subscriptions or '',
    }

    if jinja_env:
        template = jinja_env.from_string(template)
        if jinja_env.is_async:
            source = await template.render_async(**template_vars)
        else:
            source = template.render(**template_vars)
    else:
        source = simple_renderer(template, **template_vars)

    return web.Response(text=source, content_type='text/html')
