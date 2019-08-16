from flask_restplus import Namespace, Resource, fields
from flask import Flask,jsonify,request,flash,redirect,send_file
import json
import io,base64,os,pdfkit,zipfile,logging


logger = logging.getLogger('documents')
documents = Namespace('Documents', description='Documents conversions and related operations')
optionModel =  documents.model('options' , {'page-size': fields.String(required=True, description='document size ex:A4 or Letter'),
      'margin-top': fields.String(required=True, description='ex:1in or 0.1in'),
      'margin-right': fields.String(required=True, description='ex:1in or 0.1in'),
      'margin-bottom': fields.String(required=True, description='ex:1in or 0.1in'),
      'margin-left': fields.String(required=True, description='ex:1in or 0.1in'),}
)
mainModel = documents.model("RequestObject",{
     'fileData': fields.String(required=True, description='base64 encoded payload data'),  
     'fileType': fields.String(required=True, description='html - base64 encoded html data'),
     'reference': fields.String(required=True, description='reconsiliation reference'), 
     'options' : fields.Nested(optionModel, description='specifiy the page size and margins. default is A4 and 0 margin')

})
@documents.route('/htmltopdf')
class HtmlToPDF(Resource):
            @documents.expect(mainModel, validate=True)
            @documents.doc(responses={
            200: 'Success',
        401: 'Authentication Error',
        403: 'Requested resource unavailable',
        409: 'Conflict, document already exists',
        422: 'Validation Error'
                  })
            def post(self):
                 
                  reqData = json.loads(request.data)
                  
                  returnMime = ''
                  #set pdf options
                  if 'options' not in reqData:
                        reqData['options'] ={
                                          'page-size': 'A4',
                                          'margin-top': '0in',
                                          'margin-right': '0in',
                                          'margin-bottom': '0in',
                                          'margin-left': '0in',
                                          'encoding': "UTF-8",
                                          'no-outline': None,
                                          'disable-smart-shrinking': ''
                                           }
                  else:
                        reqData['options']['encoding'] = 'UTF-8'
                        reqData['options']['no-outline'] = None
                        reqData['options']['disable-smart-shrinking'] = ''

                  #check file types
                  if reqData['fileType'] == 'html':
                        logger.info('start processing HTML data for request:'+reqData['reference'])
                        fileData=base64.decodestring( reqData['fileData'].encode("utf-8")).decode('utf-8', 'ignore')
                        returnMime = 'application/pdf'
                        pdf = pdfkit.from_string(fileData,False,options=reqData['options'])
                        outputData=base64.b64encode(pdf).decode('utf-8', 'ignore')

                  if reqData['fileType'] == 'zip':
                        logger.info('start processing ZIP data for request:'+reqData['reference'])
                        fileData = []
                        returnMime = 'application/zip'
                        outputDatax = io.BytesIO()
                        zipdata = base64.decodestring( reqData['fileData'].encode("utf-8"))
                        zipinside = zipfile.ZipFile(io.BytesIO(zipdata), "r")
                        for file in zipinside.infolist():
                              pdf = pdfkit.from_string(zipinside.read(file).decode('utf-8', 'ignore'),False,options=reqData['options'])
                              basename = os.path.splitext(file.filename)[0]+'.pdf'
                              fileData.append({'data':pdf,'name':basename})
                              
                              
                        zipOut = zipfile.ZipFile(outputDatax, 'w')
                        for filex in fileData:
                              zipOut.writestr(filex['name'],filex['data'])
                        
                        zipOut.close()
                        outputData=base64.b64encode(outputDatax.getvalue()).decode("utf-8")


                  if not fileData:
                        logger.info('incorrect filetype or data request:'+reqData['reference'])
                        return 'invalid file type of empty input',400

                  
                  logger.info('succefully processed request:'+reqData['reference'])
                  return {'data':outputData, 'mimetype':returnMime},200
