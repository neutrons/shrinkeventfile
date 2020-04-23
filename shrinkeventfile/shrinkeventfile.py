#!/usr/bin/env python
__VERSION__ = '0.1'

import os
import h5py 

SDS = 'SDS'

# each items is a triplit of (from, name, to)
links_to_make = []

class NoAttrInHDF5FileException(Exception):
    '''Raise exception when attribute not found in HDF5 File'''

def product(shape):
    total = 1
    for num in shape:
        total *= num
    return total

def write_global_attrs(infile, outfile, **kwargs):
    '''
    This function just copies (blindly) all of the file attributes.

    @param kwargs - List of attributes to override the old file.
                    Supplying a value of 'None' will make the 
                    attribute to not be copied.
    '''
    # get the old file attributes
    attrs = infile.attrs

    # override with new values as requested
    for name in kwargs.keys():
        if name not in attrs:
            raise NoAttrInHDF5FileException()
        if kwargs[name] is None:
            del attrs[name]
        else:
            attrs[name] = kwargs[name]

    # put the values into the new file
    for name in attrs.keys():
        outfile.attrs.create(name, attrs[name])

def writeGroup(infile, outfile, name, nxtype, **kwargs):
    if kwargs['verbose'] > 1:
        print("{} write(..., {}, {}, {})"(infile.path, name, nxtype, kwargs))
    if nxtype == SDS:
        writeData(infile, outfile, name, **kwargs)
    else: # work on groups
        infile.opengroup(name, nxtype)
        entries = infile.getentries()

    outfile.makegroup(name, nxtype)
    outfile.opengroup(name, nxtype)
    for temp in entries.keys():
        writeGroup(infile, outfile, temp, entries[temp], **kwargs)
    outfile.closegroup()
    infile.closegroup()

def writeData(infile, outfile, name, **kwargs):
    infile.opendata(name)

    # check if linking to something else
    linkto = infile.link()
    if linkto is not None and linkto != infile.path:
        links_to_make.append((infile.path, name, linkto))
    else:
        # shape is needed for next step
        (shape, ctype) = infile.getinfo()

        # decide whether or not to limit the node
        # NOTE: sns files link frequency/time as event pulse time
        limitlength = -1 # by default do nothing
        if kwargs['eventlimit'] > 0:
            if name == "event_id" \
                or name == "event_index" \
                or name == "event_pixel_id" \
                or name == "event_time_offset" \
                or name == "event_time_zero" \
                or name == "event_time_of_flight" \
                or infile.path.endswith("DASlogs/frequency/time"):
                if len(shape) == 1:
                    if shape[0] > kwargs['eventlimit']:
                        limitlength = kwargs['eventlimit']
        if kwargs['loglimit'] > 0:
            path = infile.path
            if "DASlogs" in path:
                if len(shape) == 1:
                    if path.endswith("DASlogs/frequency/time"):
                        if shape[0] > kwargs['eventlimit']:
                            limitlength = kwargs['eventlimit']
                    if shape[0] > kwargs['loglimit']:
                        limitlength = kwargs['loglimit']


        # read in the appropriate amount of data
        if limitlength > 0:
            if kwargs['verbose'] > 1:
                msg = "limiting length of {} from {} to {}"
                print(msg.format(infile.path, shape, [limitlength]))
            shape = [limitlength]
            data = infile.getslab([0], shape)
        else:
             data = infile.getdata()

        if name == "event_time_zero":
            print("limiting length of {} to {}".format(infile.path, shape))

        # put the data itself into the file
        outfile.makedata(name, ctype, shape)
        outfile.opendata(name)
        if product(shape) > 0: # some things are zero length
            outfile.putdata(data)

        # add some attributes
        writeAttrs(infile, outfile, **kwargs)
        outfile.closedata()

        infile.closedata()

def writeAttrs(infile, outfile, **kwargs):
    attrs = infile.getattrs()
    for name in attrs:
        value = attrs[name]
        if kwargs['verbose'] > 2:
            print(infile.path, name, value, type(value))
        try:
            outfile.putattr(name, value)
        except:
            outfile.putattr(name, value, value.dtype)

def writeLinks(outfile, **kwargs):
    for (src, name, target) in links_to_make:
        if kwargs['verbose'] > 2:
            print(src, name, target)
        parent = src.replace('/'+name, '')
        outfile.openpath(target)
        if outfile.path != target:
             raise RuntimeError("Something is very wrong: %s != %s" % \
                               (outfile.path, target))

        # in principle we should check if it is a linked group
        linkid = outfile.getdataID()
        outfile.openpath(parent)
        outfile.makenamedlink(name, linkid)


if __name__ == "__main__":
    import optparse

    info = []
    parser = optparse.OptionParser("usage %prog [options] <in> <out>",
                                   None, optparse.Option, __VERSION__,
                                   'error', ' '.join(info))
    parser.add_option("--limit-events", dest="eventlimit",
                      help="Limit the size of event lists")
    parser.add_option("--limit-logs", dest="loglimit",
                      help="Limit the size of logs")
    parser.add_option("-d", "--debug", dest="verbose", default=0,
                      action="count",
                      help="Increase print level")
    parser.set_defaults(eventlimit=-1)
    parser.set_defaults(loglimit=-1)
    (options, args) = parser.parse_args()
    options.eventlimit = int(options.eventlimit)
    options.loglimit = int(options.loglimit)

    # get the in/out file names
    if not len(args) == 2:
        parser.error("Must supply input and output file")
    args = [os.path.abspath(name) for name in args]
    (input_filename, output_filename) = args
    if not os.path.exists(input_filename):
        parser.error("'%s' does not exist" % input_filename)

    # open the file handles
    infile  = h5py.File(input_filename, 'r')
    outfile = h5py.File(output_filename, 'w')

    # copy things over
    write_global_attrs(infile, outfile)
    entries = infile.getentries()
    for name in entries.keys():
        writeGroup(infile, outfile, name, entries[name],
                   eventlimit=options.eventlimit, loglimit=options.loglimit,
                   verbose=options.verbose)
    infile.close()

    # put in the links
    writeLinks(outfile, verbose=options.verbose)
    outfile.close()
