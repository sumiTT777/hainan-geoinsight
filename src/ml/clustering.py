"""Validated clustering; unavailable distances are never treated as zero."""
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
FEATURES=['medical_count','education_count','transit_count','medical_m','education_m','transit_m','road_km_per_km2','facility_density']
def cluster(grid, k: int=3):
    x=grid[FEATURES].replace([np.inf,-np.inf],np.nan)
    if len(x)<max(10,2*k) or x.notna().mean().min()<0.5: raise ValueError('Insufficient samples or more than 50% missing in a feature')
    x=StandardScaler().fit_transform(SimpleImputer(strategy='median').fit_transform(x))
    if len(np.unique(x,axis=0))<=k: raise ValueError('Insufficient distinct feature vectors')
    labels=KMeans(n_clusters=k,random_state=42,n_init=20).fit_predict(x)
    score=silhouette_score(x,labels,sample_size=min(5000,len(x)),random_state=42)
    out=grid.copy(); out['cluster']=labels.astype(str)
    xy=PCA(n_components=2).fit_transform(x); out['PC1']=xy[:,0]; out['PC2']=xy[:,1]
    return out,float(score)
