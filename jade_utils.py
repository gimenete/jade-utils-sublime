from HTMLParser import HTMLParser
import sublime, sublime_plugin

void_elements = ["area", "base", "br", "col", "embed", "hr",
    "img", "input", "keygen", "link", "menuitem",
    "meta", "param", "source", "track", "wbr"]

class JadeUtilsHtml(sublime_plugin.TextCommand):

    def run(self, edit):
        html = sublime.get_clipboard()
        for region in self.view.sel():
            line = self.view.line(region)
            prefix = self.view.substr(sublime.Region(line.a, region.a))
            parser = HTML2JadeParser()
            output = parser.convert(html, prefix)
            self.view.replace(edit, sublime.Region(line.a, region.b), output)

    def is_enabled(self):
        return True

class HTML2JadeParser(HTMLParser):

    def convert(self, html, prefix):
        self.prefix = prefix
        self.output = ''
        self.indent = 0
        self.feed(html)
        return self.output

    def indentation(self):
        self.output += self.prefix
        for i in range(self.indent):
            self.output += '  '

    def handle_starttag(self, tag, attrs):
        nodestr = ''
        nodeid = ''
        nodeclasses = ''
        nodeattrs = []
        for attr in attrs:
            name = attr[0]
            value = attr[1]
            if name == 'id':
                nodeid = '#'+value
            elif name == 'class':
                classes = value.split(' ')
                for clazz in classes:
                    nodeclasses += '.'+clazz
            else:
                nodeattrs.append(attr)
        if tag == 'div' and (nodeid or nodeclasses or nodeattrs):
            tag = ''

        self.indentation()
        self.output += tag
        self.output += nodeid
        self.output += nodeclasses
        if len(nodeattrs) > 0:
            self.output += '('
            self.output += ', '.join([o[0]+'="'+o[1]+'"' for o in nodeattrs])
            self.output += ')'
        self.output += '\n'
        if not tag in void_elements:
            self.indent += 1

    def handle_endtag(self, tag):
        if not tag in void_elements:
            self.indent -= 1

    def handle_data(self, data):
        data = data.replace('\r\n', '\n').replace('\r', '\n').strip()
        for value in data.split('\n'):
            if value:
                self.indentation()
                self.output += '| '
                self.output += value
                self.output += '\n'

    def handle_comment(self, data):
        data = data.replace('\r\n', '\n').replace('\r', '\n').strip()
        for value in data.split('\n'):
            if value:
                self.indentation()
                self.output += '//- '
                self.output += value
                self.output += '\n'

    def handle_decl(self, decl):
        if decl == 'DOCTYPE html':
            self.output += 'doctype html\n'
        else:
            self.output += '<!'
            self.output += decl
            self.output += '>\n'

# def main():
#     parser = HTML2JadeParser()
#     output = parser.convert('<!DOCTYPE html><html class="foo"><head><title>Test</title></head>'
#                 '<body><div /><meta/><meta></meta><meta><meta><br><img><a>hello</a></html>')
#     print output

# main()