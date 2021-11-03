from node.behaviors import Adopt
from node.behaviors import DefaultInit
from node.behaviors import Nodify
from node.behaviors import Storage
from node.interfaces import IStorage
from node.utils import instance_property
from odict import odict
from plumber import default
from plumber import finalize
from plumber import override
from plumber import plumb
from plumber import plumbing
from zope.interface import implementer
import os
import yaml


class OrderedLoader(yaml.SafeLoader):

    @staticmethod
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return odict(loader.construct_pairs(node))


OrderedLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    OrderedLoader.construct_mapping
)


def ordered_load(stream):
    return yaml.load(stream, OrderedLoader)


class OrderedDumper(yaml.SafeDumper):

    @staticmethod
    def odict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items()
        )


OrderedDumper.add_representer(
    odict,
    OrderedDumper.odict_representer
)


def ordered_dump(data, stream=None, **kw):
    return yaml.dump(data, stream, OrderedDumper, **kw)


class IYamlStorage(IStorage):
    """YAML storage interface.
    """


class IYamlRoot(IYamlStorage):
    """YAML root storage interface
    """


class IYamlMember(IYamlStorage):
    """YAML member storage interface
    """


@implementer(IYamlStorage)
class YamlStorage(Storage):
    factories = default({})

    @override
    def __getitem__(self, name):
        val = self.storage[name]
        if isinstance(val, odict):
            factory = self.factories.get(name, self.factories.get('*'))
            if factory is not None:
                val = factory(name=name, parent=self)
        return val

    @override
    def __setitem__(self, name, val):
        if IYamlMember.providedBy(val):
            val = val.storage
        self.storage[name] = val

    @override
    def __call__(self):
        yaml_root = self.acquire(IYamlRoot)
        if yaml_root:
            yaml_root()


@implementer(IYamlRoot)
class YamlRootStorage(YamlStorage):

    @default
    @property
    def fs_path(self):
        msg = 'Abstract ``YamlRoot`` does not implement ``fs_path``'
        raise NotImplementedError(msg)

    @finalize
    @instance_property
    def storage(self):
        if os.path.exists(self.fs_path):
            with open(self.fs_path) as f:
                return ordered_load(f.read())
        return odict()

    @finalize
    def __call__(self):
        if self.storage:
            with open(self.fs_path, 'w') as f:
                f.write(ordered_dump(self.storage, sort_keys=False))


@implementer(IYamlMember)
class YamlMemberStorage(YamlStorage):

    @plumb
    def __init__(next_, self, **kw):
        next_(self, **kw)
        name = self.name
        parent = self.parent
        if parent and name in parent.storage:
            self._storage = parent.storage[name]
        else:
            self._storage = odict()

    @finalize
    @property
    def storage(self):
        return self._storage


@plumbing(
    Adopt,
    DefaultInit,
    Nodify,
    YamlMemberStorage)
class YamlNode:
    """A YAML node.
    """


YamlNode.factories = {'*': YamlNode}


@plumbing(
    Adopt,
    DefaultInit,
    Nodify,
    YamlRootStorage)
class YamlFile:
    """A YAML file.
    """
    factories = {'*': YamlNode}
