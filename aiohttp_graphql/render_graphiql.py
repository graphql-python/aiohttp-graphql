import json
import re

from aiohttp import web

GRAPHIQL_VERSION = "0.17.5"

TEMPLATE = """<!--
The request to this GraphQL server provided the header "Accept: text/html"
and as a result has been presented GraphiQL - an in-browser IDE for
exploring GraphQL.
If you wish to receive JSON, provide the header "Accept: application/json" or
add "&raw" to the end of the URL within a browser.
-->
<!DOCTYPE html>
<html>
<head>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      overflow: hidden;
      width: 100%;
    }
  </style>
  <meta name="referrer" content="no-referrer">
  <link href="//cdn.jsdelivr.net/npm/graphiql@{{graphiql_version}}/graphiql.css" rel="stylesheet" />
  <script src="//cdn.jsdelivr.net/gh/github/fetch@3.0.0/fetch.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/react@16.12.0/umd/react.production.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/react-dom@16.12.0/umd/react-dom.production.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/graphiql@{{graphiql_version}}/graphiql.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/subscriptions-transport-ws@0.9.16/browser/client.js"></script>
  <script src="//cdn.jsdelivr.net//npm/graphiql-subscriptions-fetcher@0.0.2/browser/client.js"></script>
</head>
<body>
  <script>
    // Collect the URL parameters
    var parameters = {};
    window.location.search.substr(1).split('&').forEach(function (entry) {
      var eq = entry.indexOf('=');
      if (eq >= 0) {
        parameters[decodeURIComponent(entry.slice(0, eq))] =
          decodeURIComponent(entry.slice(eq + 1));
      }
    });

    // Produce a Location query string from a parameter object.
    function locationQuery(params) {
      return '?' + Object.keys(params).map(function (key) {
        return encodeURIComponent(key) + '=' +
          encodeURIComponent(params[key]);
      }).join('&');
    }

    // Derive a fetch URL from the current URL, sans the GraphQL parameters.
    var graphqlParamNames = {
      query: true,
      variables: true,
      operationName: true
    };

    var otherParams = {};
    for (var k in parameters) {
      if (parameters.hasOwnProperty(k) && graphqlParamNames[k] !== true) {
        otherParams[k] = parameters[k];
      }
    }

    var subscriptionsFetcher;
    if ('{{subscriptions}}') {
      const subscriptionsClient = new SubscriptionsTransportWs.SubscriptionClient(
        '{{ subscriptions }}',
        {reconnect: true}
      );

      subscriptionsFetcher = GraphiQLSubscriptionsFetcher.graphQLFetcher(
        subscriptionsClient,
        graphQLFetcher
      );
    }

    var fetchURL = locationQuery(otherParams);

    // Defines a GraphQL fetcher using the fetch API.
    function graphQLFetcher(graphQLParams) {
      return fetch(fetchURL, {
        method: 'post',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(graphQLParams),
        credentials: 'include',
      }).then(function (response) {
        return response.text();
      }).then(function (responseBody) {
        try {
          return JSON.parse(responseBody);
        } catch (error) {
          return responseBody;
        }
      });
    }

    // When the query and variables string is edited, update the URL bar so
    // that it can be easily shared.
    function onEditQuery(newQuery) {
      parameters.query = newQuery;
      updateURL();
    }

    function onEditVariables(newVariables) {
      parameters.variables = newVariables;
      updateURL();
    }

    function onEditOperationName(newOperationName) {
      parameters.operationName = newOperationName;
      updateURL();
    }

    function updateURL() {
      history.replaceState(null, null, locationQuery(parameters));
    }

    // Render <GraphiQL /> into the body.
    ReactDOM.render(
      React.createElement(GraphiQL, {
        fetcher: subscriptionsFetcher || graphQLFetcher,
        onEditQuery: onEditQuery,
        onEditVariables: onEditVariables,
        onEditOperationName: onEditOperationName,
        query: {{query|tojson}},
        response: {{result|tojson}},
        variables: {{variables|tojson}},
        operationName: {{operation_name|tojson}},
      }),
      document.body
    );
  </script>
</body>
</html>"""


def escape_js_value(value):
    quotation = False
    if value.startswith('"') and value.endswith('"'):
        quotation = True
        value = value[1:-1]

    value = value.replace("\\\\n", "\\\\\\n").replace("\\n", "\\\\n")
    if quotation:
        value = '"' + value.replace('\\\\"', '"').replace('"', '\\"') + '"'

    return value


def process_var(template, name, value, jsonify=False):
    pattern = r"{{\s*" + name + r"(\s*|[^}]+)*\s*}}"
    if jsonify and value not in ["null", "undefined"]:
        value = json.dumps(value)
        value = escape_js_value(value)

    return re.sub(pattern, value, template)


def simple_renderer(template, **values):
    replace = ["graphiql_version", "subscriptions"]
    replace_jsonify = ["query", "result", "variables", "operation_name"]

    for rep in replace:
        template = process_var(template, rep, values.get(rep, ""))

    for rep in replace_jsonify:
        template = process_var(template, rep, values.get(rep, ""), True)

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
        "graphiql_version": graphiql_version,
        "query": params and params.query,
        "variables": params and params.variables,
        "operation_name": params and params.operation_name,
        "result": result,
        "subscriptions": subscriptions or "",
    }

    if jinja_env:
        template = jinja_env.from_string(template)
        if jinja_env.is_async:
            source = await template.render_async(**template_vars)
        else:
            source = template.render(**template_vars)
    else:
        source = simple_renderer(template, **template_vars)

    return web.Response(text=source, content_type="text/html")
