from node.behaviors import DefaultInit
from node.behaviors import MappingNode
from node.behaviors import SequenceNode
from node.ext.yaml import YamlCallableMember
from node.ext.yaml import YamlFile
from node.ext.yaml import YamlMapping
from node.ext.yaml import YamlMappingStorage
from node.ext.yaml import YamlRootStorage
from node.ext.yaml import YamlSequence
from node.ext.yaml import YamlSequenceStorage
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

    @temp_directory
    def test_YamlRootStorage(self, tempdir):
        @plumbing(DefaultInit, YamlRootStorage)
        class AbstractYamlRoot:
            pass

        self.assertRaises(
            NotImplementedError,
            lambda: AbstractYamlRoot().fs_path
        )

        @plumbing(YamlRootStorage)
        class YamlRoot:
            @property
            def fs_path(self):
                return os.path.join(tempdir, 'data.yaml')

        root = YamlRoot()
        storage = root.storage
        self.assertIsInstance(storage, odict)
        self.assertEqual(storage, odict())
        self.assertTrue(storage is root.storage)
        self.assertFalse(os.path.exists(root.fs_path))

        root()
        self.assertTrue(os.path.exists(root.fs_path))
        with open(root.fs_path) as f:
            self.assertEqual(f.read(), '{}\n')

        storage['foo'] = 'bar'
        root()
        self.assertTrue(os.path.exists(root.fs_path))
        with open(root.fs_path) as f:
            self.assertEqual(f.read(), 'foo: bar\n')

        root = YamlRoot()
        self.assertEqual(root.storage, odict([('foo', 'bar')]))

        root = YamlRoot()
        storage = root.storage
        storage['bar'] = uuid.UUID('5906c219-31db-425d-964a-358a1e3f4183')
        with self.assertRaises(RepresenterError):
            root()
        with open(root.fs_path) as f:
            self.assertEqual(f.read(), 'foo: bar\n')
        storage['bar'] = '5906c219-31db-425d-964a-358a1e3f4183'

        root()
        with open(root.fs_path) as f:
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
        @plumbing(DefaultInit, SequenceNode, YamlSequenceStorage)
        class YamlSequenceMember:
            pass

        member = YamlSequenceMember()
        self.assertIsInstance(member.storage, list)
        self.assertEqual(member.storage, list())

        parent = YamlSequenceMember()
        parent.storage.insert(0, list())
        member = YamlSequenceMember(name='0', parent=parent)
        self.assertTrue(member.storage is parent.storage[0])

    @temp_directory
    def test_YamlFile(self, tempdir):
        class TestYamlFile(YamlFile):
            factories = {
                '*': TestYamlMapping,
                'sequence': TestYamlSequence
            }

            @property
            def fs_path(self):
                return os.path.join(tempdir, 'data.yaml')

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
        with open(file.fs_path) as f:
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
        __<class 'node.ext.yaml.tests.TestYamlSequence'>: sequence
        ____<class 'node.ext.yaml.tests.TestYamlMapping'>: 0
        """, file.treerepr(prefix='_'))

        file.factories = dict()
        self.assertEqual(
            file['mapping'],
            odict([('baz', 'bam'), ('sub', odict())])
        )

        del file['mapping']
        del file['sequence']
        file()
        with open(file.fs_path) as f:
            self.assertEqual(f.read().split('\n'), [
                'foo: bar',
                ''
            ])

        del file['foo']
        file()
        with open(file.fs_path) as f:
            self.assertEqual(f.read(), '{}\n')

    @temp_directory
    def test_YamlCallableMember(self, tempdir):
        class TestYamlFile(YamlFile):
            @property
            def fs_path(self):
                return os.path.join(tempdir, 'data.yaml')

        @plumbing(YamlCallableMember)
        class TestYamlMember(YamlMapping):
            pass

        file = TestYamlFile()
        child = file['child'] = TestYamlMember()
        child()
        with open(file.fs_path) as f:
            self.assertEqual(f.read().split('\n'), [
                'child: {}',
                ''
            ])

    @temp_directory
    def test_Order(self, tempdir):
        # XXX: Order behavior only works with node children right now.
        #      Either extend Order behavior to also support keys or implement
        #      dedicated YamlOrder providing this.
        class TestYamlFile(YamlFile):
            factories = {
                '*': TestYamlMapping
            }

            @property
            def fs_path(self):
                return os.path.join(tempdir, 'data.yaml')

        file = TestYamlFile()
        file['a'] = TestYamlMapping()
        file['b'] = TestYamlMapping()
        self.assertEqual(file.keys(), ['a', 'b'])

        file.swap(file['a'], file['b'])
        self.assertEqual(file.keys(), ['b', 'a'])

        file()
        with open(file.fs_path) as f:
            self.assertEqual(f.read().split('\n'), [
                'b: {}',
                'a: {}', ''
            ])

        file = TestYamlFile()
        self.assertEqual(file.keys(), ['b', 'a'])
        file.swap(file['a'], file['b'])
        self.assertEqual(file.keys(), ['a', 'b'])

        file()
        with open(file.fs_path) as f:
            self.assertEqual(f.read().split('\n'), [
                'a: {}',
                'b: {}', ''
            ])


def test_suite():
    from node.ext.yaml import tests

    suite = unittest.TestSuite()

    suite.addTest(unittest.findTestCases(tests))

    return suite


def run_tests():
    from zope.testrunner.runner import Runner

    runner = Runner(found_suites=[test_suite()])
    runner.run()
    sys.exit(int(runner.failed))


if __name__ == '__main__':
    run_tests()
