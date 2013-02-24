# collectd-solr.py
#
# This program is free software; you can solrtribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; only version 2 of the License is applicable.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# Authors:
#   Denis Zhdanov <denis.zhdanov@gmail.com>
#   Garret Heaton <powdahound at gmail.com> (I used his solr-info.py as template of collectd plugin)
#   Distilled Media Ltd - author of Munin Solr plugins
#   Gasol Wu - another author of Solr Munin plugins
#
# About this plugin:
#   This plugin uses collectd's Python plugin to record Solr information.
#
# collectd:
#   http://collectd.org
# Solr:
#   http://lucene.apache.org/solr/
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml
# Distilled Media Ltd.
#   https://github.com/distilledmedia/munin-plugins/
# Gasol Wu
#   https://github.com/Gasol/munin-solr-plugins/
# powdahoud's solr-collectd-plugin
#   https://github.com/powdahound/solr-collectd-plugin/
#

import collectd
import os, sys, urllib2
try:
    import xml.etree.cElementTree as etree
except ImportError:
    try:
        import xml.etree.ElementTree as etree
    except ImportError:
        print 'python >= 2.5'
        sys.exit()

# Host to connect to. Override in config by specifying 'Host'.
SOLR_HOST = 'localhost'

# Port to connect on. Override in config by specifying 'Port'.
SOLR_PORT = 8080

# Solr URL. Override in config by specifying 'SolrURL'.
SOLR_URL = '/solr'

# Solr Admin URL. Override in config by specifying 'SolrAdminURL'.
SOLR_ADMIN_URL = 'admin/stats?stats=true'


def get_cores():
    url = '%s?action=status' % SOLR_ADMIN_URL
    f = urllib2.urlopen(url)
    xml = etree.fromstring(f.read())
    cores = [lst.attrib['name'].strip() for lst in xml.findall('./lst/lst')]
    return cores

def fetch_info():
    """Connect to Solr stat page and request info"""
    return


def configure_callback(conf):
    """Receive configuration block"""
    global SOLR_HOST, SOLR_PORT, SOLR_URL, SOLR_ADMIN_URL
    for node in conf.children:
        if node.key == 'Host':
            SOLR_HOST = node.values[0]
        elif node.key == 'Port':
            SOLR_PORT = int(node.values[0])
        if node.key == 'Host':
            SOLR_URL = node.values[0]
        if node.key == 'Host':
            SOLR_ADMIN_URL = node.values[0]
        else:
            collectd.warning('collectd-solr plugin: Unknown config key: %s.' % node.key)
    log_verbose('Configured: host=%s, port=%s, url=%s, admin_url=%s' % (SOLR_HOST, SOLR_PORT, SOLR_URL, SOLR_ADMIN_URL))


def dispatch_value(info, key, type, type_instance=None):
    """Read a key from info response data and dispatch a value"""
    if key not in info:
        collectd.warning('collectd-solr plugin: Info key not found: %s' % key)
        return

    if not type_instance:
        type_instance = key

    value = int(info[key])
    log_verbose('Sending value: %s=%s' % (type_instance, value))

    val = collectd.Values(plugin='collectd-solr')
    val.type = type
    val.type_instance = type_instance
    val.values = [value]
    val.dispatch()


def read_callback():
    log_verbose('Read callback called')
    info = fetch_info()

    if not info:
        collectd.error('solr plugin: No info received')
        return

    # send high-level values
    dispatch_value(info, 'test1', 'gauge')
    dispatch_value(info, 'test2', 'bytes')
    dispatch_value(info, 'test3', 'counter', 'values')

# register callbacks
collectd.register_config(configure_callback)
collectd.register_read(read_callback)