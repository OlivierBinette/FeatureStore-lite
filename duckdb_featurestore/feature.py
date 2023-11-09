from abc import abstractmethod, ABCMeta
from typing import List, Union, Optional, Type, Any
import networkx as nx
from featurestore import FeatureStore
import logging
from exceptions import MissingMethodException, CyclicDependencyException

logger = logging.getLogger(__name__)

class FeatureMeta(ABCMeta):
    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace, **kwargs)
        if "Feature" not in bases:
            return
        
        required_class_methods = getattr(cls, '_required_class_methods', [])
        
        missing_methods = [
            method for method in required_class_methods 
            if method not in namespace or not isinstance(namespace[method], classmethod)
        ]
        
        if missing_methods:
            error = MissingMethodException(f"Class {name} must implement class methods: {missing_methods}")
            logger.error(f"Error in Feature definition: {error}")
            raise error
    
    def __call__(cls, *args, **kwargs):
        error = TypeError(f"Instances of {cls.__name__} cannot be created")
        logger.error(f"Error instanciating Feature subclass: {error}")
        raise error

class Feature(metaclass=FeatureMeta):
    _required_class_methods = ['compute']

    description: Optional[str] = None
    version: Optional[str] = None
    dependencies: Optional[List[Union[str, "Feature"]]] = None
    fstore: Optional[FeatureStore] = None
    data_type: Type = Any

    @classmethod
    def compute(cls, input: data_type, *args, **kwargs) -> data_type:
        """Compute feature values assuming that all dependencies are available as columns in the given input.
        """
        try:
            return cls.compute_logic(input, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in computing {cls}: {e}")
            raise

    @classmethod
    @abstractmethod
    def compute_logic(cls, input: data_type, *args, **kwargs) -> data_type:
        pass
    
    @classmethod 
    def assert_no_cyclic_dependencies(cls):
        """
        Check that there are no cyclic dependencies.

        raises: ValueError if dependencies do not form a DAG
        """
        graph = cls.dependency_graph()
        if not nx.is_directed_acyclic_graph(graph):
            error = CyclicDependencyException("Dependencies do not form a DAG.")
            logger.error(f"Error in Feature definition: {error}")
            raise error

    @classmethod
    def dependency_graph(cls) -> nx.DiGraph:
        """Return dependency graph as a networkx object."""
        graph = nx.DiGraph()
        graph.add_node(cls)
        cls._add_dependencies_to_graph(graph)
        return graph

    @classmethod
    def _add_dependencies_to_graph(cls, graph: nx.DiGraph):
        """Recursively add dependencies to the graph."""
        for dep in cls.dependencies:
            graph.add_node(dep)
            graph.add_edge(cls, dep)
            if isinstance(dep, Feature) and not graph.has_predecessor(dep, cls):
                dep._add_dependencies_to_graph(graph)

    @classmethod
    def root_dependencies(cls):
        """Root dependencies of the dependency graph.
        """
        graph = cls.dependency_graph()
        return [node for node in graph.nodes if list(graph.predecessors(node)) == []]

    @classmethod
    def name(cls) -> str:
        """Feature name (class name)."""
        return cls.__name__