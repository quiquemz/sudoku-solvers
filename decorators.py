import signal
import time


class TimedOutExc(Exception):
    pass


def deadline(timeout, *args):
    def decorate(f):
        def handler(signum, frame):
            raise TimedOutExc()

        def new_f(*args):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            return f(*args)
            signa.alarm(0)
        new_f.__name__ = f.__name__
        return new_f
    return decorate


def time_deco(f):
    def decorated(*args):
        t = time.time()
        try:
            result = f(*args)
            t = time.time() - t
            print('\nExecution time: %s seconds\n' % str(t))
            return (t, result)

        except:
            print('\nEXCEEDED LIMIT: 5 Seconds\n')
            return(5., False)
    return decorated
