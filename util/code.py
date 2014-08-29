
import inspect
import linecache
import sys
import types


code = types.CodeType


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


def get_func_code(target):
    if inspect.isclass(target):
        target = target.__init__
        # TODO: classes with no init using empty code object
    if inspect.ismethod(target.__call__):
        target = target.__call__.im_func
    if inspect.ismethod(target):
        target = target.im_func
    if inspect.isfunction(target):
        return target.func_code


def print_helpful_traceback():
    """Prints traceback with local variables.

    This should be called within an except block
    """
    frame = sys.exc_info()[2].tb_next
    stack = []
    while frame is not None:  # Build reversed stack of frames
        stack.append(frame.tb_frame)
        frame = frame.tb_next
    # stack.reverse()
    print('\033[91mTraceback (most recent call last):\033[0m')
    for frame in stack:
        code = frame.f_code
        print('\033[94m  File "%s", line %d, in %s\033[0m' %
              (code.co_filename, frame.f_lineno, code.co_name))
        line = linecache.getline(code.co_filename, frame.f_lineno)
        for key, value in frame.f_locals.items():
            print('\t%s = %r' % (key, value))
        if line:
            print('\033[96m\t\t%s\033[0m' % line.strip())
