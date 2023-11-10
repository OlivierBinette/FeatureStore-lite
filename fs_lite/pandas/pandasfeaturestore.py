import pandas as pd
from fs_lite.featurestore import FeatureStore
from fs_lite.feature import Feature

def compute_feature(input, feature):
        if len(feature.index_columns) > 0:
            raise ValueError('The `index_columns` Feature attribute is not used with Pandas features. Pandas DataFrame index is used instead.')
        
        if feature.compute is None:
            if feature.name not in input.columns:
                raise ValueError(f'Feature {feature.name} is not in input table.')
            output = input[feature.name].to_frame()
        else:
            output = feature.compute(input)
            if not isinstance(output, pd.DataFrame):
                raise ValueError(f'Feature {feature.name} did not return a DataFrame.')

        output.columns = [feature.name + '_' + str(i) for i, _ in enumerate(output.columns)]
        return output

class PandasFeatureStore(FeatureStore[pd.DataFrame]):
    
    def compute(self, input: pd.DataFrame, features: list[Feature[pd.DataFrame]]) -> pd.DataFrame:
        return pd.concat([compute_feature(input, feature) for feature in features], axis=1, )
