import os
import pandas as pd
import numpy as np
import seaborn as sns


from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report,r2_score
from sklearn.feature_selection import f_regression, f_classif, chi2
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from rfpimp import permutation_importances

sns.set(rc={'figure.figsize':(14,9)})
pd.set_option("display.max_rows", 300)
pd.set_option("display.max_columns", 30)


os.chdir('/Users/witnes/Workspace/MDA/Peru-MDA-Ship')

def r2(rf, X_train, y_train):
    return r2_score(y_train, rf.predict(X_train))

#%%
df_country_ts_dim = pd.read_csv('data/dim_all_country_info.csv')
df_country_ts_dim = df_country_ts_dim.set_index( ['country', 'year'], drop =False)

#df_country_ts_dim.to_csv('data/dim_all_country_info.csv')

#%%

df_country_ts_dim.columns
#%%

country = df_country_ts_dim['country.1'].dropna().unique()

df_country_ts_dim = df_country_ts_dim[
    df_country_ts_dim['country.1'].isin(
        country[
            (df_country_ts_dim.groupby('country.1')['co2_emission_kt'].count() > 0) &
            (df_country_ts_dim.groupby('country.1')['temp_mean'].count() > 0)
        ]
    )]

df_country_ts_dim['is_hw_happend_l1'] = df_country_ts_dim.groupby(['country.1']).is_hw_happend.shift(1)
df_country_ts_dim['temp_mean_l1'] = df_country_ts_dim.groupby(['country.1']).temp_mean.shift(1)
df_country_ts_dim['temp_median_l1'] = df_country_ts_dim.groupby(['country.1']).temp_median.shift(1)
df_country_ts_dim['is_hw_happend_l1'] = df_country_ts_dim['is_hw_happend_l1'].apply(lambda r: 1 if r else 0)
df_country_ts_dim['is_hw_happend_l4'] = df_country_ts_dim.groupby(['country.1']).is_hw_happend.shift(4)
df_country_ts_dim['is_hw_happend_l4'] = df_country_ts_dim['is_hw_happend_l4'].apply(lambda r: 1 if r else 0)


#%%
cols = [
    'year', 'latitude', 'forest_area_ratio', 'urban_pop_ratio', 'log_total_population', 'agri_land_ratio',
    'log_co2_emission_kt', 'log_methane_emission_kt', 'log_land_area_sq_km','livestock_prod_ind', 'food_prod_ind',
    'temp_mean','temp_median_l1', 'is_hw_happend_l4','region',
]

ct = ColumnTransformer(
    [
        ('Impute',SimpleImputer(strategy ='mean'), cols[:-1]),
        ('incomeLevel_category', OneHotEncoder(dtype ='int'), ['region']),
        # ('standardscaler', StandardScaler(), cols[:-1])
    ],
    remainder = 'passthrough'
)

X = ct.fit_transform(df_country_ts_dim[cols])
y = df_country_ts_dim.is_hw_happend.values

X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=42)


#%%
lr = LogisticRegression(class_weight= 'balanced')
lr.fit(X_train, y_train)

clf = DecisionTreeClassifier(random_state=0, class_weight= 'balanced',  max_depth=5)
clf.fit(X_train, y_train)

#%%

print(classification_report(y_train, lr.predict(X_train)))
print(classification_report(y_test, lr.predict(X_test)))

#%%

print(classification_report(y_train, clf.predict(X_train), target_names = ['Non Heat Wave', 'Heat Wave']))
print(classification_report(y_test, clf.predict(X_test), target_names = ['Non Heat Wave', 'Heat Wave']))


#%%

svm_model = SVC(C=1.0, kernel='linear', class_weight='balanced')

svm_model.fit(X_train, y_train)

#%%
print(classification_report(y_train, svm_model.predict(X_train), target_names = ['Non Heat Wave', 'Heat Wave']))
print(classification_report(y_test, svm_model.predict(X_test), target_names = ['Non Heat Wave', 'Heat Wave']))

#%%
rf = RandomForestClassifier(
            n_estimators=1000, min_samples_split =6, max_depth= 10,
            max_features= 6, class_weight = 'balanced', bootstrap = True)

rf.fit(X_train, y_train)


#%%
f_m = pd.DataFrame(
    f_classif(X_train, y_train)
).T

f_m
#%%
params = {'n_estimators': 2000, 'max_leaf_nodes': 4, 'max_depth': 6, 'random_state': 2,
                   'min_samples_split': 5, 'learning_rate': 0.1, 'subsample': 0.4}

gbt = GradientBoostingClassifier(**params)

gbt.fit(X_train, y_train)

#%%

print(classification_report(y_train, gbt.predict(X_train)))
print(classification_report(y_test, gbt.predict(X_test)))
