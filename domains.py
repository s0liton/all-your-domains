import requests
import xmltodict


class Domains:
    def __init__(self, base_url, api_key):
        self.api_key = api_key
        self.base_url = base_url

        self.conn = requests.Session()

    def ping(self):
        resource = '/service/ping'
        response = self.conn.get(self.base_url + resource)
        response_xml = xmltodict.parse(response)
        return response

    def register(self):
        resource = '/domain/register'
        response = self.conn.get(self.base_url + resource)
        response_xml = xmltodict.parse(response)
        return response

    def search_domain(self, domain, *args, **kwargs):
        resource = '/domain/search.xml'
        url = self.base_url + resource
        params = {'domainname': domain, 'domaintype': "paid"}
        response = self.conn.get(url=url, params=params)
        response_dict = xmltodict.parse(response)
        domain_state = response_dict['freenom']['result']
        return domain_state
