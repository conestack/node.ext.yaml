from node.ext.yaml import YamlFile
from node.ext.yaml import YamlMemberStorage
from node.ext.yaml import YamlNode
from node.ext.yaml import YamlRootStorage
from node.tests import NodeTestCase
from odict import odict
from plumber import plumbing
import os
import shutil
import sys
import tempfile
import unittest


def temp_directory(fn):
    def wrapper(*a, **kw):
        tempdir = tempfile.mkdtemp()
        kw['tempdir'] = tempdir
        try:
            fn(*a, **kw)
        finally:
            shutil.rmtree(tempdir)
    return wrapper


class TestYaml(NodeTestCase):

    @temp_directory
    def test_YamlRootStorage(self, tempdir):
        @plumbing(YamlRootStorage)
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
        self.assertFalse(os.path.exists(root.fs_path))
        storage['foo'] = 'bar'
        root()
        self.assertTrue(os.path.exists(root.fs_path))
        with open(root.fs_path) as f:
            self.assertEqual(f.read(), 'foo: bar\n')
        root = YamlRoot()
        self.assertEqual(root.storage, odict([('foo', 'bar')]))

    def test_YamlMemberStorage(self):
        @plumbing(YamlMemberStorage)
        class YamlMember:
            def __init__(self, name=None, parent=None):
                self.name = name
                self.parent = parent

        member = YamlMember()
        self.assertIsInstance(member.storage, odict)
        self.assertEqual(member.storage, odict())

        parent = YamlMember()
        parent.storage['name'] = odict()
        member = YamlMember(name='name', parent=parent)
        self.assertTrue(member.storage is parent.storage['name'])

    @temp_directory
    def test_YamlStorage(self, tempdir):
        class TestYamlFile(YamlFile):
            @property
            def fs_path(self):
                return os.path.join(tempdir, 'data.yaml')

        file = TestYamlFile()
        self.assertEqual(file.factories, {'*': YamlNode})

        self.assertRaises(KeyError, file.__getitem__, 'inexistent')
        file['foo'] = 'bar'
        self.assertEqual(file.storage, odict([('foo', 'bar')]))

        child = YamlNode()
        child['baz'] = 'bam'
        file['child'] = child
        self.assertTrue(child.storage is file.storage['child'])
        self.assertEqual(
            file.storage,
            odict([('foo', 'bar'), ('child', odict([('baz', 'bam')]))])
        )

        sub = YamlNode()
        child['sub'] = sub
        self.assertTrue(sub.storage is file.storage['child']['sub'])
        self.assertEqual(file.storage, odict([
            ('foo', 'bar'),
            ('child', odict([
                ('baz', 'bam'),
                ('sub', odict())
            ]))
        ]))

        sub()
        with open(file.fs_path) as f:
            self.assertEqual(f.read().split('\n'), [
                'foo: bar',
                'child:',
                '  baz: bam',
                '  sub: {}',
                ''
            ])

        file = TestYamlFile()
        self.assertEqual(file.keys(), ['foo', 'child'])
        self.assertEqual(file['foo'], 'bar')
        self.assertIsInstance(file['child'], YamlNode)

        self.checkOutput("""
        <class '...TestYamlFile'>: None
          <class 'node.ext.yaml.YamlNode'>: child
            baz: 'bam'
            <class 'node.ext.yaml.YamlNode'>: sub
          foo: 'bar'
        """, file.treerepr())

        file.factories = dict()
        self.assertEqual(file['child'], odict([('baz', 'bam'), ('sub', odict())]))

    @temp_directory
    def test_Order(self, tempdir):
        # XXX: Order behavior only works with node children right now.
        #      Either extend Order behavior to also support keys or implement
        #      dedicated YamlOrder providing this.
        class TestYamlFile(YamlFile):
            @property
            def fs_path(self):
                return os.path.join(tempdir, 'data.yaml')

        file = TestYamlFile()
        file['a'] = YamlNode()
        file['b'] = YamlNode()
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
