# FeatureStore-Lite

!!! (under construction / brainstorming / not ready for use) !!!

**FeatureStore-Lite** (FS-Lite) is a lightweight feature store for individuals and small teams working with medium-sized data (up to the 100s of GB).

There are three key concepts represented in FS-Lite, listed below.

1. **Records:** Objects with unique identifiers and to which features are attached. Typically this is a row of data, such as `(vehicle_id, year, make, model, mileage)`.
2. **Features:** Functions that compute new feature values for given records. For instance, the `value` feature could compute a vehicle's value based on its `year`, `make`, `model`, and `mileage`.
3. **FeatureStore:** This orchestrates the efficient computation of new features as well as caching and storage. For example, when requesting the `value` feature for a given vehicle, a featurestore would first check if the feature has already been computed. If not, it computes the feature value based on its implementation and dependencies.

In FS-Lite, emphasis is placed on:

- Getting out of your way. Features definitions are immediately useable and testable, whether or not you use a featurestore.
- Helping you document a feature's logic, purpose, version, and dependencies.
- Using a featurestore to abstract away storage, computations along dependency graphs, optimization, and caching details.

That's it. Feature can be defined in any computation framework. Featurestores are provided for pandas and duckdb backends.

## Usage

### Defining and Documenting Features

In FS-Lite, features are simply functions with added metadata. The metadata is only used by `FeatureStore` objects to resolve dependency graphs, orchestrate computations, and cache feature values.

For example, you can define features that rely on named columns:

```python
from fs_lite import feature, column

@feature(dependencies={"price": column("price")})
def log10_price(input):
  """Compute the log10 of 'price'."""
  return log10(input["price"])

df = pd.DataFrame({"price": [1, 10, 100]})
log10_price(df)
# df with values [0, 1, 2]
```

And you can define features that rely on other features:
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
  index_columns=["index_column"],  # Default is []
  dependencies={  # Default is {}
    "column_1": first_feature,
    "column_2": second_feature
  }
)
def myFeature(input):
  pass
```

### Using a FeatureStore for computation and retrieval.

