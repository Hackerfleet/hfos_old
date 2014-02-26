__author__ = 'riot'

from mako.lookup import TemplateLookup
from mako.exceptions import TemplateLookupException

from weatherscraper.logging import log

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

    def loadTemplate(self):
        try:
            self.template = self.templatestore.get_template(self.templatename + ".html")
        except TemplateLookupException:
            log("Can't find template '%s.html' in templatefolder." % self.templatename)


    def __init__(self, template):
        self.templatename = template
        self.loadTemplate()

    def render(self, input):
        self.loadTemplate()
        return self.template.render(**input).encode("UTF-8")
