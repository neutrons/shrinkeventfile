import h5py
import os
import pytest
import tempfile

from tests import TEST_DATA_DIR

import shrinkeventfile as shrink
from shrinkeventfile.shrinkeventfile import get_entries, product

INPUT_RUN="NOM_92628"
INPUT_FILE="{}.nxs.h5".format(INPUT_RUN)
FAKE_INPUT_FILE="{}_fake.nxs.h5".format(INPUT_RUN)

@pytest.fixture
def infile():
    filename = os.path.join(TEST_DATA_DIR, INPUT_FILE)
    infile =  h5py.File(filename, 'r')
    return infile

@pytest.fixture
def fake_infile():
    filename = os.path.join(FAKE_INPUT_FILE)
    fake_infile =  h5py.File(filename, 'w')
    fake_infile.attrs.create("HDF5_VERSION", '1.8.5')
    fake_infile.close()

    fake_infile =  h5py.File(FAKE_INPUT_FILE, 'r')
    return fake_infile

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

def test_get_entries(infile):
    result = get_entries(infile)

    # NXcollection entry
    assert "DASlogs" in result
    assert result["DASlogs"] == "NXcollection"

    # NXeven_data entry
    assert "bank10_events" in result
    assert result["bank10_events"] == "NXevent_data"

    # SDS entry
    assert "duration" in result
    assert result["duration"] == "SDS"

    # NXinstrument entry
    assert "instrument" in result
    assert result["instrument"] == "NXinstrument"

    # NXmonitor entry
    assert "monitor1" in result
    assert result["monitor1"] == "NXmonitor"

    # NXsample
    assert "sample" in result
    assert result["sample"] == "NXsample"

    # NXuser
    assert "user1" in result
    assert result["user1"] == "NXuser"

def test_write_global_attrs(fake_infile, outfile):
    shrink.write_global_attrs(fake_infile, outfile)
    assert "HDF5_VERSION" in outfile.attrs
    assert outfile.attrs.get("HDF5_VERSION") ==  '1.8.5'

def test_write_global_attrs_with_kwargs_to_skip_attribute(fake_infile, outfile):
    shrink.write_global_attrs(fake_infile, outfile, HDF5_VERSION=None)
    assert "HDF5_VERSION" not in outfile.attrs

def test_write_global_attrs_with_kwargs_to_overridte(fake_infile, outfile):
    shrink.write_global_attrs(fake_infile, outfile, HDF5_VERSION='9.9.9')
    assert "HDF5_VERSION" in outfile.attrs
    assert outfile.attrs.get("HDF5_VERSION") ==  '9.9.9'

def test_write_global_attrs_with_undefined_kwargs(fake_infile, outfile):
    with pytest.raises(shrink.NoAttrInHDF5FileException):
        shrink.write_global_attrs(fake_infile, outfile, Foo="Bar")
