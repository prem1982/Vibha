#For debugging; only
try:
    from IPython.Shell import IPShellEmbed
    ipython = IPShellEmbed()
    from ipdb import set_trace
    idebug = set_trace
except:
    def nothing():
        pass
    idebug = nothing
    ipython = nothing

__all__ = ['ipython','idebug']