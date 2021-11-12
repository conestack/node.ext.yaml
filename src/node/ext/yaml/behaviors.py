from ._yaml import ordered_dump
from ._yaml import ordered_load
from .interfaces import IYamlMember
from .interfaces import IYamlRoot
from .interfaces import IYamlStorage
from node.behaviors import Storage
from node.interfaces import ICallable
from node.utils import instance_property
from odict import odict
from plumber import Behavior
from plumber import default
from plumber import finalize
from plumber import override
from plumber import plumb
from zope.interface import implementer
import os


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


@implementer(IYamlRoot, ICallable)
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
            data = ordered_dump(self.storage, sort_keys=False)
            with open(self.fs_path, 'w') as f:
                f.write(data)


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


@implementer(ICallable)
class YamlCallableMember(Behavior):

    @override
    def __call__(self):
        yaml_root = self.acquire(IYamlRoot)
        if yaml_root:
            yaml_root()
