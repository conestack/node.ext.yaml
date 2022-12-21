Changes
=======

0.3 (2022-12-21)
----------------

- ``node.ext.yaml.behaviors.YamlSequenceStorage`` implements now
  ``__contains__``, which compares the storage values directly. This is needed
  to make containment checks work because yaml child nodes are not cached on
  ``__getitem__``.
  [rnix]

- ``node.ext.yaml.behaviors.YamlMember`` provides now
  ``default_mapping_factory`` and ``default_sequence_factory`` settings.
  [rnix]

- ``node.ext.yaml.behaviors.YamlMember`` inherits from
  ``node.behaviors.WildcardFactory`` now.
  [rnix]

- Use ``node.behaviors.SequenceAdopt`` and ``node.behaviors.SequenceOrder``
  behaviors on ``node.ext.yaml.YamlSequence``.
  [rnix]

- Use ``node.behaviors.MappingOrder`` behavior in favor of
  ``node.behaviors.Order`` as introduced in
  ``node`` 1.2 on ``node.ext.yaml.YamlMapping`` and ``node.ext.yaml.YamlFile``.
  [rnix]


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
