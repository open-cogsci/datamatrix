#!/usr/bin/env python3
# coding=utf-8

from collections import OrderedDict
import yaml
import sys

if '--publish' in sys.argv:
    import publishconf as conf
else:
    import pelicanconf as conf

ROOT = conf.SITEURL
SUFFIX = ''


def orderedLoad(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):

    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)
    

def isseparator(pagename):

    for ch in pagename:
        if ch != '_':
            return False
    return True


def build_menu(d, lvl=1):

    l = []
    for pagename, entry in d.items():
        if isseparator(pagename):
            l.append('</ul></li>\n<li class="col-sm-3"><ul>')
            continue
        if entry is None:
            l.append('%s<li class="dropdown-header dropdown-header-level-%d">%s</li>' \
                % ('\t'*lvl, lvl, pagename))
            continue
        if isinstance(entry, dict):
            if lvl == 1:
                l.append(
                    ('<li class="dropdown mega-dropdown">'
                    '<a href="#" class="dropdown-toggle level-%d" data-toggle="dropdown">'
                    '%s&nbsp;<span class="glyphicon glyphicon-menu-down"></span></a>') \
                    % (lvl+1, pagename))
                l.append('<ul class="dropdown-menu mega-dropdown-menu row"><li class="col-sm-3"><ul>')
                l.append(build_menu(entry, lvl+1))
                l.append('</ul></li></ul></li>')
            else:
                l.append('%s<li class="dropdown-header dropdown-header-level-%d">%s</li>' \
                    % ('\t'*(lvl+1), lvl+1, pagename))
                l.append(build_menu(entry, lvl+1))
            continue
        if entry.startswith('http'):
            l.append('%s<li class="level-%d"><a href="%s">%s</a></li>' \
                % ('\t'*lvl, lvl, entry, pagename))
        else:
            l.append('%s<li class="level-%d"><a href="%s/%s%s">%s</a></li>' \
                % ('\t'*lvl, lvl, ROOT, entry, SUFFIX, pagename))
    return '\n'.join(l)


def build_live_sitemap(d):

    sitemap = OrderedDict()
    for pagename, entry in d.items():
        if isinstance(entry, list):
            cls = entry[1]
            entry = entry[0]
        else:
            cls = ''
        if isseparator(pagename) or entry in [None, '']:
            continue
        if isinstance(entry, dict):
            sitemap[pagename] = build_live_sitemap(entry)
            continue
        if entry.startswith('http'):
            sitemap[pagename] = entry
        else:
            sitemap[pagename] = '/' + conf.BRANCH + '/' + entry + SUFFIX
    return sitemap


def build_seo_sitemap(d):

    sitemap = []
    for pagename, entry in d.items():
        if isseparator(pagename) or entry in [None, '']:
            continue
        if isinstance(entry, dict):
            sitemap += build_seo_sitemap(entry)
            continue
        if not entry.startswith('http'):
            sitemap.append(ROOT + '/' + entry + SUFFIX)
    return sitemap


def main():

    with open('sitemap.yaml') as f:
        d = orderedLoad(f)
    with open('themes/cogsci/templates/mega-menu-content.html', 'w') as f:
        f.write(build_menu(d))
    print('Generated menu content')
    sitemap = build_live_sitemap(d)
    with open(u'static/sitemap.yml', u'w') as fd:
        yaml.dump(sitemap, fd, default_flow_style=False)
    print('Generated live sitemap')
    with open('static/seo-sitemap.txt', 'w') as fd:
        fd.write('\n'.join(build_seo_sitemap(d)) + '\n')
    print('Generated seo sitemap')


if __name__ == '__main__':
    main()
