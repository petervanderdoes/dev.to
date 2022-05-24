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
