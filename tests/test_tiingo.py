#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `tiingo` package."""

import csv

from unittest import TestCase

import vcr

from tiingo import TiingoClient
from tiingo.restclient import RestClientError


# TODO
# Add tests for
# Invalid API key
# Invalid ticker
# Use unittest asserts rather than regular asserts
# Wrap server errors with client side descriptive errors
# Coerce startDate/endDate to string if they are passed in as datetime
# Use VCR.py to enable offline testing
# Expand test coverage


def test_client_repr():
    """Test representation of client when logged to console"""
    client = TiingoClient()
    base_url = "https://api.tiingo.com"
    assert repr(client) == "<TiingoClient(url=\"{}\")>".format(base_url)


# PRICES ENDPOINTS
class TestTickerPrices(TestCase):

    def setUp(self):
        self._client = TiingoClient()
        # Stub all endpoints that get reused
        with vcr.use_cassette('tests/fixtures/ticker_price.yaml'):
            self._ticker_price_response = \
                self._client.get_ticker_price("GOOGL")
        with vcr.use_cassette('tests/fixtures/ticker_metadata.yaml'):
            self._ticker_metadata_response = \
                self._client.get_ticker_metadata("GOOGL")

    def test_ticker_price(self):
        """Test the EOD Prices Endpoint"""
        assert len(self._ticker_price_response) == 1
        assert self._ticker_price_response[0].get('adjClose')

    def test_ticker_price_with_date(self):
        """Test the EOD Prices Endpoint with data param"""
        with vcr.use_cassette('tests/fixtures/ticker_price_with_date.yaml'):
            prices = self._client.get_ticker_price("GOOGL",
                                                   startDate="2015-01-01",
                                                   endDate="2015-01-05")
        self.assertGreater(len(prices), 1)

    def test_ticker_price_with_csv(self):
        """Confirm that CSV endpoint works"""
        with vcr.use_cassette('tests/fixtures/ticker_price_with_date_csv.yaml'):
            prices_csv = self._client.get_ticker_price("GOOGL",
                                                       startDate="2015-01-01",
                                                       endDate="2015-01-05",
                                                       fmt='csv')
        reader = csv.reader(prices_csv.splitlines(), delimiter=",")
        rows = list(reader)
        assert len(rows) > 2  # more than 1 day of data

    def test_ticker_metadata(self):
        """Refactor this with python data schemavalidation"""
        assert self._ticker_metadata_response.get('ticker') == "GOOGL"
        assert self._ticker_metadata_response.get("name")

    def test_list_stock_tickers(self):
        """Update this test when the method is added."""
        with vcr.use_cassette('tests/fixtures/list_stock_tickers.yaml'):
            tickers = self._client.list_stock_tickers()
        assert len(tickers) > 1
        assert all(ticker['assetType'] == 'Stock' for ticker in tickers)

    def test_ticker_metadata_for_object(self):
        data = self._client.get_ticker_metadata("GOOGL", fmt='object')
        assert len(data[0].name) > 1


# tiingo/news
class TestNews(TestCase):

    def setUp(self):
        self._client = TiingoClient()
        self.article_keys = [  # Properties every article should have.
            'description',
            'title',
            'url',
            'publishedDate',
            'tags',
            'source',
            'tickers',
            'crawlDate',
            'id'
        ]

    def test_get_news_articles(self):
        """Confirm that news article work"""
        NUM_ARTICLES = 1

        search_params = {
            "tickers": ["aapl", "googl"],
            "tags": ["Technology", "Bitcoin"],
            "startDate": "2016-01-01",
            "endDate": "2017-08-31",
            "sources": ['washingtonpost.com', 'altcointoday.com'],
            "limit": NUM_ARTICLES
        }

        with vcr.use_cassette('tests/fixtures/news.yaml'):
            articles = self._client.get_news(**search_params)
        assert len(articles) == NUM_ARTICLES
        for article in articles:
            assert all(key in article for key in self.article_keys)

    def test_get_news_bulk(self):
        """Fails because this API key lacks institutional license"""

        with self.assertRaises(RestClientError),\
                vcr.use_cassette('tests/fixtures/news_bulk.yaml'):
            value = self._client.get_bulk_news(file_id="1")
            assert value

    def test_get_news_bulk_ids(self):
        """Fails because this API key lacks institutional license"""

        with self.assertRaises(RestClientError),\
                vcr.use_cassette('tests/fixtures/news_bulk_file_ids.yaml'):
            value = self._client.get_bulk_news()
            assert value

    def test_get_news_as_objects(self):
        """Fails because this API key lacks institutional license"""
        with self.assertRaises(RestClientError):
            value = self._client.get_news(fmt="object")
            assert value

    def test_news_bulk_as_objects(self):
        """Fails because this API key lacks institutional license"""
        with self.assertRaises(RestClientError):
            assert self._client.get_bulk_news(fmt="object")
