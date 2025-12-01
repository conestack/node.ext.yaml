from node.behaviors import DefaultInit
from node.behaviors import MappingNode
from node.behaviors import SequenceAdopt
from node.behaviors import SequenceNode
from node.ext.fs import Directory
from node.ext.fs import join_fs_path
from node.ext.yaml import YamlCallableMember
from node.ext.yaml import YamlFile
from node.ext.yaml import YamlMapping
from node.ext.yaml import YamlMappingStorage
from node.ext.yaml import YamlMember
from node.ext.yaml import YamlRootStorage
from node.ext.yaml import YamlSequence
from node.ext.yaml import YamlSequenceStorage
from node.interfaces import IWildcardFactory
from node.tests import NodeTestCase
from odict import odict
from plumber import plumbing
from yaml.representer import RepresenterError
import os
import shutil
import sys
import tempfile
import unittest
import uuid


def temp_directory(fn):
    def wrapper(*a, **kw):
        tempdir = tempfile.mkdtemp()
        kw['tempdir'] = tempdir
        try:
            fn(*a, **kw)
        finally:
            shutil.rmtree(tempdir)
    return wrapper


class TestYamlMapping(YamlMapping):
    pass


TestYamlMapping.factories = {'*': TestYamlMapping}


class TestYamlSequence(YamlSequence):
    pass


TestYamlSequence.factories = {'*': TestYamlMapping}


