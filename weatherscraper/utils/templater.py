__author__ = 'riot'

from mako.lookup import TemplateLookup
from mako.exceptions import TemplateLookupException

class SimpleTemplater(object):
    def __init__(self, template):
        self.template = template

    def render(self, input):
        return self.template.format(**input)

class MakoTemplater(object):

    templatestore = TemplateLookup(directories=['/home/riot/src/c-weatherscraper/weatherscraper/templates'],
                                   strict_undefined=True,
                                   input_encoding='UTF8',
                                   )

    def __init__(self, template):
        try:
            self.template = self.templatestore.get_template(template + ".html")
        except TemplateLookupException:
            print("Can't find template '%s.html' in templatefolder." % template)

    def render(self, input):
        return self.template.render(**input).encode("UTF-8")
