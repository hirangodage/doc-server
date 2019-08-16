from flask_restplus import Api
from apis.Documents import documents
from apis.Health import health


api = Api(version='1.0', title='USC API',
    description='use to generate PDF files from HTML',
)

api.add_namespace(documents)
api.add_namespace(health)



