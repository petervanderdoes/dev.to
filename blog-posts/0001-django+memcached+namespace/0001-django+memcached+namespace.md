---
published: true
title: 'Django + memcached + namespace'
cover_image: 'https://raw.githubusercontent.com/petervanderdoes/dev.to/main/blog-posts/0001-django+memcached+namespace/assets/cover.png'
description: 'Simulate namespace in memcached to allow for deletion of multiple mecached entries'
tags: Python, Django, memcached
series:
canonical_url:
---

## Introduction

One of the drawbacks of using memcached is that you can not delete keys using a wildcard. With Django, you can delete many keys but you have to give it a list of keys to delete.

A way around this is by using namespaces. You will organize keys by namespace. For example, every key related to the products you sell falls in the namespace _product_. And your clients are in a namespace _client_. If you delete the namespace all keys within the namespace will be deleted as well. Unfortunately, we run into another snag, namespaces are not supported by memcached.

With the code presented in this article we fake namespaces and have a way to "delete" all keys in a namespace

TL;DR Check out the code.

## How do we do this?

When we store data in memcached you need a key. What we will do is prepend this key with the namespace we want to use. For the key _guitar_, we will prepend the key like this _product:guitar_.

Wait! How will we invalidate all keys in the namespace _product_? Instead of using _product_ as the prefix, we will store the namespace in memcached with a value. We use that value as the actual namespace.

The namespace key for memcached will be _namespace:product_ and we store the value _1_. I hear you say it: "Ha, but that will cause a conflict with other namespaces". You are right so let us prepend this value with the namespace itself like this _product1_. Now the guitar key will look like this _product1:guitar_.
When we change the value of the _product_ value to _product2_, the guitar key will be _product2:guitar_. Now all keys in the namespace _product1_ will no longer be reachable and memcached will take care of removing them.

## Code

Wrapping this all up in a class to be used within Django

```py
# code/cache.py

import time

import xxhash
from django.core.cache import cache as django_cache


IS_DEVELOPMENT = False
CACHE_PREFIX = "MyApp"
HOUR = 3600
DAY = HOUR * 24


class MyCache:
    """
    This class is used to create a cache for MyApp.
    """

    def __init__(self, timeout=DAY):
        """
        Initialize the cache.
        """
        self.timeout = timeout if not IS_DEVELOPMENT else 20

    def __str__(self):
        """
        Return a string representation of the cache.
        """
        return "MyCache"

    def get(self, namespace, key):
        """
        Get a value from the cache.

        Parameters
        ----------
        namespace: str
        key: str
        """
        try:
            cache_key = self.safe_cache_key(namespace=namespace, key=key)
            return django_cache.get(cache_key)
        except Exception:
            return None

    def set(self, namespace, key, value, timeout=None):
        """
        Set a value in the cache.

        Parameters
        ----------
        namespace: str
        key: str
        value: str|int|dict|list
        timeout: int or None
        """
        try:
            cache_key = self.safe_cache_key(namespace=namespace, key=key)
            timeout = timeout or self.timeout
            django_cache.set(cache_key, value, timeout)
        except Exception:
            pass

    def delete(self, namespace, key):
        """
        Delete a value from the cache.

        Parameters
        ----------
        namespace: str
        key: str
        """
        try:
            cache_key = self.safe_cache_key(namespace=namespace, key=key)
            django_cache.delete(cache_key)
        except Exception:
            pass

    def delete_namespace(self, namespace):
        """
        Delete the namespace

        Parameters
        ----------
        namespace:str
        """
        self.update_cache_namespace(namespace=namespace)

    def safe_cache_key(self, namespace, key):
        """
        Create a key that is safe to use in memcached

        Parameters
        ----------
        namespace: str
        value: str

        Returns
        -------
        str
        """

        namespace = self.get_namespace(namespace=namespace)
        new_key = "{}:{}:{}".format(
            CACHE_PREFIX, namespace, xxhash.xxh3_64_hexdigest(key)
        )
        return new_key

    def get_namespace(self, namespace):
        """
        Get the namespace value for the given namespace

        Parameters
        ----------
        namespace: str

        Returns
        -------
        str
        """
        key = self.get_namespace_key(namespace=namespace)
        rv = django_cache.get(key)
        if rv is None:
            value = self.get_namespace_value(namespace=namespace)
            django_cache.add(key, value, DAY)
            # Fetch the value again to avoid a race condition if another
            # caller added a value between the first get() and the add()
            # above.
            return django_cache.get(key, value)

        return rv

    def update_cache_namespace(self, namespace):
        """
        Update the value for the namespace key
        Parameters
        ----------
        namespace: str
        """
        key = self.get_namespace_key(namespace=namespace)
        value = self.get_namespace_value(namespace=namespace)
        django_cache.set(key, value, DAY)

    def get_namespace_key(self, namespace):
        """

        Parameters
        ----------
        namespace: str

        Returns
        -------
        str
        """
        return xxhash.xxh3_64_hexdigest(f"namespace:{namespace}")

    def get_namespace_value(self, namespace):
        """
        Create value for the namespace value

        The namespace is used to make sure the hashed value is unique

        Parameters
        ----------
        namespace: str

        Returns
        -------
        str
        """
        namespace_value = namespace + str(int(round(time.time() * 1000)))
        return xxhash.xxh3_64_hexdigest(namespace_value)


cache = MyCache()

```

## Usage

**Set a value**

```python
cache.set("product", "combined_pricing", 5000)
```

**Get a value**

```python
pricing = cache.get("product", "combined_pricing")
```

**Delete single key**

```python
pricing = cache.delete("product", "combined_pricing")
```

**Delete namespace**

```python
cache.delete_namespace("product")
```

## Conclusion

Using this code allows you to group memcached keys and invalidate the keys in that namespace all at once.

**Notes**

- I hash all memcached keys as well as the namespace value because it is part of a key. Parts of the key are not predictable and could potentially have characters that are incompatible with a key.
- Using time for the namespace value eliminates the need for an increase method.
- I prefer xxhash over any other hasher, it's super fast.

**References**

- xxhash at PyPi: https://pypi.org/project/xxhash/

## Found a typo?

If you've found a typo, a sentence that could be improved or anything else that should be updated on this blog post, you can access it through a git repository and make a pull request. Instead of posting a comment, please go directly to [GitHub](https://github.com/petervanderdoes/dev.to/tree/main/blog-posts/0001-django+memcached+namespace) and open a new pull request with your changes.

---

###### Photo by Colin Lloyd - https://unsplash.com/photos/62OEfKjU1Vs
