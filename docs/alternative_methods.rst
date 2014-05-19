========================================================
Using alternative implementations of get or pack methods
========================================================

packman provides a way to override the basic implementations for the get and pack methods for each component.

let's look at the example:

- we have a components file in our cwd with a ``riemann`` component.
- we want to run a different ``get`` method than the default one.
- we create a get.py file in our cwd with a function called ``get_riemann``.
- this will override the get method when running ``pkm get -c riemann``
- same goes for the ``pack`` method.
- of course, a user can create a specific get function only to extend the base get method by importing the ***get*** method from packman and adding to it.

for an example, see an example `get <https://github.com/cloudify-cosmo/packman/blob/develop/packman/examples/get.py>`_ file.