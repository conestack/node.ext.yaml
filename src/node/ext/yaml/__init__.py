from .behaviors import YamlCallableMember  # noqa
from .behaviors import YamlMemberStorage
from .behaviors import YamlRootStorage
from node.behaviors import Adopt
from node.behaviors import DefaultInit
from node.behaviors import Nodify
from node.behaviors import Order
from plumber import plumbing


@plumbing(
    Adopt,
    DefaultInit,
    Nodify,
    Order,
    YamlMemberStorage)
class YamlNode:
    """A YAML node.
    """


@plumbing(
    Adopt,
    DefaultInit,
    Nodify,
    Order,
    YamlRootStorage)
class YamlFile:
    """A YAML file.
    """
