Kalpa
#####

Kalpa provides a starting point for resource traversal in Pyramid. It provides
two classes for this, a :code:`Branch` and a :code:`Leaf`, which allow you to
create arbitrary resource trees without the boilerplate.

There is also a :code:`Root` class for added convenience that accepts a
request during initialization. This can be used to create a starting point for
Pyramid's traversal.

.. code-block:: python

    from kalpa import Root, Node, branch

    USERS = {...}


    class Root(Root):
        """Root resource for Pyramid traversal."""
        users = branch('UserCollection')


    class UserCollection(Node):
        """User collection, for listings, or loading single users."""
        __child_cls__ = 'User'

        def __load__(self, key):
            """Returns dict with attributes to create a child node from."""
            return {'user': USERS[key]}  # Load user or raise KeyError.


    class User(Node):
        """User resource, a single loaded user."""
        gallery = branch('UserGallery', aliases=['images'])


    class UserGallery(Node):
        """Gallery of images posted by a user.

        Reachable as `/users/:id/gallery` but also `/users/:id/images`.
        """
