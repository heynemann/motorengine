#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.testing import AsyncTestCase as TornadoAsyncTestCase
from tornado.testing import gen_test  # NOQA

import motorengine.connection


class AsyncTestCase(TornadoAsyncTestCase):
    def tearDown(self):
        super(AsyncTestCase, self).tearDown()
        motorengine.connection.cleanup()

    def stop(self, *args, **kwargs):
        '''Stops the ioloop, causing one pending (or future) call to wait()
        to return.

        Keyword arguments or a single positional argument passed to stop() are
        saved and will be returned by wait().
        '''
        self.__stop_args = {'args': args, 'kwargs': kwargs}
        if self.__running:
            self.io_loop.stop()
            self.__running = False
        self.__stopped = True

    def exec_async(self, method, *args, **kw):
        method(callback=self.stop, *args, **kw)
        result = self.wait()

        return result['args'], result['kwargs']
