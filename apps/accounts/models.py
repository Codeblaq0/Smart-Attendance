from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("role", "student")  # Everyone set to student
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("coordinator", "Coordinator"),
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    level = models.CharField(max_length=50)
    faculty = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    mat_no = models.CharField(max_length=20, unique=True)

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="student"
    )  # Student role field

    is_active = models.BooleanField(
        default=True
    )  # control student access (set to false and the student can't login)
    is_staff = models.BooleanField(
        default=False
    )  # staff access having the ability to log into /admin (lecturer access)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "mat_no"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

# Class session Test
class ClassSession(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"role": "student"},
        related_name="class_sessions",
    )
    reminder_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200)
    credits = models.IntegerField(default=3)
    level = models.CharField(max_length=50,  default="100")
    lecturer = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"is_superuser": True},
        related_name="courses",
    )

    def __str__(self):
        return f"{self.code} - {self.title}"


class RegisterCourse(models.Model):
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="register_courses",
        limit_choices_to={"role": "student"}, 
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="register_courses"
    )
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.mat_no} registered course {self.course.code}"
