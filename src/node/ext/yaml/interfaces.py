from node.interfaces import IMappingStorage
from node.interfaces import ISequenceStorage
from zope.interface import Attribute
from zope.interface import Interface


class IYamlMember(Interface):
    """YAML member interface.
    """

    factories = Attribute('Dictionary defining child factories.')

    def __getitem__(name):
        """"""

    def __setitem__(name, value):
        """"""


class IYamlMappingStorage(IMappingStorage, IYamlMember):
    """YAML mapping storage interface.

    Plumbing hooks:

    * ``__init__``
        Map storage to underlying data structure.
    """


class IYamlSequenceStorage(ISequenceStorage, IYamlMember):
    """YAML sequence storage interface.

    Plumbing hooks:

    * ``__init__``
        Map storage to underlying data structure.

    * ``__getitem__``
        XXX

    * ``__setitem__``
        XXX
    """


class IYamlRoot(IMappingStorage, IYamlMember):
    """YAML root storage interface."""
