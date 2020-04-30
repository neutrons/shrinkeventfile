#!/usr/bin/env python
__VERSION__ = '0.1'

import os
import h5py

SDS = 'SDS'

# each items is a triplet of (from, to)
links_to_make = []


class NoAttrInHDF5FileException(Exception):
    '''Raise exception when attribute not found in HDF5 File'''


def product(shape):
    total = 1
    for num in shape:
        total *= num
    return total


def get_entries(data):
    result = {}
    for item in data:
        nxtype = SDS
        if u'NX_class' in data[item].attrs.keys():
            nxtype = data[item].attrs['NX_class'].decode('UTF-8')
        result[item] = nxtype
    return result


def write_global_attrs(infile, outfile, **kwargs):
    '''
    This function just copies (blindly) all of the file attributes.

    @param kwargs - List of attributes to override the old file.
                    Supplying a value of 'None' will make the
                    attribute to not be copied.
    '''
    # get the old file attributes
    attrs = dict(infile.attrs)

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


def write_group(ingroup, outgroup, name, **kwargs):

    # Get the NeXus type attribute
    nxtype = ingroup[name].attrs.get('NX_class', SDS)

    # Debug - print the group, name of next directory and its NeXus type
    verbose = kwargs.get('verbose', 0)
    if verbose > 1:
        print("{} write(..., {}, {})".format(ingroup, name, nxtype))

    # If we are at a "leaf" of the tree, just write the data
    if nxtype == SDS:
        indataset = ingroup[name]
        write_data(indataset, outgroup, name, **kwargs)

    # If we are still on group nodes of the tree, traverse recursively
    else:
        # Create the next groups we will be copying
        ingroup_next = ingroup[name]
        outgroup_next = outgroup.create_group(name)
        write_attrs(ingroup_next, outgroup_next)

        # Get all the current entries of this next group node
        entries = get_entries(ingroup_next)

        for temp in entries.keys():
            write_group(ingroup_next, outgroup_next, temp, **kwargs)


def write_data(indataset, outgroup, name, verbose=0, eventlimit=0, loglimit=0):
    # check if linking to something else
    linkto = indataset.parent.get(indataset.name, getlink=True)
    is_a_link = not isinstance(linkto, h5py.HardLink)
    if is_a_link:
        links_to_make.append((indataset, linkto))
    else:
        # shape is needed for next step
        shape = indataset.shape

        # decide whether or not to limit the node
        # NOTE: sns files link frequency/time as event pulse time
        limitlength = -1  # by default do nothing
        if eventlimit > 0:
            if name == "event_id" \
                    or name == "event_index" \
                    or name == "event_pixel_id" \
                    or name == "event_time_offset" \
                    or name == "event_time_zero" \
                    or name == "event_time_of_flight" \
                    or indataset.name.endswith("DASlogs/frequency/time"):
                if len(shape) == 1:
                    if shape[0] > eventlimit:
                        limitlength = eventlimit
        if loglimit > 0:
            if "DASlogs" in indataset.name:
                if len(shape) == 1:
                    if indataset.name.endswith("DASlogs/frequency/time"):
                        if shape[0] > eventlimit:
                            limitlength = eventlimit
                    if shape[0] > loglimit:
                        limitlength = loglimit

        # read in the appropriate amount of data
        if limitlength > 0:
            if verbose > 1:
                msg = "limiting length of {} from {} to {}"
                print(msg.format(indataset.name, shape, [limitlength]))
            shape = limitlength
            data = indataset[0:shape]
        else:
            data = indataset[()]

        if name == "event_time_zero":
            print("limiting length of {} to {}".format(indataset.name, shape))

        # put the data itself into the file
        outdataset = outgroup.create_dataset(name, data=data)

        # add some attributes
        write_attrs(indataset, outdataset, verbose=verbose)


def write_attrs(indataset, outdataset, verbose=0):
    for name, value in indataset.attrs.items():
        if verbose > 2:
            print(indataset.name, name, value, type(value))
        try:
            outdataset.attrs.create(name, value)
        except BaseException:
            # TODO: What is the actual exception we would get for this?
            outdataset.attrs.create(name, value, dtype=value.dtype)


def write_links(outfile, verbose):
    for (in_soft_link, in_hard_link) in links_to_make:
        soft_link_path = in_soft_link.name
        hard_link_path = in_hard_link.path
        if verbose > 2:
            msg = "Creating soft link {} to hard link {}"
            print(msg.format(soft_link_path, hard_link_path))
        outfile[soft_link_path] = h5py.SoftLink(hard_link_path)


def shrink_and_write_eventfile(input_filename, output_filename, **kwargs):
    # open the file handles
    infile = h5py.File(input_filename, 'r')
    outfile = h5py.File(output_filename, 'w')

    # copy things over
    write_global_attrs(infile, outfile)
    entries = get_entries(infile)
    for name in entries.keys():
        write_group(infile, outfile, name, **kwargs)

    infile.close()

    # put in the links
    verbosity = kwargs.get('verbose', 0)
    write_links(outfile, verbose=verbosity)

    outfile.close()


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

    if not len(args) == 2:
        parser.error("Must supply input and output file")

    # Get the absolute paths for the input and output filenames
    args = [os.path.abspath(name) for name in args]

    # Make sure input file name exists
    (input_filename, output_filename) = args
    if not os.path.exists(input_filename):
        parser.error("'%s' does not exist" % input_filename)

    # Take the input filename, shrink based on inputs, and save to output file
    shrink_and_write_eventfile(*args, **options)
