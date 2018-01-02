#  PyExpense, Django powered webapp to track shared expenses.
#  Copyright (C) 2017 Peijun Ma
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from math import fsum
from typing import Dict, Tuple

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

from core import MONEY, STRING_SIZE as SS

Model = models.Model

name_field = models.CharField(max_length=SS['small'])
auto_created_at = models.DateTimeField(auto_now_add=True)
auto_updateed_at = models.DateTimeField(auto_now=True)


class User(Model):
    """
    User model.

    Fields:
        name: A string for the name.
        created_at: A Django datetime object for creation time.
        updated_at:  A Dajango datetime object for latest update time.

    Relations:
        Many to many: Share
        One to Many: One User -> Many Expense
                     One User -> Many Expense Ratio
    """

    name = name_field
    created_at = auto_created_at
    updated_at = auto_updateed_at

    @property
    def paid_by(self) -> QuerySet:
        """Return a QuerySet of ``Expense`` paid by this user."""
        return Expense.objects.filter(paid_by=self).distinct()

    @property
    def paid_for(self) -> QuerySet:
        """Return a QuerySet of ``ExpenseRatio`` for this user."""
        return ExpenseRatio.objects.filter(user=self).distinct()

    @property
    def shares(self) -> QuerySet:
        """Returns a QuerySet of ``Share`` the user is in."""
        return Share.objects.filter(users__in=[self]).distinct()

    @property
    def balance(self) -> Dict['User', float]:
        """Returns a dict of {User: amount owned}"""
        # TODO: implement this
        return {}


PaidFor = Dict[User, Tuple[int, int]]


class Share(Model):
    """
    Share model.

    Fields:
        name: A string for the name.
        created_at: A Django datetime object for creation time.
        updated_at:  A Dajango datetime object for latest update time.
        description: A string for the description of this share.
        users: All users in this Share.

    Relations:
        Many to many: User
        One to many: One Share -> Many Expense
    """
    name = name_field
    created_at = auto_created_at
    updated_at = auto_updateed_at
    description = models.CharField(max_length=SS['medium'])
    users = models.ManyToManyField(User)

    @property
    def expenses(self) -> QuerySet:
        return Expense.objects.filter(share=self).distinct()

    @property
    def total(self) -> float:
        return fsum(e.total for e in self.expenses)


class Expense(Model):
    """
    Expense model.

    Fields:
        created_at: A Django datetime object for creation time.
        updated_at: A Dajango datetime object for latest update time.
        description: A string for the description of this share.
        share: The Share that this expense belongs to.
        total: The total amount of money for this Expense.
        paid_by: This Expense is *paid by* the User.
        resolved: A bool indicating wether this Expense is resolved.

    Relations:
        One to Many: One Expense -> Many ExpenseRatio
                     One Share -> Many Expense
                     One User -> Many Expense
    """
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = auto_updateed_at
    description = models.CharField(max_length=SS['medium'])
    share = models.ForeignKey(Share, on_delete=models.CASCADE)
    total = models.DecimalField(**MONEY)
    paid_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    resolved = models.BooleanField(default=False)

    @classmethod
    def new(cls, *, paid_for: PaidFor, **kwargs):
        instance = cls.objects.create(**kwargs)
        instance.generate_ratio(paid_for)
        return instance

    @property
    def ratio(self) -> QuerySet:
        """
        Returns a QuerySet of ExpenseRatio that belongs to this Expense.
        """
        return ExpenseRatio.objects.filter(expense=self)

    def generate_ratio(self, paid_for: PaidFor):
        """
        Generate a set of ``ExpenseRatio`` for this expense.

        :param paid_for: A dict of User to a tuple representing a fraction
                         like so {User: (numerator, denominator)}

        :return: A list of the generated ``ExpenseRatio``
        """
        for ratio in self.ratio:
            ratio.delete()
        return [ExpenseRatio.objects.create(
            user=user, numerator=top, denominator=bot, expense=self)
            for user, (top, bot) in paid_for.items()]


class ExpenseRatio(Model):
    """
    ExpenseRatio model

    Fields:
        user: The User associated with this ExpenseRatio.
        numerator: The numerator of this ratio fraction.
        denominator: The denominator of this ratio fraction.
        expense: The Expense thie ExpenseRaio belongs to.

    Relations:
        One to Many: One Expense -> Many ExpenseRatio
                     One User -> Many ExpenseRatio
    """
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    numerator = models.PositiveIntegerField()
    denominator = models.PositiveIntegerField()
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
