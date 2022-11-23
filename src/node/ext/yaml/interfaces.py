from node.ext.fs.interfaces import IFile
from node.interfaces import IMappingStorage
from node.interfaces import ISequenceStorage
from node.interfaces import IWildcardFactory
from zope.interface import Attribute


class IYamlMember(IWildcardFactory):
    """YAML member interface.
    """

    factories = Attribute('Dictionary defining child factories.')

    default_mapping_factory = Attribute(
        'Default factory for mapping members. Defaults to None.'
    )

    default_sequence_factory = Attribute(
        'Default factory for sequence members. Defaults to None.'
    )

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


class IYamlRoot(IMappingStorage, IFile, IYamlMember):
    """YAML root storage interface."""
