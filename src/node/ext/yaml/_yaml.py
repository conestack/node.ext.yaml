from odict import odict
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