class TestYaml(NodeTestCase):

    def test_YamlMember(self):
        # YamlMember is a wildcard factory
        @plumbing(YamlMember)
        class MappingMember:
            pass

        member = MappingMember()
        self.assertTrue(IWildcardFactory.providedBy(member))

        # YamlMember with mapping as storage
        @plumbing(YamlMember)
        class MappingMember:
            storage = dict()
            factories = dict()

        member = MappingMember()

        # __setitem__
        a = YamlMapping()
        b = YamlSequence()
        member['a'] = a
        member['b'] = b
        member['c'] = 'c'
        self.assertTrue(member.storage['a'] is a.storage)
        self.assertEqual(member.storage['a'], odict())
        self.assertTrue(member.storage['b'] is b.storage)
        self.assertEqual(member.storage['b'], list())
        self.assertEqual(member.storage['c'], 'c')

        # __getitem__, default
        self.assertEqual(member['a'], odict())
        self.assertEqual(member['b'], list())
        self.assertEqual(member['c'], 'c')

        # __getitem__, default factories defined
        member.default_mapping_factory = YamlMapping
        member.default_sequence_factory = YamlSequence
        self.assertIsInstance(member['a'], YamlMapping)
        self.assertIsInstance(member['b'], YamlSequence)
        self.assertEqual(member['c'], 'c')

        # __getitem__, factories take precedence over default factories
        class CustomMapping(YamlMapping):
            pass

        member.factories['a'] = CustomMapping
        self.assertIsInstance(member['a'], CustomMapping)

        # YamlMember with sequrence as storage
        @plumbing(YamlMember)
        class SequenceMember:
            storage = [None, None, None]
            factories = dict()

        member = SequenceMember()

        # __setitem__
        a = YamlMapping()
        b = YamlSequence()
        member[0] = a
        member[1] = b
        member[2] = 'c'
        self.assertTrue(member.storage[0] is a.storage)
        self.assertEqual(member.storage[0], odict())
        self.assertTrue(member.storage[1] is b.storage)
        self.assertEqual(member.storage[1], list())
        self.assertEqual(member.storage[2], 'c')

        # __getitem__, default
        self.assertEqual(member[0], odict())
        self.assertEqual(member[1], list())
        self.assertEqual(member[2], 'c')

        # __getitem__, default factories defined
        member.default_mapping_factory = YamlMapping
        member.default_sequence_factory = YamlSequence
        self.assertIsInstance(member[0], YamlMapping)
        self.assertIsInstance(member[1], YamlSequence)
        self.assertEqual(member[2], 'c')

        # __getitem__, factories take precedence over default factories
        member.factories['0'] = CustomMapping
        self.assertIsInstance(member[0], CustomMapping)

    @temp_directory
    def test_YamlRootStorage(self, tempdir):
        @plumbing(YamlRootStorage)
        class YamlRoot:
            @property
            def fs_path(self):
                return [tempdir, 'data.yaml']

        root = YamlRoot()
        storage = root.storage
        self.assertIsInstance(storage, odict)
        self.assertEqual(storage, odict())
        self.assertTrue(storage is root.storage)
        self.assertFalse(os.path.exists(join_fs_path(root)))

        root()
        self.assertTrue(os.path.exists(join_fs_path(root)))
        with open(join_fs_path(root)) as f:
            self.assertEqual(f.read(), '{}\n')

        storage['foo'] = 'bar'
        root()
        self.assertTrue(os.path.exists(join_fs_path(root)))
        with open(join_fs_path(root)) as f:
            self.assertEqual(f.read(), 'foo: bar\n')

        root = YamlRoot()
        self.assertEqual(root.storage, odict([('foo', 'bar')]))

        root = YamlRoot()
        storage = root.storage
        storage['bar'] = uuid.UUID('5906c219-31db-425d-964a-358a1e3f4183')
        with self.assertRaises(RepresenterError):
            root()
        with open(join_fs_path(root)) as f:
            self.assertEqual(f.read(), 'foo: bar\n')
        storage['bar'] = '5906c219-31db-425d-964a-358a1e3f4183'

        root()
        with open(join_fs_path(root)) as f:
            self.assertEqual(f.read().split('\n'), [
                'foo: bar',
                'bar: 5906c219-31db-425d-964a-358a1e3f4183',
                ''
            ])

    def test_YamlMappingStorage(self):
        @plumbing(DefaultInit, MappingNode, YamlMappingStorage)
        class YamlMappingMember:
            pass

        member = YamlMappingMember()
        self.assertIsInstance(member.storage, odict)
        self.assertEqual(member.storage, odict())

        parent = YamlMappingMember()
        parent.storage['name'] = odict()
        member = YamlMappingMember(name='name', parent=parent)
        self.assertTrue(member.storage is parent.storage['name'])

    def test_YamlSequenceStorage(self):
        @plumbing(DefaultInit, SequenceAdopt, SequenceNode, YamlSequenceStorage)
        class YamlSequenceMember:
            pass

        member = YamlSequenceMember()
        self.assertIsInstance(member.storage, list)
        self.assertEqual(member.storage, list())

        parent = YamlSequenceMember()
        parent.storage.insert(0, list())
        member = YamlSequenceMember(name='0', parent=parent)
        self.assertTrue(member.storage is parent.storage[0])

        parent['0'] = 'value'
        self.assertEqual(parent.storage, ['value'])

        with self.assertRaises(NotImplementedError):
            parent[:]
        with self.assertRaises(NotImplementedError):
            parent[:] = []

        value_a = object()
        value_b = YamlSequenceMember()
        value_c = YamlSequenceMember()
        parent.append(value_a)
        parent.append(value_b)
        self.assertTrue(value_a in parent)
        self.assertTrue(value_b in parent)
        self.assertFalse(value_c in parent)

    @temp_directory
    def test_YamlFile(self, tempdir):
        class TestYamlFile(YamlFile):
            factories = {
                '*': TestYamlMapping,
                'sequence': TestYamlSequence
            }

            @property
            def fs_path(self):
                return [tempdir, 'data.yaml']

        file = TestYamlFile()

        self.assertRaises(KeyError, file.__getitem__, 'inexistent')
        file['foo'] = 'bar'
        self.assertEqual(file.storage, odict([('foo', 'bar')]))

        mapping = TestYamlMapping()
        mapping['baz'] = 'bam'
        file['mapping'] = mapping
        self.assertTrue(mapping.storage is file.storage['mapping'])
        self.assertEqual(
            file.storage,
            odict([('foo', 'bar'), ('mapping', odict([('baz', 'bam')]))])
        )

        sub = TestYamlMapping()
        mapping['sub'] = sub
        self.assertTrue(sub.storage is file.storage['mapping']['sub'])
        self.assertEqual(file.storage, odict([
            ('foo', 'bar'),
            ('mapping', odict([
                ('baz', 'bam'),
                ('sub', odict())
            ]))
        ]))

        with self.assertRaises(TypeError):
            sub()

        sequence = file['sequence'] = TestYamlSequence()
        sequence.insert(0, TestYamlMapping())
        self.assertTrue(sequence.storage is file.storage['sequence'])
        self.assertEqual(file.storage, odict([
            ('foo', 'bar'),
            ('mapping', odict([
                ('baz', 'bam'),
                ('sub', odict())
            ])),
            ('sequence', [odict()])
        ]))

        file()
        with open(join_fs_path(file)) as f:
            self.assertEqual(f.read().split('\n'), [
                'foo: bar',
                'mapping:',
                '  baz: bam',
                '  sub: {}',
                'sequence:',
                '- {}',
                ''
            ])

        file = TestYamlFile()
        self.assertEqual(file.keys(), ['foo', 'mapping', 'sequence'])
        self.assertEqual(file['foo'], 'bar')
        self.assertIsInstance(file['mapping'], YamlMapping)

        self.checkOutput("""
        <class '...TestYamlFile'>: None
        __foo: 'bar'
        __<class '...TestYamlMapping'>: mapping
        ____baz: 'bam'
        ____<class '...TestYamlMapping'>: sub
        __<class 'node.ext.yaml.tests.test_yaml.TestYamlSequence'>: sequence
        ____<class 'node.ext.yaml.tests.test_yaml.TestYamlMapping'>: 0
        """, file.treerepr(prefix='_'))

        file.factories = dict()
        self.assertEqual(
            file['mapping'],
            odict([('baz', 'bam'), ('sub', odict())])
        )

        del file['mapping']
        del file['sequence']
        file()
        with open(join_fs_path(file)) as f:
            self.assertEqual(f.read().split('\n'), [
                'foo: bar',
                ''
            ])

        del file['foo']
        file()
        with open(join_fs_path(file)) as f:
            self.assertEqual(f.read(), '{}\n')

    @temp_directory
    def test_YamlCallableMember(self, tempdir):
        class TestYamlFile(YamlFile):
            @property
            def fs_path(self):
                return [tempdir, 'data.yaml']

        @plumbing(YamlCallableMember)
        class TestYamlMember(YamlMapping):
            pass

        file = TestYamlFile()
        child = file['child'] = TestYamlMember()
        child()
        with open(join_fs_path(file)) as f:
            self.assertEqual(f.read().split('\n'), [
                'child: {}',
                ''
            ])

    @temp_directory
    def test_MappingOrder(self, tempdir):
        # XXX: Order behavior only works with node children right now.
        #      Either extend Order behavior to also support keys or implement
        #      dedicated YamlOrder providing this.
        class TestYamlFile(YamlFile):
            factories = {
                '*': TestYamlMapping
            }

            @property
            def fs_path(self):
                return [tempdir, 'data.yaml']

        file = TestYamlFile()
        file['a'] = TestYamlMapping()
        file['b'] = TestYamlMapping()
        self.assertEqual(file.keys(), ['a', 'b'])

        file.swap(file['a'], file['b'])
        self.assertEqual(file.keys(), ['b', 'a'])

        file()
        with open(join_fs_path(file)) as f:
            self.assertEqual(f.read().split('\n'), [
                'b: {}',
                'a: {}', ''
            ])

        file = TestYamlFile()
        self.assertEqual(file.keys(), ['b', 'a'])
        file.swap(file['a'], file['b'])
        self.assertEqual(file.keys(), ['a', 'b'])

        file()
        with open(join_fs_path(file)) as f:
            self.assertEqual(f.read().split('\n'), [
                'a: {}',
                'b: {}', ''
            ])

    @temp_directory
    def test_SequenceOrder(self, tempdir):
        class TestYamlFile(YamlFile):
            factories = {
                '*': TestYamlSequence
            }

            @property
            def fs_path(self):
                return [tempdir, 'data.yaml']

        file = TestYamlFile()
        sequence = file['sequence'] = TestYamlSequence()
        sequence.factories = dict()
        sequence.default_mapping_factory = TestYamlMapping
        sequence.default_sequence_factory = TestYamlSequence

        mapping_member = TestYamlMapping()
        sequence.append(mapping_member)
        sequence_member = TestYamlSequence()
        sequence.append(sequence_member)
        string_member = 'NO NODE'
        sequence.append(string_member)
        self.assertEqual(sequence.storage, [odict(), [], 'NO NODE'])

        sequence.swap(0, 1)
        self.assertEqual(sequence.storage, [[], odict(), 'NO NODE'])
        sequence.swap(2, 0)
        self.assertEqual(sequence.storage, ['NO NODE', odict(), []])
        sequence.movefirst(1)
        self.assertEqual(sequence.storage, [odict(), 'NO NODE', []])
        sequence.movelast(1)
        self.assertEqual(sequence.storage, [odict(), [], 'NO NODE'])
        sequence.movebefore(2, 1)
        self.assertEqual(sequence.storage, [odict(), 'NO NODE', []])
        sequence.moveafter(0, 1)
        self.assertEqual(sequence.storage, ['NO NODE', odict(), []])

        with self.assertRaises(ValueError):
            sequence.insertfirst(sequence[2])
        with self.assertRaises(ValueError):
            sequence.insertlast(sequence[0])
        with self.assertRaises(ValueError):
            sequence.insertbefore(sequence[2], sequence[0])
        with self.assertRaises(ValueError):
            sequence.insertafter(sequence[0], sequence[2])

        sequence.insertfirst('FIRST')
        self.assertEqual(
            sequence.storage,
            ['FIRST', 'NO NODE', odict(), []]
        )
        sequence.insertlast('LAST')
        self.assertEqual(
            sequence.storage,
            ['FIRST', 'NO NODE', odict(), [], 'LAST']
        )
        sequence.insertbefore('BEFORE', 1)
        self.assertEqual(
            sequence.storage,
            ['FIRST', 'BEFORE', 'NO NODE', odict(), [], 'LAST']
        )
        sequence.insertafter('AFTER', 2)
        self.assertEqual(
            sequence.storage,
            ['FIRST', 'BEFORE', 'NO NODE', 'AFTER', odict(), [], 'LAST']
        )

    @temp_directory
    def test_FSLocation(self, tempdir):
        class TestDirectory(Directory):
            default_file_factory = YamlFile

        container = TestDirectory(fs_path=[tempdir])
        container['file.yaml'] = YamlFile()
        container()

        self.assertTrue(os.path.exists(os.path.join(tempdir, 'file.yaml')))

        container = TestDirectory(fs_path=[tempdir])
        self.assertIsInstance(container['file.yaml'], YamlFile)
