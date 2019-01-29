"""Intelligent initialization of plugins."""
try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache

from ..base import BasePlugin
from ..basic_auth import BasicAuthDetector                  # noqa: F401
from ..high_entropy_strings import Base64HighEntropyString  # noqa: F401
from ..high_entropy_strings import HexHighEntropyString     # noqa: F401
from ..keyword import KeywordDetector                       # noqa: F401
from ..private_key import PrivateKeyDetector                # noqa: F401
from ..slack import SlackDetector                           # noqa: F401
from detect_secrets.core.log import log


def from_parser_builder(plugins_dict):
    """
    :param plugins_dict: plugins dictionary received from ParserBuilder.
        See example in tests.core.usage_test.
    :returns: tuple of initialized plugins
    """
    output = []
    for plugin_name in plugins_dict:
        output.append(from_plugin_classname(
            plugin_name,
            **plugins_dict[plugin_name]
        ))

    return tuple(output)


def merge_plugin_from_baseline(baseline_plugins, args):
    if args.overwrite:
        plugins = _merge_plugin_from_baseline(baseline_plugins, args)
    else:
        plugins = baseline_plugins
    return plugins


def _merge_plugin_from_baseline(baseline_plugins, args):
    # include all enabled plugins
    # include all baseline plugins
    #   - if same as enabled plugin, use parameter from enabled plugin
    # remove all disabled plugins
    enabled_plugins = from_parser_builder(args.enabled_plugins)
    merged_plugins_dict = {vars(plugin)['name']: plugin for plugin in enabled_plugins}
    baseline_plugins_dict = {vars(plugin)['name']: plugin for plugin in baseline_plugins}

    for plugin_name, plugin in list(baseline_plugins_dict.items()):
        if plugin_name not in merged_plugins_dict:
            merged_plugins_dict[plugin_name] = plugin

    for plugin_name in args.disabled_plugins:
        if plugin_name in merged_plugins_dict:
            merged_plugins_dict.pop(plugin_name)

    return merged_plugins_dict.values()


def from_plugin_classname(plugin_classname, **kwargs):
    """Initializes a plugin class, given a classname and kwargs.

    :type plugin_classname: str
    :param plugin_classname: subclass of BasePlugin
    """
    klass = globals()[plugin_classname]

    # Make sure the instance is a BasePlugin type, before creating it.
    if not issubclass(klass, BasePlugin):
        raise TypeError

    try:
        instance = klass(**kwargs)
    except TypeError:
        log.warning(
            'Unable to initialize plugin!',
        )
        raise

    return instance


def from_secret_type(secret_type, settings):
    """
    :type secret_type: str
    :param secret_type: unique identifier for plugin type

    :type settings: list
    :param settings: output of "plugins_used" in baseline. e.g.
        >>> [
        ...     {
        ...         'name': 'Base64HighEntropyString',
        ...         'base64_limit': 4.5,
        ...     },
        ... ]
    """
    mapping = _get_mapping_from_secret_type_to_class_name()
    try:
        classname = mapping[secret_type]
    except KeyError:
        return None

    for plugin in settings:
        if plugin['name'] == classname:
            plugin_init_vars = plugin.copy()
            plugin_init_vars.pop('name')

            return from_plugin_classname(
                classname,
                **plugin_init_vars
            )


@lru_cache(maxsize=1)
def _get_mapping_from_secret_type_to_class_name():
    """Returns secret_type => plugin classname"""
    mapping = {}
    for key, value in globals().items():
        try:
            if issubclass(value, BasePlugin) and value != BasePlugin:
                mapping[value.secret_type] = key
        except TypeError:
            pass

    return mapping