from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.core.mail import send_mail
from django.dispatch import receiver
from examaltersys.exceptions import *

TYPE = [('examdutyofficer', 'EXAMDUTYOFFICER'),
        ('faculty', 'FACULTY'), ('admin', 'ADMIN')]

# 1


class Exam(models.Model):
    SUNDAY = 'SU'
    MONDAY = 'M'
    TUESDAY = 'T'
    WEDNESDAY = 'W'
    THURSDAY = 'T'
    FRIDAY = 'F'
    SATURDAY = 'S'
    DAY_OF_WEEK = [
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
    ]
    exam_name = models.CharField(max_length=30)
    day = models.CharField(max_length=10, choices=DAY_OF_WEEK, default=MONDAY)
    Date = models.DateField(null=True)
    start_time = models.TimeField(
        auto_now=False, auto_now_add=False)
    end_time = models.TimeField(
        auto_now=False, auto_now_add=False)
    duration = models.DurationField(null=True, blank=True)
    slot = models.CharField(max_length=15, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return "Exam Slot Object "+str(self.id-1)

    class Meta:
        ordering = (['Date', 'start_time'])
        verbose_name = 'Exam Slot'
        verbose_name_plural = 'Exam Slots'

    def get_verbose_name(object):
        return object._meta.verbose_name

# 2


class User_T(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=30, choices=TYPE,
                            default=None, blank=False)
    phno = models.CharField(max_length=10)
    DOB = models.DateField(null=True)
    photo = models.ImageField(
        upload_to='user', default=None, null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'User Type'
        verbose_name_plural = 'User Types'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Notification(
            user=self, notification="has been added as a" + str(self.type)+".").save()

# 3


class FacultyCount(models.Model):
    fac_count = models.ForeignKey(User_T, on_delete=models.DO_NOTHING)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'FacultyCountObject'
        verbose_name_plural = 'FacultyCountObjects'

# 4


class Course(models.Model):
    Course_ID = models.CharField(max_length=30)
    Course_name = models.CharField(max_length=40)
    description = models.CharField(max_length=100, null=True)
    credits = models.IntegerField(null=True)

    class Meta:
        ordering = ('Course_ID',)
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

# 5


class Room(models.Model):
    Room_ID = models.CharField(max_length=30)
    Block = models.CharField(max_length=30)
    capacity = models.IntegerField()

    class Meta:
        ordering = ('Room_ID',)
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'

# 6


class RoomAllocation(models.Model):
    room = models.ForeignKey(
        Room, on_delete=models.DO_NOTHING, default=None)
    faculty = models.ForeignKey(
        User_T, on_delete=models.DO_NOTHING, default=None)

    def __str__(self):
        return "RoomAllocation "+str(self.id)

    def clean(self):
        if(str(self.faculty.user.type) == 'faculty'):
            pass
        else:
            raise ValidationError("You are not an faculty")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Notification(
            user=self.faculty, Notification=str(self.faculty.user.username)+"has been alloted to room no" + str(self.room.Room_ID)+" for invigilation").save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Room Allocation'
        verbose_name_plural = 'Room Allocations'

# 7


class ExamAllocation(models.Model):
    exam = models.ForeignKey(
        Exam, on_delete=models.DO_NOTHING, default=None)
    course = models.ForeignKey(
        Course, on_delete=models.DO_NOTHING, default=None)
    room = models.ForeignKey(
        Room, on_delete=models.DO_NOTHING, default=None)

    def __str__(self):
        return "ExamAllocation "+str(self.id)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Exam Allocation'
        verbose_name_plural = 'Exam Allocations'

# 8


class TakeDuty(models.Model):
    exam = models.ForeignKey(
        ExamAllocation, on_delete=models.DO_NOTHING, default=None)
    faculty = models.ForeignKey(
        User_T, related_name='takers', on_delete=models.DO_NOTHING, default=None)
    status = models.CharField(
        max_length=30, null=True, blank=True, default='available')
    reason = models.CharField(
        max_length=100, null=True, blank=True, default='Nil', verbose_name='Reason(for unable to attend)')

    def clean(self):
        if(str(self.faculty.type) == 'faculty'):
            if(self.status == 'Available'):
                raise AvailableException(
                    str(self.faculty.user.username), "is available to take duty")
            elif(self.status == 'unable'):
                Notification(
                    user=self.faculty, notification=str(self.faculty.user.username)+"was unable to attend duty for "+str(self.exam.exam.id)).save()
            elif(self.status == 'completed'):
                Notification(
                    user=self.faculty, notification=str(self.faculty.user.username)+"has completed duty for"+str(self.exam.exam.id)).save()
            else:
                raise NameError("Not a valid status")
        else:
            raise ValidationError("You are not a faculty")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Notification(
            user=self.faculty, notification=str(self.faculty.user.username) + "have been assigned duty for " + str(self.exam.exam.id)).save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'TakeDuty'
        verbose_name_plural = 'TakeDuties'

 # 9


class TakeDutyCount(models.Model):
    exam_count = models.ForeignKey(
        TakeDuty, on_delete=models.DO_NOTHING, default=None)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'TakeDutyCountObject'
        verbose_name_plural = 'TakeDutyCountObjects'
# 10


class AssignDuty(models.Model):
    exam = models.ForeignKey(
        ExamAllocation, on_delete=models.DO_NOTHING, default=None)
    edo = models.ForeignKey(
        User_T, related_name='assigners', on_delete=models.DO_NOTHING, default=None)

    def clean(self):
        if(str(self.edo.user.type) == 'examdutyofficer'):
            pass
        else:
            raise ValidationError("You are not an examdutyofficer")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'AssignDuty'
        verbose_name_plural = 'AssignDuties'

# 11


class Notification(models.Model):
    user = models.ForeignKey(User_T, on_delete=models.CASCADE, default=None)
    notification = models.CharField(
        max_length=255)

    def __str__(self):
        return str(self.user)+" -Notification:"+self.notification

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

# 12


class NotificationCount(models.Model):
    notifycount = models.ForeignKey(
        Notification, on_delete=models.DO_NOTHING)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'TakeDutyCountObject'
        verbose_name_plural = 'TakeDutyCountObjects'
