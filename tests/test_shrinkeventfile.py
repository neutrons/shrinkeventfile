import h5py
import pytest
import tempfile

import shrinkeventfile as shrink
from shrinkeventfile.shrinkeventfile import product

INPUT_RUN="NOM_92628"
INPUT_FILE="{}.nxs.h5".format(INPUT_RUN)

@pytest.fixture
def infile():
    infile =  h5py.File(INPUT_FILE, 'w')
    infile.attrs.create("HDF5_VERSION", b'1.8.5')
    infile.close()

    infile =  h5py.File(INPUT_FILE, 'r')
    return infile

@pytest.fixture
def outfile():
    f = tempfile.NamedTemporaryFile(
            delete=False,
            prefix=INPUT_RUN).name
    outfile = h5py.File(f, 'w')
    return outfile

def test_product():
    shape = [1, 2, 3, 4]
    total = product(shape)
    assert total == 24

def test_write_global_attrs(infile, outfile):
    shrink.write_global_attrs(infile, outfile)
    assert "HDF5_VERSION" in outfile.attrs
    assert outfile.attrs.get("HDF5_VERSION") ==  b'1.8.5'

def test_write_global_attrs_with_kwargs_to_skip_attribute(infile, outfile):
    shrink.write_global_attrs(infile, outfile, HDF5_VERSION=None)
    assert "HDF5_VERSION" not in outfile.attrs

def test_write_global_attrs_with_kwargs_to_overridte(infile, outfile):
    shrink.write_global_attrs(infile, outfile, HDF5_VERSION=b'9.9.9')
    assert "HDF5_VERSION" in outfile.attrs
    assert outfile.attrs.get("HDF5_VERSION") ==  b'9.9.9'

def test_write_global_attrs_with_undefined_kwargs(infile, outfile):
    with pytest.raises(shrink.NoAttrInHDF5FileException):
        shrink.write_global_attrs(infile, outfile, Foo="Bar")
