class Word(models.Model):
    word = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.word
