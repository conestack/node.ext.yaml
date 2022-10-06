Changes
=======

0.2 (2022-10-06)
----------------

- Inherit ``YamlRootStorage`` from ``node.ext.fs.FSLocation``, which provides
  ``fs_path`` property. Note that ``fs_path`` is handled as list now.
  [rnix]

- Inherit ``IYamlRoot`` from  ``node.ext.fs.interfaces.IFile``.
  [rnix]

- Package depends on ``node.ext.fs`` now.
  [rnix]

- Replace deprecated use of ``Adopt`` by ``MappingAdopt``.
  [rnix]

- ``node.ext.yaml.YamlNode`` and ``node.ext.yaml.YamlFile`` not provides a
  default child factory any more.
  [rnix]


0.1 (2021-11-22)
----------------

- Initial work
  [rnix]
