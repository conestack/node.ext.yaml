.. image:: https://img.shields.io/pypi/v/node.ext.yaml.svg
    :target: https://pypi.python.org/pypi/node.ext.yaml
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/node.ext.yaml.svg
    :target: https://pypi.python.org/pypi/node.ext.yaml
    :alt: Number of PyPI downloads

``node.ext.yaml`` provides a node implementation to yaml files.

For more information on nodes see `node <http://pypi.python.org/pypi/node>`_
package.

For more information on plumbing see
`plumber <http://pypi.python.org/pypi/plumber>`_ package.


Usage
-----

Create a yaml file:

.. code-block:: python

    from node.ext.yaml import YamlFile
    from node.ext.yaml import YamlNode

    class MyYamlFile(YamlFile):

        @property
        def fs_path(self):
            return '/path/to/file.yaml'

    file = MyYamlFile()
    file['child'] = YamlNode()

    # write file to disk
    file()

Define factories for child nodes:

.. code-block:: python

    class SpecificChild(YamlNode):
        pass

    class DefaultChild(YamlNode):
        pass

    class MyYamlFile(YamlFile):
        factories = {
            'child': SpecificChild,
            '*': DefaultChild
        }

Define a schema for node members:

.. code-block:: python

    from node import schema
    from node.behaviors import SchemaAsAttributes
    from plumber import plumbing

    @plumbing(SchemaAsAttributes)
    class MyYamlFile(YamlFile):
        schema = {
            'int_member': schema.Int(),
            'str_member': schema.Str()
        }

    file = MyYamlFile()
    file.attr['int_member'] = 1
    file.attr['str_member'] = 'String'


Python Versions
===============

- Python 2.7, 3.3+


Contributors
============

- Robert Niederreiter
