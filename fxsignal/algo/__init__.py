import importlib
#from .trend_keltner    import BasicStrategy, BuyStrategy, SellStrategy
#from .trend_keltnera   import BasicStrategy, BuyStrategy, SellStrategy

def import_algo_module(algo):
    module = importlib.import_module("fxsignal.algo.{}".format(algo))
    return module

def import_algo_class(algo, strategy):
    module = importlib.import_module("fxsignal.algo.{}".format(algo))
    class_name = "{}Strategy".format(strategy.capitalize())
    return getattr(module, class_name)
