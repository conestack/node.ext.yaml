from node.interfaces import IStorage


class IYamlStorage(IStorage):
    """YAML storage interface.
    """


class IYamlRoot(IYamlStorage):
    """YAML root storage interface
    """


class IYamlMember(IYamlStorage):
    """YAML member storage interface
    """
