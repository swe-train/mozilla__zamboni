import mock
from nose.tools import eq_

from lib.utils import static_url
from mkt.constants.applications import DEVICE_TYPE_LIST
from mkt.site.tests import TestCase
from mkt.websites.models import Website
from mkt.websites.utils import website_factory


class TestWebsiteModel(TestCase):
    def test_devices(self):
        website = Website()
        eq_(sorted(website.devices),
            sorted([device.id for device in DEVICE_TYPE_LIST]))

    def test_get_icon_url(self):
        website = Website(pk=1, icon_type='image/png')
        expected = (static_url('WEBSITE_ICON_URL')
                    % ('0', website.pk, 32, 'never'))
        assert website.get_icon_url(32).endswith(expected), (
            'Expected %s, got %s' % (expected, website.get_icon_url(32)))

    def test_get_icon_url_big_pk(self):
        website = Website(pk=9876, icon_type='image/png')
        expected = (static_url('WEBSITE_ICON_URL')
                    % (str(website.pk)[:-3], website.pk, 32, 'never'))
        assert website.get_icon_url(32).endswith(expected), (
            'Expected %s, got %s' % (expected, website.get_icon_url(32)))

    def test_get_icon_url_bigger_pk(self):
        website = Website(pk=98765432, icon_type='image/png')
        expected = (static_url('WEBSITE_ICON_URL')
                    % (str(website.pk)[:-3], website.pk, 32, 'never'))
        assert website.get_icon_url(32).endswith(expected), (
            'Expected %s, got %s' % (expected, website.get_icon_url(32)))

    def test_get_icon_url_hash(self):
        website = Website(pk=1, icon_type='image/png', icon_hash='abcdef')
        assert website.get_icon_url(32).endswith('?modified=abcdef')

    def test_get_icon_no_icon(self):
        website = Website(pk=1)
        assert website.get_icon_url(32).endswith('/default-32.png')


class TestWebsiteESIndexation(TestCase):
    @mock.patch('mkt.search.indexers.BaseIndexer.index_ids')
    def test_update_search_index(self, update_mock):
        website = website_factory()
        update_mock.assert_called_once_with([website.pk])

    @mock.patch('mkt.search.indexers.BaseIndexer.unindex')
    def test_delete_search_index(self, delete_mock):
        for x in xrange(4):
            website_factory()
        count = Website.objects.count()
        Website.objects.all().delete()
        eq_(delete_mock.call_count, count)
