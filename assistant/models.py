from django.db import models
from django.contrib.auth.models import User


# ==========================================
# USER PROFILE
# ==========================================

class UserProfile(models.Model):

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# ==========================================
# FAQ
# ==========================================

class FAQ(models.Model):

    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question


# ==========================================
# NOTICE
# ==========================================

class Notice(models.Model):

    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


# ==========================================
# TIMETABLE
# ==========================================

class Timetable(models.Model):

    TIMETABLE_TYPE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
    )

    timetable_type = models.CharField(
        max_length=20,
        choices=TIMETABLE_TYPE_CHOICES,
        default='student'
    )

    day = models.CharField(max_length=20)

    subject = models.CharField(max_length=100)

    start_time = models.TimeField()

    end_time = models.TimeField()

    classroom = models.CharField(
        max_length=50,
        default='Not Assigned'
    )

    def __str__(self):
        return f"{self.timetable_type} - {self.day} - {self.subject}"


# ==========================================
# ASSIGNMENT
# ==========================================

class Assignment(models.Model):

    title = models.CharField(max_length=255)

    subject = models.CharField(max_length=100)

    description = models.TextField(
        blank=True
    )

    due_date = models.DateField()

    def __str__(self):
        return self.title