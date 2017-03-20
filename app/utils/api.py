#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib
import json
import decimal
from jinja2 import Template
from flask import request, Response
import flask_restful as restful
from flask_restful import reqparse, abort
from werkzeug.datastructures import FileStorage
from werkzeug import exceptions
from app import errorcode
from .validate import IntParam, ParamValidation


class RestfulApi(restful.Api):
    def add_resources(self, resources):
        for resource in resources:
            if isinstance(resource[0], str):
                self.add_resource(*resource[1:], endpoint=resource[0])
            else:
                if len(resource) == 1:
                    resource.extend(resource[0].urls)
                apply(self.add_resource, resource)

    def _register_view(self, app, resource, *urls, **kwargs):
        endpoint = kwargs.pop('endpoint', resource.__name__.lower() + self.prefix)
        super(RestfulApi, self)._register_view(app, resource, *urls, endpoint=endpoint, **kwargs)


class Argument(reqparse.Argument):
    def __init__(self, name, default=None, dest=None, required=False,
                 ignore=False, type=reqparse.text_type, location=('json', 'values',),
                 choices=(), action='store', help=None, operators=('=',),
                 case_sensitive=True, store_missing=True, trim=False,
                 nullable=True, **kwargs):
        reqparse.Argument.__init__(self, name, default, dest, required, ignore,
                                   type, location, choices, action, help, operators,
                                   case_sensitive, store_missing, trim, nullable)
        self.args = kwargs if kwargs else {}

    def convert(self, value, op):
        # Don't cast None
        if value is None:
            if self.nullable:
                return None
            else:
                raise ValueError('Must not be null!')

        # and check if we're expecting a filestorage and haven't overridden `type`
        # (required because the below instantiation isn't valid for FileStorage)
        elif isinstance(value, FileStorage) and self.type == FileStorage:
            return value

        try:
            return self.type(value, self.name, op)
        except TypeError:
            try:
                if self.type is decimal.Decimal:
                    return self.type(str(value), self.name)
                elif hasattr(self.type, '__self__') and issubclass(self.type.__self__, ParamValidation):
                    return self.type(value, self.name, self.args)
                else:
                    return self.type(value, self.name)
            except TypeError:
                return self.type(value)


class RequestParser(reqparse.RequestParser):
    def __init__(self, *args, **kwargs):
        reqparse.RequestParser.__init__(self, *args, **kwargs)
        self.argument_class = Argument

    def parse_args(self, req=None, strict=False):
        if req is None:
            req = request
        namespace = self.namespace_class()
        # A record of arguments not yet parsed; as each is found
        # among self.args, it will be popped out
        req.unparsed_arguments = dict(self.argument_class('').source(req)) if strict else {}
        errors = {}
        for arg in self.args:
            value, found = arg.parse(req, True)
            if isinstance(value, ValueError):
                errors.update(found)
                found = None
            if found or arg.store_missing:
                namespace[arg.dest or arg.name] = value
        if errors:
            print errors
            abort(400, message=u'参数错误(%s)' % errors.keys()[0], status_code=errorcode.BAD_REQUEST)

        if strict and req.unparsed_arguments:
            raise exceptions.BadRequest('Unknown arguments: %s'
                                        % ', '.join(req.unparsed_arguments.keys()))
        return namespace


class BaseResource(restful.Resource):
    default_count = 200

    def options(self, *args, **kwargs):
        headers = {'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                   'Access-Control-Allow-Headers': 'x-requested-with,content-type',
                   }
        return Response(headers=headers)

    def get_parser(self):
        self._parser = parser = RequestParser()
        return parser

    def get_param(self, name, default=None, args=None):
        args = args or self._parser.parse_args()
        value = args.get(name, default)
        return value

    def get_params(self, *names, **kwargs):
        args = kwargs.pop('args', None) or self._parser.parse_args()
        return [kwargs.pop(name) if name in kwargs else
                self.get_param(name, None, args) for name in names]

    def add_pagination_args(self, parser=None):
        parser = parser or self.get_parser()
        parser.add_argument(
            'page', type=IntParam.check, required=False, location='args', default=1, min=1)
        parser.add_argument(
            'page_size', type=IntParam.check, required=False, location='args',
            default=self.default_count, min=1, max=2000)
        return parser

    @classmethod
    def abort(cls, http_status_code, status_code, **kwargs):
        info = kwargs.get('_info', {})
        temp = Template(errorcode.ErrorMsg[status_code])
        msg = temp.render(**kwargs)
        abort(http_status_code, status_code=status_code, message=msg, **info)

    @classmethod
    def bad_request(cls, status_code=httplib.BAD_REQUEST, **kwargs):
        '''Return bad request with status code and message'''
        cls.abort(httplib.BAD_REQUEST, status_code, **kwargs)

    @classmethod
    def not_found(cls, **kwargs):
        cls.abort(httplib.NOT_FOUND, errorcode.NOT_FOUND, **kwargs)

    @classmethod
    def unauthorized(cls, status_code=errorcode.UNAUTHORIZED, **kwargs):
        cls.abort(httplib.UNAUTHORIZED, status_code, **kwargs)

    def created(self, message, **kwargs):
        '''Return created message'''
        info = {'status_code': httplib.CREATED,
                'message': '%s' % message
                }
        if kwargs:
            info.update({'extra': kwargs})
        return info, httplib.CREATED

    def ok(self, message, **kwargs):
        info = {'status_code': httplib.OK,
                'message': '%s' % message
                }
        if kwargs:
            info.update({'extra': kwargs})
        return info, httplib.OK

    @classmethod
    def server_error(cls, status_code=httplib.INTERNAL_SERVER_ERROR, **kwargs):
        cls.abort(httplib.INTERNAL_SERVER_ERROR, status_code, **kwargs)

    @classmethod
    def not_login(cls, status_code=errorcode.NOT_LOGINED, **kwargs):
        cls.abort(httplib.UNAUTHORIZED, status_code, **kwargs)

    def build_post(self, args, data):
        def get_data(cache=True, as_text=False, parse_form_data=False):
            return json.dumps(data)
        request.environ['CONTENT_TYPE'] = 'application/json'
        if args:
            request.args = request.parameter_storage_class(args)
        else:
            request.args = None
        request.get_data = get_data
        try:
            delattr(request, '_cached_json')
            delattr(request, '_cached_data')
        except:
            pass


