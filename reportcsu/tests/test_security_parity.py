"""
Security tests for reportcsu: the claims behind the CSU invoice reports are row scoped.

The report view (report.scope) refuses a location or health-facility parameter outside
the user's districts, but a report run on "all" (no location parameter) used to read
every claim of the country. Each report now starts from Claim.get_queryset(None, user),
whose district / health-facility / program scope is covered by the claim parity tests;
these tests make sure every report goes through it, with the caller.
Tags: [NEW] no reference equivalent (reportcsu is Cameroon specific).

Run: manage.py test reportcsu.test_security_parity --keepdb
"""
from unittest import mock

from django.test import TestCase

from claim.models import Claim
from core.test_helpers import create_right_only_user, create_security_tree
from program.test_helpers import create_test_program
from reportcsu import models as reports

PERIOD = dict(date_from="2026-01-01", date_to="2026-01-31")


class ReportClaimsAreScopedTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tree = create_security_tree("SPRC")
        cls.user = create_right_only_user("sprc_rep", [131215], [cls.tree.d1.id])
        # the HIV invoice only runs when an HIV program exists
        create_test_program(code="SPHIV", name="HIV")

    def _scoped_users(self, report, **params):
        """The users each claim list of `report` was scoped with."""
        users = []
        original = Claim.get_queryset.__func__

        def spy(cls, queryset, user=None, **kwargs):
            users.append(user)
            return original(cls, queryset, user, **kwargs)

        with mock.patch.object(Claim, "get_queryset", classmethod(spy)):
            report(self.user, **params)
        return users

    def _assert_scoped(self, report, **params):
        users = self._scoped_users(report, **params)
        self.assertTrue(users, f"{report.__name__} read no claim through Claim.get_queryset")
        self.assertTrue(all(u is self.user for u in users),
                        f"{report.__name__} scoped its claims with another user")

    def test_invoice_csu_reads_the_users_claims(self):
        self._assert_scoped(reports.invoice_csu_query, **PERIOD)

    def test_invoice_hiv_reads_the_users_claims(self):
        self._assert_scoped(reports.invoice_hiv_query, **PERIOD)

    def test_invoice_birth_declaration_reads_the_users_claims(self):
        self._assert_scoped(reports.invoice_declaration_naissance_query, **PERIOD)

    def test_invoice_district_reads_the_users_claims(self):
        self._assert_scoped(reports.invoice_district_query,
                            date_from="2026-01", date_to="2026-01", district=self.tree.d1.code)

    def test_invoice_fagep_reads_the_users_claims(self):
        self._assert_scoped(reports.invoice_fagep_query, **PERIOD)
