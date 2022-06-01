---
title: 'Human Readable Passwords'
description: 'Code that allows you to create human-readable passwords.'
tags: Python, Django
series:
canonical_url:
---

## Introduction

For a Django application, I had to create passwords for users who sign up on a website. Generating passwords can be relatively easy.

Take a look at this function.

```python
def generate_password(length=10):
 return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
```

This is the result

```python
>>> print(generate_raw_password())
>>> B61CbF9GdW
```

This is secure but hard to remember.

To make them more user-friendly I thought I would create a function that is inspired by https://xkpasswd.net/s/. This website creates human-readable passwords which are secure. An example is `3~shoes~FOUND@` and this is much more human-readable than the previous method.

## Details

How did I go about creating the human-readable passwords?

### Word List

I had to start with a list of words. With Wordle being so popular finding a list of 5-letter words is not that hard. There are many Worlde clones and GitHub has a whole bunch of Wordle clones with such a list. But in all honesty why not go to the source of the original Wordle and see if you can get their list.

#### NY Times Wordle

The NY Times bought the original Wordle and the source is no longer available. You can still get the list with a little bit of hacking.
Open this link: https://www.nytimes.com/games/wordle/main.bd4cb59c.js. Search for `,Oa=` and there you have the start of the list. There are about 10K words in this list. When I checked the list I did find some words that people might find slightly inappropriate, d\*cks and that's not the bird, b\*\*by.

#### On your computer

I found another way to generate a list of 5-letter words. Most Linux-based machines and Macs have a words list on the system, `/usr/share/dict/words`. To extract all 5-letter words we can write a simple one-liner in Perl.

```perl
perl -nle 'print if /^[a-z]{5}$/' /usr/share/dict/words > words5.txt
```

And there we have a list. Unfortunately, the full list contains words from 1934 and I found some words in the list that we no longer use.

#### The Stanford GraphBase

Donald Knuth created a list of five-letter words. This list is used to run various combinatoric experiments, graph algorithms, and other algorithms to explore the relationships among these words. The list is in the public domain and has 5757 words.

This is the list I'm using right now to create the human-readable password.

#### Using the list

Instead of putting the word list in a Python list, I decided to put the list in a DB instead. This makes it easier to add more words later if that is preferred.

The model is super easy.

```py
# code/word_model.py

class Word(models.Model):
    word = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.word

```

I will leave it up to you on how to fill the model.

### Requirements

The password must meet the following requirements

- Prepend and append the password with at least 1 digit and at most 2 digits.
- Separate each word by a special character.
- Each word will go through a transformation of being either all lower case, all upper case, or capitalized.
- Do not repeat the words within the password.

I also want to have the flexibility of using as many words as I want, by default I'll use 3 and will not allow less than two words.

### Code

```py
# code/password.py

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

```

Some examples of passwords generated by this function:

```
73PYGMY|Glens~Naiad33
29radar|bylaw%SWATH19
5plant.Cages+Dizzy54
72DOUGH!Yolks-hooch28
92FLESH^churl%genet69
```

## Conclusion

The code allows you to create human-readable passwords. It is easy to expand the words used by adding them to the database.

**Notes**

- I use my selection of special characters instead of `string.punctuation`. I did not want certain characters from that list like the quotation marks.

**References**

- NY Times Wordle: https://www.nytimes.com/games/wordle/index.html
- The Stanford GraphBase: https://www-cs-faculty.stanford.edu/~knuth/sgb.html

### Found a typo?

If you've found a typo, a sentence that could be improved or anything else that should be updated on this blog post, you can access it through a git repository and make a pull request. Instead of posting a comment, please go directly to [GitHub](https://github.com/petervanderdoes/dev.to/tree/main/blog-posts/0002-human-readable-passwords) and open a new pull request with your changes.

---

###### Photo by Colin Lloyd - https://unsplash.com/photos/62OEfKjU1Vs
