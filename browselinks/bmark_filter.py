#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
"""
browselinks
"""
from BeautifulSoup import BeautifulSoup
import json
import logging
import string
import webbrowser

def extract_links(_file, urlstr):
    with open(_file) as f:
        bs = BeautifulSoup(f)
        for a in bs.findAll('a'):
            if urlstr in a.get('href'):
                logging.debug(a.get('href'))
                yield a
        #links = [a for a in bs.findAll('a') if urlstr in a.get('href')]
        #return links


def write_links(_file, links):
    with file(_file,'w') as output:
        for l in links:
            output.write('<li>%s</li>' % l)

PAGE_NAV="""
<a id="prev" href="#prev">Prev</a>
<a id="next" href="#next">Next</a>
<a id="current" href="#links">[current URL]</a>
"""
PAGE_TEMPLATE=string.Template("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">
<html>
    <head>
        <title>${title}</title>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
        <script type="text/javascript">
            $(window.parent.frames[1].document).ready(function() {
                var links=${links};
                var i = 0;

                main = $$("#main");
                current = $$("a#current", nav.document);
                prev = $$("#prev", nav.document);
                next = $$("#next", nav.document);

                function update_url(url) {
                    console.log("update url to: " + url);
                    //main.attr("src",url);
                    main.location = url;
                    current.attr("href",url);
                    current.text(url);
                }

                update_url(links[i]);

                prev.click(function(e) {
                    if (i >= 1) {
                        i = i - 1;
                        update_url(links[i]);
                    }
                });

                next.click(function(e) {
                    if (i < links.length) {
                        i = i + 1;
                        update_url(links[i]);
                    }
                });
            });
        </script>
    </head>
        <frameset rows="20px,*">
            <frame id="navlinks" name="nav" src="navlinks.html" frameborder=0>

            </frame>
            <frame name="main" frameborder=0>
                [should display page here]
            </frame>
        </frameset>

</html>
""")
def write_browse_page(_file, links, title):
    links = [a.get('href') for a in links]
    with file("navlinks.html",'w') as output:
        output.write(PAGE_NAV)

    with file(_file,'w') as output:
        output.write(
            PAGE_TEMPLATE.safe_substitute(**{
                'links': json.dumps(links),
                'title': title})
        )


def browse_link_slices(links, n=6):
    hrefs = [l.get('href') for l in links]
    slices = [(n*i, n*(i+1)) for i in xrange( (len(links) / n) + 1)]
    linkslices = (hrefs.__getslice__(*slice) for slice in slices)
    for linkslice in linkslices:
        for link in linkslice:
            webbrowser.open_new_tab(link)
        raw_input('enter to continue')


import unittest
class Test_browselinks(unittest.TestCase):
    def test_browselinks(self):
        links = extract_links('./bookmarks_10_18_12.html', 'wikipainting')
        write_links('output.html', links)
        write_browse_page('browse.html', links, 'wikipainting links')
        #browse_link_slices(links)


def main():
    import optparse
    import logging

    prs = optparse.OptionParser(usage="./%prog : args")

    prs.add_option('-v', '--verbose',
                    dest='verbose',
                    action='store_true',)
    prs.add_option('-q', '--quiet',
                    dest='quiet',
                    action='store_true',)
    prs.add_option('-t', '--test',
                    dest='run_tests',
                    action='store_true',)

    prs.add_option('-f', '--filter',
                    dest='filter',
                    action='store')

    prs.add_option('-l', '--write-list',
                    dest='write_links',
                    action='store')

    prs.add_option('-o', '--write-output',
                    dest='write_output',
                    action='store')

    prs.add_option('-p', '--page-links',
                    dest='page_links',
                    action='store')

    (opts, args) = prs.parse_args()

    if not opts.quiet:
        logging.basicConfig()

        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        import sys
        sys.argv = [sys.argv[0]] + args
        import unittest
        exit(unittest.main())

    bookmarks_file = args[0]

    links = list( extract_links(bookmarks_file, opts.filter) )

    if opts.write_links:
        write_links(opts.write_links, links)

    if opts.write_output:
        write_browse_page(opts.write_output, links,
            "links from %r containing %r" % (bookmarks_file, opts.filter))

    if opts.page_links:
        n = 6
        try:
            n = int(opts.page_links)
        except Exception:
            pass
        browse_link_slices(links, n)


if __name__ == "__main__":
    main()
