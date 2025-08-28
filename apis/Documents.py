from flask_restx import Namespace, Resource, fields
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
                        try:
                            fileData = base64.b64decode(reqData['fileData']).decode('utf-8', 'ignore')
                            returnMime = 'application/pdf'
                            pdf = pdfkit.from_string(fileData, False, options=reqData['options'])
                            outputData = base64.b64encode(pdf).decode('utf-8', 'ignore')
                        except Exception as e:
                            logger.error(f"Error processing HTML for request {reqData['reference']}: {e}")
                            return "Error generating PDF from HTML", 500

                  if reqData['fileType'] == 'zip':
                        logger.info('start processing ZIP data for request:'+reqData['reference'])
                        fileData = []
                        returnMime = 'application/zip'
                        outputDatax = io.BytesIO()
                        try:
                            zipdata = base64.b64decode(reqData['fileData'])
                            with zipfile.ZipFile(io.BytesIO(zipdata), "r") as zipinside:
                                for file in zipinside.infolist():
                                    try:
                                        pdf = pdfkit.from_string(zipinside.read(file).decode('utf-8', 'ignore'), False, options=reqData['options'])
                                        basename = os.path.splitext(file.filename)[0] + '.pdf'
                                        fileData.append({'data': pdf, 'name': basename})
                                    except Exception as e:
                                        logger.error(f"Error converting file {file.filename} in zip for request {reqData['reference']}: {e}")
                                        # Optionally, skip this file and continue with others
                                        continue

                            with zipfile.ZipFile(outputDatax, 'w') as zipOut:
                                for filex in fileData:
                                    zipOut.writestr(filex['name'], filex['data'])

                            outputData = base64.b64encode(outputDatax.getvalue()).decode("utf-8")
                        except zipfile.BadZipFile:
                            logger.error(f"Bad zip file for request {reqData['reference']}")
                            return "Bad zip file", 400
                        except Exception as e:
                            logger.error(f"Error processing zip for request {reqData['reference']}: {e}")
                            return "Error processing zip file", 500


                  if not fileData:
                        logger.info('incorrect filetype or data request:'+reqData['reference'])
                        return 'invalid file type of empty input',400

                  
                  logger.info('succefully processed request:'+reqData['reference'])
                  return {'data':outputData, 'mimetype':returnMime},200
