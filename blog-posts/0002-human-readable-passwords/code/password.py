import random

from models import Word


def create_password(words=3):
    """
    Generate a password

    Parameters
    ----------
    words: int

    Returns
    -------
    str
    """
    if words < 2:
        raise ValueError
    numbers = random.sample(range(1, 99), 2)
    special_character = "!@$%^&*-_+=:|~?/.;"
    separator = random.sample(special_character, words - 1)
    selected_words = get_random_words(words)
    password = str(numbers[0])
    for step in range(words - 1):
        password = password + transform_word(selected_words[step]) + separator[step]
    password = password + transform_word(selected_words[words - 1]) + str(numbers[1])
    return password


def get_random_words(amount):
    """
    Get a list of unique words

    Parameters
    ----------
    amount: int

    Returns
    -------
    list of str

    """
    total_word_count = Word.objects.all().count()
    ids = random.sample(range(1, total_word_count), amount)
    selected_words = list(
        Word.objects.filter(id__in=ids).values_list("word", flat=True)
    )
    while len(selected_words) < amount:
        id = random.randint(1, total_word_count)
        if id in ids:
            continue
        selected_word = Word.objects.get(id=id)
        if selected_word:
            selected_words.append(selected_word.word)
    return selected_words


def transform_word(word):
    """
    Transform a string

    Parameters
    ----------
    word: str

    Returns
    -------
    str
    """
    transform = random.randint(1, 3)
    if transform == 1:
        transformed_word = word.capitalize()
    elif transform == 2:
        transformed_word = word.lower()
    elif transform == 3:
        transformed_word = word.upper()
    return transformed_word
