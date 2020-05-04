from shrinkeventfile.shrinkeventfile import \
    NoAttrInHDF5FileException, \
    write_global_attrs, \
    write_group, \
    write_data, \
    write_attrs, \
    write_links, \
    shrink_and_write_eventfile

__all__ = [
    "NoAttrInHDF5FileException",
    "write_global_attrs",
    "write_group",
    "write_data",
    "write_attrs",
    "write_links",
    "shrink_and_write_eventfile",
]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
