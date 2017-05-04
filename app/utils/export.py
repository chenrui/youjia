import os.path
import subprocess32
import uuid
from StringIO import StringIO


class PDFFormat(object):
    def __init__(self, host='127.0.0.1'):
        self._target = None
        self.__host = host
        self._path = '/tmp'

    def export(self, user_id):
        self._target = os.path.join(self._path, 'export-%s.pdf' % str(uuid.uuid4()))
        wkhtmltopdf_url = '"http://' + self.__host + '/export.html#/?user_id=%d" ' % user_id
        wkhtmltopdf_args = '/usr/local/bin/wkhtmltopdf -q --orientation Landscape --javascript-delay 1000 --no-stop-slow-scripts '

        wkhtmltopdf_args = wkhtmltopdf_args + wkhtmltopdf_url
        wkhtmltopdf_args = wkhtmltopdf_args + self._target

        try:
            exit_code = subprocess32.call(wkhtmltopdf_args, shell=True, timeout=20)
            if exit_code != 0 or not os.path.exists(self._target):
                raise
        except Exception:
            return None
        output = StringIO()
        with open(self._target, 'rb') as fd:
            output.write(fd.read())
        output.seek(0)
        os.remove(self._target)
        return output
