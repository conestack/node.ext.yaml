from .behaviors import YamlCallableMember  # noqa
from .behaviors import YamlMappingStorage
from .behaviors import YamlMember  # noqa
from .behaviors import YamlRootStorage
from .behaviors import YamlSequenceStorage
from node.behaviors import DefaultInit
from node.behaviors import MappingAdopt
from node.behaviors import MappingNode
from node.behaviors import MappingOrder
from node.behaviors import SequenceAdopt
from node.behaviors import SequenceNode
from node.behaviors import SequenceOrder
from plumber import plumbing


@plumbing(
    DefaultInit,
    MappingAdopt,
    MappingNode,
    MappingOrder,
    YamlMappingStorage)
class YamlMapping:
    """A YAML mapping node.
    """


# B/C 2022-02-16
YamlNode = YamlMapping


@plumbing(
    DefaultInit,
    SequenceAdopt,
    SequenceNode,
    SequenceOrder,
    YamlSequenceStorage)
class YamlSequence:
    """A YAML sequence node.
    """


@plumbing(
    DefaultInit,
    MappingAdopt,
    MappingNode,
    MappingOrder,
    YamlRootStorage)
class YamlFile:
    """A YAML file.
    """
