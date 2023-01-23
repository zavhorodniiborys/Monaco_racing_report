import json
from collections import OrderedDict
from dict2xml import dict2xml
from flask import abort, Blueprint, make_response
from flask_restful import Resource, Api, reqparse

from Flask_app.racing_data import ReportDB


api_endpoints = Blueprint('api_endpoints', __name__)
api = Api(api_endpoints)

parser = reqparse.RequestParser()
parser.add_argument('format', location='args',
                    choices=('json', 'xml'), help='API format (json/xml)')
parser.add_argument('order', location='args',
                    choices=('asc', 'desc'), help='Result order (asc/desc)')
parser.add_argument('driver_id', location='args', help="Driver's id.")


class ReportBasic:
    @staticmethod
    def create_response(api_format, response_data):
        if api_format == 'json':
            response = make_response(json.dumps(response_data))
            response.headers['Content-Type'] = 'application/json'
            return response

        elif api_format == 'xml':
            response = make_response(dict2xml(OrderedDict(response_data), wrap='results'))
            response.headers['Content-Type'] = 'application/xml'
            return response


class ReportApi(Resource, ReportBasic):
    def get(self):
        """
    This is the Monaco racing report API
    Call this api and get it's result
    ---
    tags:
      - Monaco racing report API
    parameters:
      - name: format
        in: query
        type: string
        required: true
        description: API format (json/xml)
    responses:
      500:
        description: Wrong API format
      200:
        description: Api in a chosen format
        schema:
          id: Output
          properties:
            abbr:
              type: object
              description: Driver abbreviation
              minLength: 3
              maxLength: 3
              properties:
                  name:
                    description: Driver's name
                    type: string
                  org:
                    description: Driver's organization
                    type: string
                  lap_time:
                    description: Driver's best lap time
                    type: string
              required:
                - name
                - org
                - lap_time

    """
        args = parser.parse_args()
        order = args['order']
        api_format = args['format']

        report = ReportDB.get_report(order)

        response = self.create_response(api_format, report)
        return response


class DriverReportAPI(Resource, ReportBasic):
    def get(self):
        """
            This is the Monaco driver racing report API
            Call this api passing a driver name and get his result
            ---
            tags:
              - Monaco driver racing report API
            parameters:
              - name: format
                in: query
                type: string
                required: true
                description: API format (json/xml)

              - name: driver_id
                in: query
                type: string
                required: true
                description: Driver's id (abbreviation with 3 capital letters)
            responses:
              500:
                description: Wrong Driver id
              200:
                description: Api in a chosen format
                schema:
                  id: Output
                  properties:
                    name:
                      description: Driver's name
                      type: string
                    org:
                      description: Driver's organization
                      type: string
                    lap_time:
                      description: Driver's best lap time
                      type: string
                  required:
                    - name
                    - org
                    - lap_time

            """
        args = parser.parse_args()
        driver_id = args['driver_id']
        api_format = args['format']

        report = ReportDB.get_report()

        if driver_id in report.keys():
            driver_result = report[driver_id]
        else:
            return 'Wrong driver id.', 500

        response = self.create_response(api_format, driver_result)
        return response


api.add_resource(ReportApi, '/api/v1/report/')
api.add_resource(DriverReportAPI, '/api/v1/report/driver/')
