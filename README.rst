Kalpa
#####

Kalpa provides a starting point for resource traversal in Pyramid. It provides
two classes for this, a :code:`Branch` and a :code:`Leaf`, which allow you to
create arbitrary resource trees without the boilerplate.

There is also a :code:`Root` class for added convenience that accepts a
request during initialization. This can be used to create a starting point for
Pyramid's traversal.

.. code-block:: python

    from kalpa import Root, Branch, Leaf

    USERS = {...}


    @Root.attach('users')
    class UserCollection(Branch):
        """User collection, for listings, or loading single users."""

        def __load__(self, key):
            """Return child resource with requested user included."""
            user = USERS[key]  # Load user or raise KeyError.
            return self._child(key, user=user)


    @UserCollection.child_resource
    class User(Branch):
        """User resource, a single loaded user."""


    @User.attach('gallery', aliases=['images'])
    class UserGallery(Leaf):
        """Gallery of images posted by a user.

        Reachable as `/users/:id/gallery` but also `/users/:id/images`.
        """
