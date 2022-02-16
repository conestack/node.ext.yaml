from .behaviors import YamlCallableMember  # noqa
from .behaviors import YamlMappingStorage
from .behaviors import YamlRootStorage
from .behaviors import YamlSequenceStorage
from node.behaviors import Adopt
from node.behaviors import DefaultInit
from node.behaviors import MappingNode
from node.behaviors import Order
from node.behaviors import SequenceNode
from plumber import plumbing


@plumbing(
    Adopt,
    DefaultInit,
    MappingNode,
    Order,
    YamlMappingStorage)
class YamlMapping:
    """A YAML mapping node.
    """


# B/C 2022-02-16
YamlNode = YamlMapping


@plumbing(
    DefaultInit,
    SequenceNode,
    YamlSequenceStorage)
class YamlSequence:
    """A YAML sequence node.
    """


@plumbing(
    Adopt,
    DefaultInit,
    MappingNode,
    Order,
    YamlRootStorage)
class YamlFile:
    """A YAML file.
    """
