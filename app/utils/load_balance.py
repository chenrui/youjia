from app.utils.commons import RestHelper


class LoadBalance(RestHelper):
    '''
    Load Balance
    '''
    def __init__(self):
        '''
        Constructor
        '''
        RestHelper.__init__(self, base_url='http://10.4.5.199:5000')
        # super(base_url='http://10.4.5.199:5000')

    def create_vip(self, target, name, ip, port, protocol, application,
                   servers):
        '''Create one vip
        servers: [{
                    "ip": "10.4.5.196",
                    "port": 80,
                    "rs": null
                }]

        '''
        url = '/loadbalance/vips/%s' % name
        request_body = {
                "protocol": protocol,
                "name": name,
                "application": application,
                "vip": ip,
                "vport": port,
                "realserver": servers
            }
        return self._send(target, url, RestHelper.POST,
                          request_body=request_body)

    def update_vip(self, target, name, ip, port, protocol, application,
                   servers):
        '''Updte one vip
        servers: [{
                    "ip": "10.4.5.196",
                    "port": 80,
                    "rs": null
                }]
        '''
        url = '/loadbalance/vips/%s' % name
        request_body = {
                "protocol": protocol,
                "name": name,
                "application": application,
                "vip": ip,
                "vport": port,
                "realserver": servers
            }
        return self._send(target, url, RestHelper.PUT,
                          request_body=request_body)

    def delete_vip(self, target, name):
        '''Delete one vip'''
        url = '/loadbalance/vips/%s' % name

        return self._send(target, url, RestHelper.DELETE)

    def reload_config(self, target):
        '''Reload balance configuration'''
        url = '/loadbalance/config'
        return self._send(target, url, RestHelper.POST)
