from flask_restplus import Namespace, Resource, fields
from flask_jwt_extended import  jwt_required
from flask import Flask,jsonify,request,flash,redirect,send_file
import logging

import io,base64,os,pdfkit

health = Namespace('health', description='Service avaiability and health check')
logger = logging.getLogger('health')
@health.route('/main')
class MainService(Resource):
      @jwt_required
      def post(self):
            return "working",200
      def get(self):
            logger.info('health check get')
            return "working",200
