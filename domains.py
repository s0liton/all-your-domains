import requests
import xmltodict


class Domains:
    def __init__(self, config, base_url, api_key):
        self.config = config
        self.api_key = api_key
        self.base_url = base_url

        self.conn = requests.Session()

    def ping(self):
        resource = '/service/ping'
        response = self.conn.get(self.base_url + resource)
        response_xml = xmltodict.parse(response)
        return response_xml

    def register(self, domain, period_length, nameservers):
        request_body = {"domain": domain, "domaintype": "FREE", "period" : period_length, "nameservers" : nameservers}
        resource = '/domain/register'
        response = self.conn.post(self.base_url + resource, data=request_body)
        response_xml = xmltodict.parse(response)
        return response_xml

    def search_domain(self, domain, *args, **kwargs):
        resource = '/domain/search.xml'
        url = self.base_url + resource
        params = {'domainname': domain, 'domaintype': "free"}
        response = self.conn.get(url=url, params=params)
        domain_state = xmltodict.parse(response)
        if domain_state["freenom"]["result"] == "DOMAIN AVAILABLE":
            return True
        else:
            return False

    def request_domain(self, domain):
        try:
            if self.search_domain(domain):
                self.register(domain)
        except ConnectionError:
            print("Could not request domain. Is it taken?")
