# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2015 SciFabric LTD.
#
# PyBossa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBossa.  If not, see <http://www.gnu.org/licenses/>.

from default import Test, assert_not_raises, db
from pybossa.auth import ensure_authorized_to
from nose.tools import assert_raises
from werkzeug.exceptions import Forbidden, Unauthorized
from mock import patch
from test_authorization import mock_current_user
from factories import ProjectFactory, TaskFactory, TaskRunFactory
from pybossa.model.result import Result
from pybossa.repositories import ResultRepository



class TestResultAuthorization(Test):

    mock_anonymous = mock_current_user()
    mock_authenticated = mock_current_user(anonymous=False, admin=False, id=2)
    mock_pro = mock_current_user(anonymous=False, admin=False, id=2, pro=True)
    mock_admin = mock_current_user(anonymous=False, admin=True, id=1)

    def setUp(self):
        super(TestResultAuthorization, self).setUp()
        self.result_repo = ResultRepository(db)

    def create_result(self, n_answers=1, filter_by=False):
        task = TaskFactory.create(n_answers=n_answers)
        TaskRunFactory.create(task=task)
        if filter_by:
            return self.result_repo.filter_by(project_id=1)
        else:
            return self.result_repo.get_by(project_id=1)


    @patch('pybossa.auth.current_user', new=mock_anonymous)
    def test_anonymous_user_can_read_result(self):
        """Test anonymous users can read results"""

        result = self.create_result()

        assert ensure_authorized_to('read', result)

    @patch('pybossa.auth.current_user', new=mock_authenticated)
    def test_auth_user_can_read_result(self):
        """Test auth users can read results"""

        result = self.create_result()

        assert ensure_authorized_to('read', result)

    @patch('pybossa.auth.current_user', new=mock_admin)
    def test_admin_user_can_read_result(self):
        """Test admin users can read results"""

        result = self.create_result()

        assert ensure_authorized_to('read', result)


    @patch('pybossa.auth.current_user', new=mock_anonymous)
    def test_anonymous_user_cannot_save_results(self):
        """Test anonymous users cannot save results of a specific project"""

        result = Result()

        assert_raises(Unauthorized, ensure_authorized_to, 'create',
                      result, project_id=1)

    @patch('pybossa.auth.current_user', new=mock_authenticated)
    def test_authenticated_user_cannot_save_results(self):
        """Test authenticated users cannot save results of a specific project"""

        result = Result()

        assert_raises(Forbidden, ensure_authorized_to, 'create',
                      result, project_id=1)


    @patch('pybossa.auth.current_user', new=mock_admin)
    def test_admin_user_cannot_save_results(self):
        """Test admin users cannot save results of a specific project"""

        result = Result()

        assert_raises(Forbidden, ensure_authorized_to, 'create',
                      result, project_id=1)

    @patch('pybossa.auth.current_user', new=mock_anonymous)
    def test_anonymous_user_cannot_delete_results(self):
        """Test anonymous users cannot delete results of a specific project"""

        result = Result()

        assert_raises(Unauthorized, ensure_authorized_to, 'delete',
                      result, project_id=1)

    @patch('pybossa.auth.current_user', new=mock_authenticated)
    def test_authenticated_user_cannot_delete_results(self):
        """Test authenticated users cannot delete results of a specific project"""

        result = Result()

        assert_raises(Forbidden, ensure_authorized_to, 'delete',
                      result, project_id=1)


    @patch('pybossa.auth.current_user', new=mock_admin)
    def test_admin_user_cannot_delete_results(self):
        """Test admin users cannot delete results of a specific project"""

        result = Result()

        assert_raises(Forbidden, ensure_authorized_to, 'delete',
                      result, project_id=1)

    @patch('pybossa.auth.current_user', new=mock_anonymous)
    def test_anonymous_user_cannot_update_results(self):
        """Test anonymous users cannot update results of a specific project"""

        result = self.create_result()

        assert_raises(Unauthorized, ensure_authorized_to, 'update',
                      result, project_id=1)

    # @patch('pybossa.auth.current_user', new=mock_authenticated)
    # def test_authenticated_user_cannot_delete_results(self):
    #     """Test authenticated users cannot delete results of a specific project"""

    #     result = Result()

    #     assert_raises(Forbidden, ensure_authorized_to, 'delete',
    #                   result, project_id=1)


    # @patch('pybossa.auth.current_user', new=mock_admin)
    # def test_admin_user_cannot_delete_results(self):
    #     """Test admin users cannot delete results of a specific project"""

    #     result = Result()

    #     assert_raises(Forbidden, ensure_authorized_to, 'delete',
    #                   result, project_id=1)


    #@patch('pybossa.auth.current_user', new=mock_authenticated)
    #def test_owner_user_cannot_read_auditlog(self):
    #    """Test owner users cannot read an auditlog"""

    #    owner = UserFactory.create_batch(2)[1]
    #    project = ProjectFactory.create(owner=owner)
    #    log = AuditlogFactory.create(project_id=project.id)

    #    assert self.mock_authenticated.id == project.owner_id

    #    assert_raises(Forbidden, ensure_authorized_to, 'read', log)


    #@patch('pybossa.auth.current_user', new=mock_authenticated)
    #def test_owner_user_cannot_read_project_auditlogs(self):
    #    """Test owner users cannot read auditlogs of a specific project"""

    #    owner = UserFactory.create_batch(2)[1]
    #    project = ProjectFactory.create(owner=owner)

    #    assert_raises(Forbidden, ensure_authorized_to, 'read', Auditlog, project_id=project.id)


    #@patch('pybossa.auth.current_user', new=mock_pro)
    #def test_pro_user_can_read_auditlog(self):
    #    """Test pro users can read an auditlog from an owned project"""

    #    owner = UserFactory.create_batch(2, pro=True)[1]
    #    project = ProjectFactory.create(owner=owner)
    #    log = AuditlogFactory.create(project_id=project.id)

    #    assert self.mock_pro.id == project.owner_id
    #    assert_not_raises(Exception, ensure_authorized_to, 'read', log)


    #@patch('pybossa.auth.current_user', new=mock_pro)
    #def test_pro_user_can_read_project_auditlogs(self):
    #    """Test pro users cannot read auditlogs from an owned project"""

    #    owner = UserFactory.create_batch(2, pro=True)[1]
    #    project = ProjectFactory.create(owner=owner)

    #    assert self.mock_pro.id == project.owner_id
    #    assert_not_raises(Exception, ensure_authorized_to, 'read', Auditlog, project_id=project.id)


    #@patch('pybossa.auth.current_user', new=mock_pro)
    #def test_pro_user_cannot_read_auditlog(self):
    #    """Test pro users cannot read an auditlog from a non-owned project"""

    #    users = UserFactory.create_batch(2, pro=True)
    #    project = ProjectFactory.create(owner=users[0])
    #    log = AuditlogFactory.create(project_id=project.id)

    #    assert self.mock_pro.id != project.owner_id
    #    assert_raises(Forbidden, ensure_authorized_to, 'read', log)


    #@patch('pybossa.auth.current_user', new=mock_pro)
    #def test_pro_user_cannot_read_project_auditlogs(self):
    #    """Test pro users cannot read auditlogs from a non-owned project"""

    #    users = UserFactory.create_batch(2, pro=True)
    #    project = ProjectFactory.create(owner=users[0])

    #    assert self.mock_pro.id != project.owner_id
    #    assert_raises(Forbidden, ensure_authorized_to, 'read', Auditlog, project_id=project.id)


    #@patch('pybossa.auth.current_user', new=mock_admin)
    #def test_admin_user_can_read_auditlog(self):
    #    """Test admin users can read an auditlog"""

    #    owner = UserFactory.create_batch(2)[1]
    #    project = ProjectFactory.create(owner=owner)
    #    log = AuditlogFactory.create(project_id=project.id)

    #    assert self.mock_admin.id != project.owner_id
    #    assert_not_raises(Exception, ensure_authorized_to, 'read', log)


    #@patch('pybossa.auth.current_user', new=mock_admin)
    #def test_admin_user_can_read_project_auditlogs(self):
    #    """Test admin users can read auditlogs from a project"""

    #    owner = UserFactory.create_batch(2)[1]
    #    project = ProjectFactory.create(owner=owner)

    #    assert self.mock_admin.id != project.owner_id
    #    assert_not_raises(Exception, ensure_authorized_to, 'read', Auditlog, project_id=project.id)


    #@patch('pybossa.auth.current_user', new=mock_anonymous)
    #def test_anonymous_user_cannot_crud_auditlog(self):
    #    """Test anonymous users cannot crud auditlogs"""

    #    log = Auditlog()

    #    assert_raises(Unauthorized, ensure_authorized_to, 'create', log)
    #    assert_raises(Unauthorized, ensure_authorized_to, 'update', log)
    #    assert_raises(Unauthorized, ensure_authorized_to, 'delete', log)


    #@patch('pybossa.auth.current_user', new=mock_authenticated)
    #def test_authenticated_user_cannot_crud_auditlog(self):
    #    """Test authenticated users cannot crud auditlogs"""

    #    log = Auditlog()

    #    assert_raises(Forbidden, ensure_authorized_to, 'create', log)
    #    assert_raises(Forbidden, ensure_authorized_to, 'update', log)
    #    assert_raises(Forbidden, ensure_authorized_to, 'delete', log)


    #@patch('pybossa.auth.current_user', new=mock_pro)
    #def test_pro_user_cannot_crud_auditlog(self):
    #    """Test pro users cannot crud auditlogs"""

    #    log = Auditlog()

    #    assert_raises(Forbidden, ensure_authorized_to, 'create', log)
    #    assert_raises(Forbidden, ensure_authorized_to, 'update', log)
    #    assert_raises(Forbidden, ensure_authorized_to, 'delete', log)

    #@patch('pybossa.auth.current_user', new=mock_admin)
    #def test_admin_user_cannot_crud_auditlog(self):
    #    """Test admin users cannot crud auditlogs"""

    #    log = Auditlog()

    #    assert_raises(Forbidden, ensure_authorized_to, 'create', log)
    #    assert_raises(Forbidden, ensure_authorized_to, 'update', log)
    #    assert_raises(Forbidden, ensure_authorized_to, 'delete', log)
