from cffi import FFI
ffibuilder = FFI()

ffibuilder.cdef(open('parse.h').read())

ffibuilder.set_source("_parse", open('parse.c').read(), libraries=[])

ffibuilder.compile(verbose=False)
