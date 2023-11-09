# FeatureStore-Lite

**FeatureStore-Lite** (FS-Lite) is a lightweight feature store for individuals and small teams working with medium-sized data (up to the 100s of GB).

There are three key concepts represented in FS-Lite, listed below.

1. **Records:** Objects with unique identifiers and to which features are attached. Typically this is a row of data, such as `(vehicle_id, year, make, model, mileage)`.
2. **Features:** Functions that compute new feature values for given records. For instance, the `value` feature could compute a vehicle's value based on its `year`, `make`, `model`, and `mileage`.
3. **FeatureStore:** This orchestrates the efficient computation of new features as well as caching and storage. For example, when requesting the `value` feature for a given vehicle, a featurestore would first check if the feature ahs already been computed. If not, it computes the feature value based on its implementation and dependencies.

In FS-Lite, emphasis is placed on:

- Documenting a feature's logic, purpose, version, and dependencies.
- Automatically computing feature dependencies when needed.
- Hiding storage, optimization, and caching details.

That's it.

## Usage


### Feature

In FS-Lite, features are simply functions with added metadata. The metadata is only used by `FeatureStore` objects to resolve dependency graphs, orchestrate computations, and cache feature values.

For example, you can define features that rely on named columns:

```python
from fs_lite import feature

@feature(dependencies=["price"])
def log10_price(input):
  """Compute the log10 of 'price'."""
  return log10(input["price"])

df = pd.DataFrame({"price": [1, 10, 100]})
log10_price(df)
# df with values [0, 1, 2]
```

And you can define features that rely on other features:

```python
@feature(dependencies=[log10_price])
def log10log0_price(input):
  return log10(input["log10_price"])
```

We recommend using column name placeholders by specifying a dictionary of dependencies with string keys and feature values. This provides the most clarity regarding input expectations:
```python
@feature(dependencies={"logprice": log10_price})
def log10log0_price(input):
  return log10(input["logprice"])
```

Here's an example with full metadata specified:
```python
@feature(
  name="myFeature",  # Default is the function's name
  descr="Feature description",  # Default is the function's docstring
  version="1.0.0",  # default is "0.0.0"
  id_column="index_column",  # Default is the list of dependency columns.
  dependencies={
    "column_1": first_feature,
    "column_2": second_feature
  }
)
def myFeature(input):
  pass
```



