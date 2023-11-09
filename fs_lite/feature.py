from dataclasses import dataclass, field

def feature(name=None, descr=None, version=None, index_columns=None, dependencies=None):
    """
    A decorator that transforms a function into a Feature object with additional metadata.

    The decorated function must have a single argument, which is the input table for the feature computation. The input table is expected to have the columns specified in the `id_columns` argument and in the keys of the `dependencies` argument. The output should be a table of the same type, with specified index_columns and additional column(s) for feature values.

    Parameters:
    - name (str): Optional. The name of the feature. Defaults to the function's name.
    - descr (str): Optional. A description of the feature. Defaults to the function's docstring.
    - version (str): Optional. The version of the feature.
    - id_columns (list): Optional. A list of indexing columns for the input table. Defaults to an empty string.
    - dependencies (list): Optional. A list of column names or features that this feature depends on. Defaults to an empty string.

    Returns:
    - A Feature instance representing the decorated function.

    Example:
    >>> @feature(dependencies={'x': column('x')})
    ... def add_1_to_x(table):
    ...     return table['x'] + 1
    >>> add_1_to_x
    Feature(name=add_1_to_x, compute=<function add_1_to_x at 0x...>, version=None, index_columns=[], dependencies={'x': 'Feature(x)'})
    """
    def decorator(func):
        return Feature._from_function(
            func,
            name=name,
            descr=descr,
            version=version, 
            index_columns=index_columns or [], 
            dependencies=dependencies or dict()
        )
    return decorator

@dataclass(frozen=True, slots=True)
class Feature:
    """
    A class representing a feature in a data processing or analysis pipeline.

    The `compute` callable is the core of the Feature. It should be designed to:
    - Have a single input table argument with columns specified in the `id_columns` argument and in the keys of the `dependencies` argument. 
    - It should return a table of the same type as the input table, with index columns specified in `id_columns` and a single column corresponding to the computed feature, or with multiple columns for a multi-column feature. For pandas DataFrame, the index is an implicit feature of the table, so it is not necessary to specify a separate index column in `index_columns`.

    Attributes:
    - name (str): The name of the feature.
    - compute (callable): The function that performs the computation for this feature.
    - descr (str): A description of the feature.
    - version (str): The version of the feature.
    - id_columns (list): Identifier columns relevant to the feature.
    - dependencies (list): Other features that this feature depends on.

    Methods:
    - __call__: Enables the feature instance to be called like a function, executing its computation.
    - __hash__: Returns a hash value for the feature.
    - from_function: Class method to create a Feature instance from a function.
    - col: Class method to create a Feature instance that retrieves a given column from the input table.
    """

    name: str
    compute: callable
    descr: str = None
    version: str = None
    dependencies: dict = field(default_factory=dict)
    index_columns: list = field(default_factory=list)

    def __call__(self, input, *args, **kwargs):
        return self.compute(input, *args, **kwargs)

    def __str__(self):
        return f'Feature(name={self.name}, compute={self.compute}, version={self.version}, index_columns={self.index_columns}, dependencies={ {key: "Feature("+value.name+")" for key, value in self.dependencies.items()} })'

    def __hash__(self):
        return hash((self.name, self.descr, self.version, tuple(self.index_columns), tuple(self.dependencies), self.compute.__code__))

    @classmethod
    def _from_function(cls, func, name=None, descr=None, version=None, index_columns=field(default_factory=list), dependencies=field(default_factory=dict)):
        name = func.__name__ if name is None else name
        descr = func.__doc__ if descr is None else descr
        return cls(name=name, compute=func, descr=descr, version=version, index_columns=index_columns, dependencies=dependencies)
    
def column(name):
    """
    Create a Feature instance that represents a given column.

    Parameters:
    - name (str): The name of the column to retrieve.

    Returns:
    - A Feature instance that represents the given column. Its compute function returns `None`.

    Example:
    >>> price_column = Feature.col('price')
    >>> price_column
    Feature(name='price', compute=<function <lambda> at 0x...>, descr='Identifies a given column by name.', version='1.0.0', index_columns=[], dependencies={})
    """
    return Feature(name=name, compute=lambda table: None, descr='Identifies a given column by name.', version='1.0.0')