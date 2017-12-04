from django.db import models
from django.db.models import QuerySet

from core.constants import MONEY, SS

Model = models.Model


class AutoTimedMixin:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class User(Model, AutoTimedMixin):
    name = models.CharField(unique=True, max_length=SS['small'])
    expenses = models.ManyToManyField('Expense')

    @property
    def shares(self) -> QuerySet:
        """
        Set of ``Share`` the user is in.
        """
        return Share.objects.filter(users__in=[self]).distinct()


class Share(Model, AutoTimedMixin):
    name = models.CharField(unique=True, max_length=SS['small'])
    description = models.CharField(max_length=SS['medium'])
    users = models.ManyToManyField(User)


class Expense(Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=SS['medium'])
    share = models.ForeignKey(Share, on_delete=models.CASCADE)
    total = models.DecimalField(**MONEY)
    paid_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    resolved = models.BooleanField(default=False)

    @property
    def ratio(self) -> QuerySet:
        return ExpenseRatio.objects.filter(expense=self)

    def generate_ratio(self, paid_for):
        for user, (top, bot) in paid_for.items():
            ExpenseRatio.objects.create(user=user, numerator=top,
                                        denominator=bot, expense=self)


class ExpenseRatio(Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    numerator = models.PositiveIntegerField()
    denominator = models.PositiveIntegerField()
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
