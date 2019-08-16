from flask_restplus import Api
from apis.Documents import documents
from apis.Health import health
from flask import url_for

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'authorization',
        'description': 'Enter your bearer token in the format **Bearer &lt;token>**'
    }
}

class MyApi(Api):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        scheme = 'http' if '80' in self.base_url else 'https'
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)

api = MyApi(version='1.0', title='USC API',
    description='use to generate PDF files from HTML',
    authorizations=authorizations,
    security='apikey',
    doc='/'
)

api.add_namespace(documents)
api.add_namespace(health)



