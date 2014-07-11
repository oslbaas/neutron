# Copyright 2014 Blue Box Group, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# @author: Dustin Lundquist, Blue Box Group

import mock

from neutron import context
from neutron.openstack.common import uuidutils
from neutron.plugins.common import constants
from neutron.services.loadbalancer import constants as lb_const
from neutron.services.loadbalancer.drivers.shim import driver as shim_driver
from neutron.tests import base
from neutron.tests.unit.db.loadbalancer import test_db_loadbalancer


class TestShimLoadBalancerDriver(base.BaseTestCase):

    def setUp(self):
        super(TestShimLoadBalancerDriver, self).setUp()
        self.context = context.get_admin_context()
        self.mock_plugin = mock.Mock()
        v1_driver = test_db_loadbalancer.NoopLbaaSDriver(self.mock_plugin)
        self.driver = shim_driver.LBShimDriver(self.mock_plugin, v1_driver)

        self._last_ip_octet = 1
        self._tenant_id = uuidutils.generate_uuid()

        self.member = self._mock_member()
        members = [self.member, self._mock_member()]
        self.health_monitor = self._mock_health_monitor()
        self.pool = self._mock_pool(members)
        self.listener = self._mock_listener(self.pool)
        self.load_balancer = self._mock_load_balancer([self.listener])

    def _mock_member(self):
        member = mock.Mock()
        member.id = uuidutils.generate_uuid()
        member.tenant_id = self._tenant_id
        member.address = '192.0.2.%d' % self._last_ip_octet
        self._last_ip_octet += 1
        member.protocol_port = 8080
        member.weight = 10
        member.subnet_id = None
        member.status = constants.ACTIVE
        member.admin_status_up = True

        return member

    def _mock_health_monitor(self):
        return None

    def _mock_pool(self, members):
        pool = mock.Mock()
        pool.id = uuidutils.generate_uuid()
        pool.tenant_id = self._tenant_id
        pool.name = 'app-pool'
        pool.description = ''
        pool.healthmonitor_id = None
        pool.protocol = lb_const.PROTOCOL_HTTP
        pool.lb_algorithm = lb_const.LB_METHOD_ROUND_ROBIN
        pool.status = constants.ACTIVE
        pool.admin_state_up = True
        pool.members = members

        for member in members:
            member.pool = pool
            member.pool_id = pool.id

        return pool

    def _mock_listener(self, pool):
        listener = mock.Mock()
        listener.id = uuidutils.generate_uuid()
        listener.name = 'http-app'
        listener.description = "App Foo HTTP"
        listener.tenant_id = self._tenant_id
        listener.default_pool = pool
        listener.default_pool_id = pool.id
        listener.protocol = lb_const.PROTOCOL_HTTP
        listener.protocol_port = 80
        listener.connection_limit = 10000
        listener.admin_status_up = True
        listener.status = constants.ACTIVE

        return listener

    def _mock_load_balancer(self, listeners):
        load_balancer = mock.Mock()
        load_balancer.id = uuidutils.generate_uuid()
        load_balancer.tenant_id = self._tenant_id
        load_balancer.name = "foo"
        load_balancer.description = "Foo load balancer"
        load_balancer.vip_subnet_id = None
        load_balancer.vip_address = None
        load_balancer.status = constants.ACTIVE
        load_balancer.listeners = listeners

        for listener in listeners:
            listener.load_balancer = load_balancer
            listener.load_balancer_id = load_balancer.id

        return load_balancer

    def test_load_balancer_create(self):
        with mock.patch.object(self.driver.wrapped_driver, 'create_vip') as \
                create:
            self.driver.load_balancer.create(self.context, self.load_balancer)
            create.assert_called_once_with(self.context, mock.ANY)

    def test_load_balancer_update(self):
        with mock.patch.object(self.driver.wrapped_driver, 'update_vip') as \
                update:
            self.driver.load_balancer.update(self.context, self.load_balancer,
                                             self.load_balancer)
            update.assert_called_once_with(self.context, mock.ANY, mock.ANY)

    def test_load_balancer_delete(self):
        with mock.patch.object(self.driver.wrapped_driver, 'delete_vip') as \
                delete:
            self.driver.load_balancer.delete(self.context, self.load_balancer)
            delete.assert_called_once_with(self.context, mock.ANY)

    def test_load_balancer_stats(self):
        with mock.patch.object(self.driver.wrapped_driver, 'stats') as stats:
            self.driver.load_balancer.stats(self.context, self.load_balancer)
            stats.assert_called_once_with(self.context, mock.ANY)

    def test_listener_create(self):
        with mock.patch.object(self.driver.wrapped_driver, 'create_vip') as \
                create:
            self.driver.listener.create(self.context, self.listener)
            create.assert_called_once_with(self.context, mock.ANY)

    def test_listener_update(self):
        with mock.patch.object(self.driver.wrapped_driver, 'update_vip') as \
                update:
            self.driver.listener.update(self.context, self.listener,
                                             self.listener)
            update.assert_called_once_with(self.context, mock.ANY, mock.ANY)

    def test_listener_delete(self):
        with mock.patch.object(self.driver.wrapped_driver, 'delete_vip') as \
                delete:
            self.driver.listener.delete(self.context, self.listener)
            delete.assert_called_once_with(self.context, mock.ANY)

    def test_pool_create(self):
        with mock.patch.object(self.driver.wrapped_driver, 'create_pool') as \
                create:
            self.driver.pool.create(self.context, self.pool)
            create.assert_called_once_with(self.context, mock.ANY)

    def test_pool_update(self):
        with mock.patch.object(self.driver.wrapped_driver, 'update_pool') as \
                update:
            self.driver.pool.update(self.context, self.pool, self.pool)
            update.assert_called_once_with(self.context, mock.ANY, mock.ANY)

    def test_pool_delete(self):
        with mock.patch.object(self.driver.wrapped_driver, 'delete_pool') as \
                delete:
            self.driver.pool.delete(self.context, self.pool)
            delete.assert_called_once_with(self.context, mock.ANY)

    def test_member_create(self):
        with mock.patch.object(self.driver.wrapped_driver, 'create_member') \
                as create:
            self.driver.member.create(self.context, self.member)
            create.assert_called_once_with(self.context, mock.ANY)

    def test_member_update(self):
        with mock.patch.object(self.driver.wrapped_driver, 'update_member') \
                as update:
            self.driver.member.update(self.context, self.member, self.member)
            update.assert_called_once_with(self.context, mock.ANY, mock.ANY)

    def test_member_delete(self):
        with mock.patch.object(self.driver.wrapped_driver, 'delete_member') \
                as delete:
            self.driver.member.delete(self.context, self.member)
            delete.assert_called_once_with(self.context, mock.ANY)

    def test_health_monitor_create(self):
        with mock.patch.object(self.driver.wrapped_driver,
                               'create_pool_health_monitor') as create:
            self.driver.health_monitor.create(self.context, self.health_monitor)
            # create.assert_called_once_with(self.context, mock.ANY, self.pool.id)

    def test_health_monitor_update(self):
        with mock.patch.object(self.driver.wrapped_driver,
                               'update_pool_health_monitor') as update:
            self.driver.health_monitor.update(self.context, self.health_monitor, self.health_monitor)
            # update.assert_called_once_with(self.context, mock.ANY, mock.ANY, mock.ANY)

    def test_health_monitor_delete(self):
        with mock.patch.object(self.driver.wrapped_driver,
                               'delete_pool_health_monitor') as delete:
            self.driver.health_monitor.delete(self.context, self.health_monitor)
            # delete.assert_called_once_with(self.context, mock.ANY, self.pool.id)
