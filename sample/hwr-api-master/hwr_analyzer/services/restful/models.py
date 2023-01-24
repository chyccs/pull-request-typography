from djongo import models


class Candidate(models.Model):
    rank = models.IntegerField(null=False)
    label = models.TextField(null=False)

    class Meta:
        abstract = True


class RecognizedWord(models.Model):
    label = models.TextField(null=False)
    candidates = models.ArrayField(model_container=Candidate)

    class Meta:
        abstract = True


class RecognizedDocument(models.Model):
    _id = models.ObjectIdField()
    section_code = models.IntegerField(null=False)
    owner_code = models.IntegerField(null=False)
    note_code = models.IntegerField(null=False)
    note_uuid = models.CharField(null=True, max_length=50, blank=True)  # skipcq: PTC-W0901
    page_number = models.IntegerField(null=False)
    user_id = models.CharField(null=True, max_length=50, blank=True)  # skipcq: PTC-W0901
    language = models.CharField(null=False, max_length=50)
    label = models.TextField(null=True, blank=True)  # skipcq: PTC-W0901
    words = models.ArrayField(
        model_container=RecognizedWord,
    )
    objects = models.DjongoManager()

    class Meta:
        db_table = "recognized_documents"


class RecognitionTaskStatus(models.TextChoices):
    PENDING = 'PENDING'
    DONE = 'DONE'
    FAILED = 'FAILED'


class RecognitionTasks(models.Model):
    _id = models.ObjectIdField()
    status = models.CharField(max_length=10,  # skipcq: PTC-W0901
                              choices=RecognitionTaskStatus.choices,
                              null=True,
                              blank=True)
    request = models.TextField(null=True, blank=True)  # skipcq: PTC-W0901
    result = models.TextField(null=True, blank=True)  # skipcq: PTC-W0901
    requested_by = models.CharField(max_length=30, null=True, blank=True)  # skipcq: PTC-W0901
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField()
    objects = models.DjongoManager()

    class Meta:
        db_table = "recognition_tasks"

    @property
    def task_id(self):
        return self._id
