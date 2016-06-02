Kalpa
#####

Kalpa provides a starting point for resource traversal in Pyramid. It provides
two classes for this, a `Branch` and a `Leaf`, which allow you to create
arbitrary resource trees without the boilerplate.

.. code-block:: python

    from kalpa import Root, Branch, Leaf

    from . import model

    @Root.attach('users')
    class UserCollection(Branch):
        """User collection, for listings or loading specific ones."""
        def __getitem__(self, key):
            # Load user with SQLAlchemy session available on request
            user = self.request.db.query(model.User).get(key)
            return self._sprout(key, user=user)


    @UserCollection.child_resource
    class User(Branch):
        """User resource, a single loaded user."""


    @User.attach('images')
    class UserImageCollection(Leaf):
        """Collection of images posted by a user."""
