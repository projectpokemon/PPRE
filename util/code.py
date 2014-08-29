
import linecache
import sys


def _c():
    """No-op"""
    pass


code = type(_c.func_code)  # : Code type


def poison(func, from_func, name=None):
    """Not for the faint of heart either"""
    prev = func.func_code
    new = from_func.func_code
    func.func_code = code(prev.co_argcount, prev.co_nlocals, prev.co_stacksize,
                          prev.co_flags, prev.co_code, prev.co_consts,
                          new.co_names,
                          prev.co_varnames, new.co_filename, new.co_name,
                          new.co_firstlineno, prev.co_lnotab,
                          prev.co_freevars, prev.co_cellvars)
    func.func_name = from_func.func_name
    func.func_doc = from_func.func_doc
    return func


def print_helpful_traceback():
    """Prints traceback with local variables.

    This should be called within an except block
    """
    frame = sys.exc_info()[2].tb_next
    stack = []
    while frame is not None:  # Build reversed stack of frames
        stack.append(frame.tb_frame)
        frame = frame.tb_next
    stack.reverse()
    for frame in stack:
        code = frame.f_code
        print('  File "%s", line %d, in %s' % (code.co_filename,
                                               frame.f_lineno,
                                               code.co_name))
        line = linecache.getline(code.co_filename, frame.f_lineno)
        if line:
            line = line.strip()
            print('\t'+line)
        for key, value in frame.f_locals.items():
            print('\t\t%s = %r' % (key, value))
