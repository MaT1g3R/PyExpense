from django.db import models


# Create your models here.
class TimedMixin:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Share(models.Model, TimedMixin):
    name = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=256)
    users = models.ManyToManyField(User)


class User(models.Model, TimedMixin):
    name = models.CharField(unique=True, max_length=64)
    expenses = models.ManyToManyField(Expense)


class ExpenseRatio(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    numerator = models.PositiveIntegerField()
    denominator = models.PositiveIntegerField()
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)


class Expense(models.Model, TimedMixin):
    description = models.CharField(max_length=256)
    share = models.ForeignKey(Share, on_delete=models.CASCADE)
    total = models.FloatField()
    paid_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    resolved = models.BooleanField(default=False)
