from flask.ext.restful import abort
import httplib
import requests
from urlparse import urljoin
from urllib import quote, urlencode
import logging
from app import errorcode


class RestHelper(object):
    '''
    Restful API Client Helper
    '''
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'

    def _send2(self, url, method_name, request_headers=None,
               request_body=None):
        _request_headers = {'content-type': 'application/json'}
        if request_headers is not None:
            _request_headers.update(request_headers)
        method = getattr(requests, method_name)
        response = method(
                    urljoin(self.base_url, quote(url)),
                    headers=_request_headers,
                    json=request_body
                )

        if method_name in ['get', 'put', 'delete']:
            if response.status_code != 200:
                logging.error('%s %s: %s (Bad response status code)\n%s' % (
                                    method_name.upper(),
                                    urljoin(self.base_url, quote(url)),
                                    response.status_code,
                                    response.request.body)
                              )
                logging.error(response.content)
                raise ValueError('Bad response status code: %s' %
                                 response.status_code)
        elif method_name in ['post']:
            if response.status_code != 201:
                logging.error('%s %s: : %s (Bad response status code)\n%s' % (
                                    method_name.upper(),
                                    urljoin(self.base_url, quote(url)),
                                    response.status_code,
                                    response.request.body)
                              )
                logging.error(response.content)
                raise ValueError('Bad response status code: %s' %
                                 response.status_code)

        return response.json()

    def _send(self, target, url, method_name, request_headers=None,
              request_body=None, return_reason=True):
        '''send rest request'''
        _request_headers = {'content-type': 'application/json'}
        if request_headers is not None:
            _request_headers.update(request_headers)
        method = getattr(requests, method_name)
        try:
            response = method(
                    urljoin(self.base_url,
                            quote(url) + '?' + urlencode({'target': target})),
                    headers=_request_headers,
                    json=request_body
                )
        except Exception:
            abort(httplib.INTERNAL_SERVER_ERROR,
                  status_code=errorcode.REQUEST_ERROR,
                  message=errorcode.ErrorMsg[errorcode.REQUEST_ERROR])

        if method_name in ['get', 'put', 'delete']:
            if response.status_code != 200:
                logging.error('%s %s: %s (Bad response status code)\n%s' % (
                                    method_name.upper(),
                                    urljoin(self.base_url, quote(url)),
                                    response.status_code,
                                    response.request.body)
                              )
                logging.error(response.content)
                data = response.json()
                if return_reason:
                    abort(httplib.BAD_REQUEST,
                          status_code=data['code'], message=data['message'])
                raise ValueError('Bad response status code: %s' %
                                 response.status_code)
        elif method_name in ['post']:
            if response.status_code != 201:
                logging.error('%s %s: : %s (Bad response status code)\n%s' % (
                                    method_name.upper(),
                                    urljoin(self.base_url, quote(url)),
                                    response.status_code,
                                    response.request.body)
                              )
                logging.error(response.content)
                data = response.json()
                if return_reason:
                    if return_reason:
                        abort(httplib.BAD_REQUEST,
                              status=data['code'], message=data['message'])
                raise ValueError('Bad response status code: %s' %
                                 response.status_code)

        return response.json()

    def __init__(self, base_url=None):
        '''
        Constructor
        '''
        self.base_url = base_url
