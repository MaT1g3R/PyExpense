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

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

from core import MONEY, STRING_SIZE as SS

Model = models.Model


class AutoTimedMixin(Model):
    """
    Mixin class for models with automatically generated creation time and
    update time.

    Fields:
        created_at: A Django datetime object for creation time.
        updated_at: A Dajango datetime object for latest update time.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NamedMixin(Model):
    """
    Mixin class for models that needs a name.

    Fields:
        name: A string for the name.
    """
    name = models.CharField(max_length=SS['small'])

    class Meta:
        abstract = True


class User(AutoTimedMixin, NamedMixin):
    """
    User model.

    Inherites fields from: AutoTimedMixin, NamedMixin

    Relations:
        Many to many: Share
        One to Many: One User -> Many Expense
                     One User -> Many Expense Ratio
    """

    @property
    def paid_by(self) -> QuerySet:
        """
        Return a QuerySet of ``Expense`` paid by this user.
        """
        return Expense.objects.filter(paid_by=self).distinct()

    @property
    def paid_for(self) -> QuerySet:
        """
        Return a QuerySet of ``ExpenseRatio`` for this user.
        """
        return ExpenseRatio.objects.filter(user=self).distinct()

    @property
    def shares(self) -> QuerySet:
        """
        Returns a QuerySet of ``Share`` the user is in.
        """
        return Share.objects.filter(users__in=[self]).distinct()


class Share(AutoTimedMixin, NamedMixin):
    """
    Share model.

    Inherites fields from: AutoTimedMixin, NamedMixin

    Fields:
        description: A string for the description of this share.
        users: All users in this Share.

    Relations:
        Many to many: User
        One to many: One Share -> Many Expense
    """
    description = models.CharField(max_length=SS['medium'])
    users = models.ManyToManyField(User)


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
    updated_at = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=SS['medium'])
    share = models.ForeignKey(Share, on_delete=models.CASCADE)
    total = models.DecimalField(**MONEY)
    paid_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    resolved = models.BooleanField(default=False)

    @property
    def ratio(self) -> QuerySet:
        """
        Returns a QuerySet of ExpenseRatio that belongs to this Expense.
        """
        return ExpenseRatio.objects.filter(expense=self)

    def generate_ratio(self, paid_for: dict):
        """
        Generate a set of ``ExpenseRatio`` for this expense.

        :param paid_for: A dict of User to a tuple representing a fraction
                         like so {User: (numerator, denominator)}

        :return: A list of the generated ``ExpenseRatio``
        """
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
