from django.db import models


class AutoTimedMixin:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class User(models.Model, AutoTimedMixin):
    name = models.CharField(unique=True, max_length=64)
    expenses = models.ManyToManyField('Expense')


class Share(models.Model, AutoTimedMixin):
    name = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=256)
    users = models.ManyToManyField(User)


class Expense(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=256)
    share = models.ForeignKey(Share, on_delete=models.CASCADE)
    total = models.FloatField()
    paid_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    resolved = models.BooleanField(default=False)


class ExpenseRatio(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    numerator = models.PositiveIntegerField()
    denominator = models.PositiveIntegerField()
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
