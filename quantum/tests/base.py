# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010-2011 OpenStack Foundation
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Base Test Case for all Unit Tests"""

import os

import fixtures
from oslo.config import cfg
import stubout
import testtools

from quantum.openstack.common import exception

CONF = cfg.CONF
TRUE_STRING = ['True', '1']


class BaseTestCase(testtools.TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()

        self.useFixture(fixtures.FakeLogger(
            format="%(asctime)s %(levelname)8s [%(name)s] %(message)s"))

        test_timeout = int(os.environ.get('OS_TEST_TIMEOUT', 0))
        if test_timeout == -1:
            test_timeout = 0
        if test_timeout > 0:
            self.useFixture(fixtures.Timeout(test_timeout, gentle=True))

        # If someone does use tempfile directly, ensure that it's cleaned up
        self.useFixture(fixtures.NestedTempfile())
        self.useFixture(fixtures.TempHomeDir())

        self.addCleanup(CONF.reset)

        if os.environ.get('OS_STDOUT_NOCAPTURE') not in TRUE_STRING:
            stdout = self.useFixture(fixtures.StringStream('stdout')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))
        if os.environ.get('OS_STDERR_NOCAPTURE') not in TRUE_STRING:
            stderr = self.useFixture(fixtures.StringStream('stderr')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))
        self.stubs = stubout.StubOutForTesting()
        self.stubs.Set(exception, '_FATAL_EXCEPTION_FORMAT_ERRORS', True)

    def config(self, **kw):
        """
        Override some configuration values.

        The keyword arguments are the names of configuration options to
        override and their values.

        If a group argument is supplied, the overrides are applied to
        the specified configuration option group.

        All overrides are automatically cleared at the end of the current
        test by the fixtures cleanup process.
        """
        group = kw.pop('group', None)
        for k, v in kw.iteritems():
            CONF.set_override(k, v, group)
