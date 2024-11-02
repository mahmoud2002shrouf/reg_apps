from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model() 

class Student(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True)
    


class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    prerequisites = models.ManyToManyField(
        'self',
        through='Prerequisite',
        symmetrical=False,
        related_name='course_prerequisites',
        blank=True
        
    )
    instructor = models.CharField(max_length=100)
    capacity = models.IntegerField()
    scheduleId = models.ForeignKey('CourseSchedule', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)


class Prerequisite(models.Model):
    course = models.ForeignKey('Course', related_name='required_for', on_delete=models.CASCADE)
    prerequisite = models.ForeignKey('Course', related_name='prerequisites_for', on_delete=models.CASCADE)

class CourseSchedule(models.Model):
    days = models.CharField(max_length=50)
    startTime = models.TimeField()
    endTime = models.TimeField()
    roomNo = models.CharField(max_length=10,)

class StudentRegistration(models.Model):
    studentId = models.ForeignKey('Student', on_delete=models.CASCADE)
    courseId = models.ForeignKey('Course', on_delete=models.CASCADE)
