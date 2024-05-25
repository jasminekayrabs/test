from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Module(models.Model):
    class ContentTypeChoices(models.TextChoices):
        SLIDES = 'SL', 'Slides'
        VIDEO = 'VD', 'Video'
        BOTH = 'BT', 'Both'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField()
    content_type = models.CharField(max_length=2, choices=ContentTypeChoices.choices, default=ContentTypeChoices.SLIDES)
    order = models.PositiveIntegerField(help_text="Order of the module in the course")
    is_unlocked = models.BooleanField(default=False, help_text="Whether the module is unlocked for viewing")

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Quiz(models.Model):
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=255)
    passing_score = models.PositiveIntegerField(default=50, help_text="Minimum score required to pass the quiz")

    def __str__(self):
        return f"Quiz for {self.module.title}"
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

def media_upload_to(instance, filename):
    # Files will be uploaded to MEDIA_ROOT/<module_type>/<course_id>/<module_id>/<filename>
    return '{0}/{1}/{2}/{3}'.format(instance.module.get_content_type_display().lower(), instance.module.course.id, instance.module.id, filename)

class Slide(models.Model):
    module = models.ForeignKey(Module, related_name='slides', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=media_upload_to, null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module.course.title} - {self.module.title} - {self.title}"

class UserModuleProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='user_progress')
    completed_module = models.BooleanField(default=False)
    completed_quiz = models.BooleanField(default=False)
    slides_viewed = models.JSONField(default=list)

    class Meta:
        unique_together = ['user', 'module']

    def __str__(self):
        return f"{self.user.username}'s progress in {self.module.title}"