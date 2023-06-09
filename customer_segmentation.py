# -*- coding: utf-8 -*-
"""customer-segmentation _FDS Group Activity.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XCRA98OLc_WHp_DtHGDVP83y9VlDKJLm

---


# DataSet
Customer Segmentation [link](https://www.kaggle.com/datasets/vetrirah/customer), contains

| Feature         | Description     | Values |
|--------------|-----------|------------|
| ID | Id of customer | 1,2,3,4,... |
| Gender | Gender of the customer  | (Male & Female) |
| Ever_Married |  Marital status of the customer | (Yes & No) |
| Age | Age of the customer | 10,20, 25, 40,.... |
| Graduated | Is the customer a graduate? | (Yes & No) | 
| Profession |Profession of the customer | (Artist, Healthcare,Doctor, Engineer, Lawyer, etc) |
| Work_Experience |  Work Experience |  (1:10) |
| Spending_Score | Spending score of the customer | (Low, Average, High) |
| Family_Size | Number of family members for the customer (including the customer)  | 1,5,2,.. |
| Var_1 | Variable  | (Cat_1, Cat_2, Cat_3, Cat_4) |

  ---

# Conclusion

*  **Dataset** is not distributed properly to the actual segments. i.e, there are poorly patterns.
* **Clustering Techniques** **`KMeans`** has been tried to cluster data better than the current situation.
the **KMeans** give best results based on silhouette score.
* **Classification Algorithms** **`KNN RF SVM AdaBoost`** were used to ensure that **KMeans** work. The performance of **classification Algorithms** on `KMeans` was very high and no ***overfitting*** occurred.
* **TSNE** is used to visualize Data
---

<a id="section-one"></a>
# Import Libraries
"""

import numpy as np
import pandas as pd

import matplotlib.pyplot as py
import seaborn as sb

from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score

from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering
from sklearn.mixture import GaussianMixture

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier

from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay, classification_report

"""# Load Data"""

trainSet = pd.read_csv('/Train.csv', index_col='ID')
trainSet.head(10)

trainCluster = trainSet['Segmentation']
trainSet.drop(['Segmentation'], axis=1, inplace=True)

testSet = pd.read_csv('/Test.csv', index_col='ID')
testCluser = pd.read_csv('/sample_submission.csv', index_col='ID')

"""# Some ***EDA*** on Data

## Information about Data
"""

trainSet.head(10)

trainSet.info()

# No of Missing Data And Its Percentage as Whole
pd.DataFrame({'missing':trainSet.isnull().sum(), 
              'percentage':(trainSet.isnull().sum() / np.shape(trainSet)[0]) * 100})

trainSet.describe()

"""By the description above the **age** is `right-skewed` this means that the 
most customers are young.


Because the `mean > median`
"""

# Number of Unique Values in fields with Most missing data
(len(np.unique(trainSet.Work_Experience))-1 , len(np.unique(trainSet.Family_Size)) - 1)

"""Deal with ***Work_Experience*** & ***Family_Size*** as **(ordinal) categorical** features, because the number of unique values is few.
But it also make sense as the nature of these features meant to be repeatative.

## Working with Features
Main Question, **Is there any combination of features that can distinguish between the Segments?**
"""

# visualization function to be used regularly for categorical features distribution based on age only
def plot_category(categorical, contenious= trainSet.Age, target= trainCluster):
    """
    Make Some Visualizations
    :param categorical: categorical feature
    :param contenious: numerical feature that want to show its distribution.
    :param target: target feature to make hue
    :return: None
    """

    sb.set_theme(style='ticks')
    py.figure(figsize=(10, 5))
    py.title("Count of each value in " + categorical.name)
    sb.countplot(x=categorical, hue=target); py.show()

    sb.set_theme(style='darkgrid')
    py.figure(figsize=(10, 5))
    py.title("Distribution of " + contenious.name + " based on " + categorical.name)
    sb.stripplot(x=categorical, y=contenious, hue=target); py.show()

    sb.set_theme(style='ticks')
    py.figure(figsize=(10, 5))
    py.title("Distribution of " + contenious.name + " based on " + categorical.name)
    sb.boxenplot(x=categorical, y=contenious, hue=target); py.show()

    pass

"""### Age"""

sb.kdeplot(x=trainSet['Age'], hue=trainCluster)

sb.histplot(x=trainSet['Age'], hue=trainCluster, bins=80)

"""Can age be the be the sole feature to describe the Customer behavior(segmentation)"""

# Let's check age behavious in some random range to see the segementation in customer  
pd.DataFrame(data=[trainCluster[(trainSet['Age'] >= 35) & (trainSet['Age'] <= 45)].value_counts(),
                   trainCluster[(trainSet['Age'] >= 35) & (trainSet['Age'] <= 45)].value_counts() / trainCluster[(trainSet['Age'] >= 35) &
                   (trainSet['Age'] <= 45)].value_counts().sum() * 100], index=['Segmentation', 'Percentage'])

"""> There are many overlaps between Segmentations. because of this, the **age** only not enough for describe behavior of customers.
i.e, can't distinguish between all ***Segments*** using this features.
But can distinguish the ***Segnment*** **D**, in case the **age** is small than ***25*** year.

### Gender
"""

pd.DataFrame(data=[(trainCluster[(trainSet['Gender'] == 'Male')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Gender'] == 'Female')].value_counts()/ trainCluster.value_counts()) * 100],
             index=['Male', 'Female'])

"""> In each Segment the Percentage(Distribution) of *males* and *female* is closer (not a sole distingusher in terms of segementation)."""

# Calling the above defined visualization function to analyze the gender
plot_category(categorical=trainSet.Gender)

"""> + From ***count plot*** the **Gender** can't distinguish between ***Segments*** 
> If Customer is *Male*, can't tell what's his ***Segments*** , because the count of each ***segment*** is closer.
> also in *Female*
> + From ***strip & boxen plots*** The distribution of **age** for each **Gender** in each ***Segment*** is almost the same.
> Can't Solve Overlap problem in age. i.e, can't distinguish between ***Segment*** using these 2-features.

### Ever_Married
"""

pd.DataFrame(data=[(trainCluster[(trainSet['Ever_Married'] == 'No')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Ever_Married'] == 'Yes')].value_counts()/ trainCluster.value_counts()) * 100],
             index=['Not Married', 'Married'])

"""> In each Segment the Percentage(Distribution) of *married* and *not married, yet* is seperated well, except the segment ***A***. Which has close distributuion"""

plot_category(categorical=trainSet.Ever_Married)

"""> + From ***count plot*** the **Gender** can distinguish between ***Segments*** only in case the customer is *not married*, where
the ***segment*** would be **D** because the count of in this ***segment*** is significantly far from the rest.
> but no in *Female*
> + From ***strip & boxen plots*** The distribution of **age** for each **category** can't distinguish between ***Segments*** using these 2-features.

### Graduated
"""

pd.DataFrame(data=[(trainCluster[(trainSet['Graduated'] == 'No')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Graduated'] == 'Yes')].value_counts()/ trainCluster.value_counts()) * 100],
             index=['Not Graduated', 'Graduated'])

"""> In each Segment the Percentage(Distribution) of *graduated* and *not graduated, yet* is seperated well, especially in the segment ***C & B***."""

plot_category(categorical=trainSet.Graduated)

"""> + Form ***count plot*** the **Graduated** can distinguish between ***Segments*** only in case the customer is *not graduated*, where
the ***segment*** would be **D** because the count of in this ***segment*** is significantly far from the rest.
> but no in *Female*
> + From ***strip & boxen plots*** The distribution of **age** for each **category** can't distinguish between ***Segment*** using these 2-features.

### Profession
"""

trainSet.Profession.unique()

pd.DataFrame(data=[(trainCluster[(trainSet['Profession'] == 'Healthcare')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Profession'] == 'Engineer')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Profession'] == 'Lawyer')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Profession'] == 'Entertainment')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Profession'] == 'Artist')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Profession'] == 'Executive')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Profession'] == 'Doctor')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Profession'] == 'Homemaker')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Profession'] == 'Marketing')].value_counts()/ trainCluster.value_counts()) * 100],
             index=trainSet.Profession.unique()[:-1])

"""> In segment ***A & B & C***, the dominant profession is **Artist**.
>
> But in segment ***D***, the dominant profession is **Healthcar**. 
"""

plot_category(categorical=trainSet.Profession)

"""> + Form ***count plot***, the **Profession** can distinguish between many ***Segments***, in case the **Profession** is
>> *Healthcare* then the ***Segments*** should be **D**
>>
>> *Artist* then the ***Segments*** should be **C**
>>
>> *Marketng* then the ***Segments*** may be **D**
>>
>> *Entertainment* then the ***Segments*** should be **A**
> + From ***strip & boxen plots***, the small **age** values `less than 25` and *Healthcare* **Profession**, the segment is **D**, but in high **age** values not and can't distinguish between ***Segments***.
 *Layer* **Profession** has diffrient pattern than other **Profession**, thier **age** is high.

### Work Experience
"""

trainSet.Work_Experience.unique()

plot_category(categorical=trainSet.Work_Experience)

"""> + Form ***count plot***, the **Work Experience** can't distinguish between ***Segments***
> + From ***strip & boxen plots***, when **Work Experience** is `11 12 13 14` and **age** is high the **segment** is **C**. but in other **Work Experience** can't distinguish.

### Spending Score
"""

trainSet.Spending_Score.unique()

pd.DataFrame(data=[(trainCluster[(trainSet['Spending_Score'] == 'Low')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Spending_Score'] == 'Average')].value_counts()/ trainCluster.value_counts()) * 100,
                   (trainCluster[(trainSet['Spending_Score'] == 'High')].value_counts()/ trainCluster.value_counts()) * 100],
             index=trainSet.Spending_Score.unique())

"""> In segment ***D & A***, the dominant Spending Score is **Low**."""

plot_category(categorical=trainSet.Spending_Score)

"""> + Form ***count plot***, the **Profession** can distinguish between many ***Segments***, in case the **Spending Score** is
>> *Low* then the ***Segments*** should be **D**
>>
>> *Average* then the ***Segments*** should be **C**
> + From ***strip & boxen plots*** The distribution of **age** for each **category** can't distinguish between ***Segment*** using these 2-features.

### Family Size
"""

trainSet.Family_Size.unique()

plot_category(categorical=trainSet.Family_Size)

"""> + Form ***count plot***, the **Profession** can distinguish between many ***Segments***, in case the **Family Size** is
>> *1* then the ***Segments*** should be **A**
>>
>> *2* then the ***Segments*** should be **C**
> + From ***strip & boxen plots*** The distribution of **age** for each **category** can't distinguish between ***Segment*** using these 2-features.

### Var1
"""

trainSet.Var_1.unique()

plot_category(categorical=trainSet.Var_1)

"""> + Form ***count plot***, the **Var 1** can't distinguish between ***Segments***
> + From ***strip & boxen plots*** The distribution of **age** for each **category** can't distinguish between ***Segments*** using these 2-features.

## Observation
the Features that use to train model are 
* Ever Married
* Graduated
* Profession
* Spending_Score
* Family_Size
* Age
These feature can distinguish the **Segment D** quite clearly.

# Preprocessing
"""

trainSet = trainSet.loc[:, ['Ever_Married', 'Graduated', 'Profession', 'Spending_Score', 'Family_Size', 'Age']]
testSet = testSet.loc[:, ['Ever_Married', 'Graduated', 'Profession', 'Spending_Score', 'Family_Size', 'Age']]

trainSet.head()

"""## Handle Missing Values"""

trainSet.isnull().sum()

testSet.isnull().sum()

"""### Further Analysis"""

trainSet.groupby(['Ever_Married']).Graduated.value_counts()

"""the most **Married**  customers are **graduated** ***70.43%***"""

trainSet.groupby(['Spending_Score']).Graduated.value_counts()

"""the most **Average** Spending Scores are **graduated** ***74.24%***"""

# Handle Graduated
trainSet['Graduated'][(trainSet['Graduated'].isnull()) &  (trainSet['Spending_Score'] == 'Average')] = 'Yes'
trainSet['Graduated'][(trainSet['Graduated'].isnull())] = 'No'

testSet['Graduated'][(testSet['Graduated'].isnull()) &  (testSet['Spending_Score'] == 'Average')] = 'Yes'
testSet['Graduated'][(testSet['Graduated'].isnull())] = 'No'

trainSet.groupby(['Spending_Score']).Family_Size.value_counts()

trainSet.groupby(['Ever_Married']).Family_Size.value_counts()

# Handle Family Size
trainSet['Family_Size'][(trainSet['Family_Size'].isnull()) & (trainSet['Spending_Score'] == 'High')] = 2
trainSet['Family_Size'][(trainSet['Family_Size'].isnull()) & (trainSet['Ever_Married'] == 'Yes')] = 2
trainSet['Family_Size'][(trainSet['Family_Size'].isnull()) & (trainSet['Spending_Score'] == 'Low')] = 1

testSet['Family_Size'][(testSet['Family_Size'].isnull()) & (testSet['Spending_Score'] == 'High')] = 2
testSet['Family_Size'][(testSet['Family_Size'].isnull()) & (testSet['Ever_Married'] == 'Yes')] = 2
testSet['Family_Size'][(testSet['Family_Size'].isnull()) & (testSet['Spending_Score'] == 'Low')] = 1

trainSet.groupby(['Ever_Married']).Profession.value_counts()

trainSet.groupby(['Spending_Score']).Profession.value_counts()

# Handle Profession
trainSet['Profession'][(trainSet['Profession'].isnull()) & ((trainSet['Ever_Married'] == 'Yes') | (trainSet['Spending_Score'] == 'Average'))] = 'Artist'
trainSet['Profession'][(trainSet['Profession'].isnull()) & (trainSet['Ever_Married'] == 'No')] = 'Healthcare'
trainSet['Profession'][(trainSet['Profession'].isnull()) & (trainSet['Spending_Score'] == 'High')] = 'Executive'

testSet['Profession'][(testSet['Profession'].isnull()) & ((testSet['Ever_Married'] == 'Yes') | (testSet['Spending_Score'] == 'Average'))] = 'Artist'
testSet['Profession'][(testSet['Profession'].isnull()) & (testSet['Ever_Married'] == 'No')] = 'Healthcare'
testSet['Profession'][(testSet['Profession'].isnull()) & (testSet['Spending_Score'] == 'High')] = 'Executive'

# Handle Ever Married
trainSet['Ever_Married'].replace(np.nan, trainSet['Ever_Married'].mode()[0], inplace=True)
testSet['Ever_Married'].replace(np.nan, testSet['Ever_Married'].mode()[0], inplace=True)

trainSet.isnull().sum()

testSet.isnull().sum()

"""## Hot Encoding"""

trainSet = pd.get_dummies(trainSet, columns=['Ever_Married', 'Graduated', 'Profession'], drop_first=True)
trainSet['Spending_Score'].replace(['Low', 'Average', 'High'], [0,1,2], inplace=True)

testSet = pd.get_dummies(testSet, columns=['Ever_Married', 'Graduated', 'Profession'], drop_first=True)
testSet['Spending_Score'].replace(['Low', 'Average', 'High'], [0,1,2], inplace=True)

trainCluster.replace(['A', 'B', 'C', 'D'], [0,1,2, 3], inplace=True)
testCluser.replace(['A', 'B', 'C', 'D'], [0,1,2, 3], inplace=True)

trainSet.info()

"""# Correlations"""

py.figure(figsize=(15,5))
sb.pairplot(data=pd.concat([trainSet, trainCluster], axis=1), hue="Segmentation")

py.figure(figsize=(15,5))
sb.heatmap(trainSet.corr(), annot=True)

"""Not found multicollinearity

# Model
"""

random_state = 45
max_itr = 500

"""## Clustering Models"""

def kmean(trainset=trainSet, actualClusters=trainCluster, testset=testSet, testClusters=testCluser, type_='k-means++',  clusters=4):
    """
    Run Kmean on the dataset
    :param trainset: Train DataSet
    :param actualClusters: The actual segmentations in training set
    :param testset: Test DataSet
    :param testClusters: The actual segmentations in testing set
    :param type_: type of initiation of KMeans, ('random' | 'k-means++')
    :param clusters: number of clusters that KMeans groups the data to them
    :return: predicted labels of  training set, predicted labels of  testng set 
    """
    model = KMeans(n_clusters=clusters, init=type_, random_state=random_state, max_iter=max_itr)
    model.fit(trainset)
    preds = model.predict(trainset)
    preds_test = model.predict(testset)
    
    print("silhouette score Train =", silhouette_score(trainset, preds))
    print("silhouette score Test = ", silhouette_score(testset, preds_test))
    return preds, preds_test

preds_train_or, preds_test_or = kmean()

sb.pairplot(data=pd.concat([trainSet, pd.Series(data=preds_train_or, name='Segmentation K', index= trainSet.index)], axis=1),  hue='Segmentation K')

"""The **Kmeans** splits the data in good way

#### Apply TSNA
"""

tsne = TSNE(random_state=random_state, init='pca')

low_dim_tsne = pd.DataFrame(tsne.fit_transform(trainSet))
low_dim_tsne['Segmentation KMeans'] = preds_train_or

low_dim_tsne_test = pd.DataFrame(tsne.fit_transform(testSet))
low_dim_tsne_test['Segmentation KMeans'] = preds_test_or

sb.pairplot(data=low_dim_tsne.loc[:, [0,1, 'Segmentation KMeans']], hue='Segmentation KMeans')

"""### Observation 
**Kmeans** is good enough. on orginal DataSet

## Classification Models
"""

def knn_fit(trainset=trainSet, trainClasess=trainCluster, testset=testSet, testClasses=testCluser):
    """
    To Chooce the best of k in  K-Nearest Neighbor
    :param trainset: Train DataSet
    :param trainClasess: The actual segmentations in training set
    :param testset: Test DataSet
    :param testClasses: The actual segmentations in testing set
    :return: None
    """
    train_error, test_error = [], []

    for k in range(3, 12, 2):
      model = KNeighborsClassifier(n_neighbors=k)
      model.fit(trainset, trainClasess)
      train_error.append(np.mean(model.predict(trainset) != trainClasess.values))
      test_error.append(np.mean(model.predict(testset) != testClasses.values))
      pass

    py.plot(range(3, 12, 2), train_error, label='Train Error') 
    py.plot(range(3, 12, 2), test_error, label='Test Error')
    py.xlabel('K values')
    py.ylabel('Error')
    py.legend()
    py.show()
    pass

def knn_apply(k, trainset=trainSet, trainClasess=trainCluster, testset=testSet, testClasses=testCluser):
    """
    Run K-Nearest Neighbor on the dataset
    :param k: Number of Nearest Neighbor for point
    :param trainset: Train DataSet
    :param trainClasess: The actual segmentations in training set
    :param testset: Test DataSet
    :param testClasses: The actual segmentations in testing set
    :return: model object
    """

    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(trainset, trainClasess)

    preds_train = model.predict(trainset)
    print("In Train Set")
    print('\t\t Accuracy Score = ', accuracy_score(trainClasess, preds_train))
    ConfusionMatrixDisplay(confusion_matrix(trainClasess, preds_train)).plot()
    py.title("Display Confusion Matrix for Train Set")
    py.show()
    print('\t\t Classification Report = ', classification_report(trainClasess, preds_train))

    preds_test = model.predict(testset)
    print("In Test Set")
    print('\t\t Accuracy Score = ', accuracy_score(testClasses, preds_test))
    ConfusionMatrixDisplay(confusion_matrix(testClasses, preds_test)).plot()
    py.title("Display Confusion Matrix for Test Set")
    py.show()
    print('\t\t Classification Report = ', classification_report(testClasses, preds_test))
  
    return model

def random_forest(trainset=trainSet, trainClasess=trainCluster, testset=testSet, testClasses=testCluser):
    """
    Run Random Forest on the dataset
    :param trainset: Train DataSet
    :param trainClasess: The actual segmentations in training set
    :param testset: Test DataSet
    :param testClasses: The actual segmentations in testing set
    :return: model object
    """
    model = RandomForestClassifier(random_state=random_state, n_estimators=300)
    model.fit(trainset, trainClasess)
    
    preds_train = model.predict(trainset)
    print("In Train Set")
    print('\t\t Accuracy Score = ', accuracy_score(trainClasess, preds_train))
    ConfusionMatrixDisplay(confusion_matrix(trainClasess, preds_train)).plot()
    py.title("Display Confusion Matrix for Train Set")
    py.show()
    print('\t\t Classification Report = ', classification_report(trainClasess, preds_train))

    preds_test = model.predict(testset)
    print("In Test Set")
    print('\t\t Accuracy Score = ', accuracy_score(testClasses, preds_test))
    ConfusionMatrixDisplay(confusion_matrix(testClasses, preds_test)).plot()
    py.title("Display Confusion Matrix for Test Set")
    py.show()
    print('\t\t Classification Report = ', classification_report(testClasses, preds_test))
    
    return model

def svm(trainset=trainSet, trainClasess=trainCluster, testset=testSet, testClasses=testCluser):
    """
    Run Support Vector Machine on the dataset
    :param trainset: Train DataSet
    :param trainClasess: The actual segmentations in training set
    :param testset: Test DataSet
    :param testClasses: The actual segmentations in testing set
    :return: model object
    """
    model = SVC(C=0.8, probability=True, kernel='linear', random_state=random_state, max_iter=max_itr)
    model.fit(trainset, trainClasess)
    
    preds_train = model.predict(trainset)
    print("In Train Set")
    print('\t\t Accuracy Score = ', accuracy_score(trainClasess, preds_train))
    ConfusionMatrixDisplay(confusion_matrix(trainClasess, preds_train)).plot()
    py.title("Display Confusion Matrix for Train Set")
    py.show()
    print('\t\t Classification Report = ', classification_report(trainClasess, preds_train))

    preds_test = model.predict(testset)
    print("In Test Set")
    print('\t\t Accuracy Score = ', accuracy_score(testClasses, preds_test))
    ConfusionMatrixDisplay(confusion_matrix(testClasses, preds_test)).plot()
    py.title("Display Confusion Matrix for Test Set")
    py.show()
    print('\t\t Classification Report = ', classification_report(testClasses, preds_test))
    
    return model

def adaboost(trainset=trainSet, trainClasess=trainCluster, testset=testSet, testClasses=testCluser):
    """
    Run Ada Boost on the dataset
    :param trainset: Train DataSet
    :param trainClasess: The actual segmentations in training set
    :param testset: Test DataSet
    :param testClasses: The actual segmentations in testing set
    :return: model object
    """
    model = AdaBoostClassifier(random_state=random_state, n_estimators=300)
    model.fit(trainset, trainClasess)
    
    preds_train = model.predict(trainset)
    print("In Train Set")
    print('\t\t Accuracy Score = ', accuracy_score(trainClasess, preds_train))
    ConfusionMatrixDisplay(confusion_matrix(trainClasess, preds_train)).plot()
    py.title("Display Confusion Matrix for Train Set")
    py.show()
    print('\t\t Classification Report = ', classification_report(trainClasess, preds_train))

    preds_test = model.predict(testset)
    print("In Test Set")
    print('\t\t Accuracy Score = ', accuracy_score(testClasses, preds_test))
    ConfusionMatrixDisplay(confusion_matrix(testClasses, preds_test)).plot()
    py.title("Display Confusion Matrix for Test Set")
    py.show()
    print('\t\t Classification Report = ', classification_report(testClasses, preds_test))
    
    return model

"""##### KNN

with actual lables
"""

knn_fit()

""" with Kmeans lables"""

knn_fit(trainClasess=pd.Series(preds_train_or), testClasses=pd.Series(preds_test_or))

knn_model = knn_apply(k=11, trainClasess=pd.Series(preds_train_or), testClasses=pd.Series(preds_test_or))

random_forest(trainClasess=pd.Series(preds_train_or), testClasses=pd.Series(preds_test_or))

svm(trainClasess=pd.Series(preds_train_or), testClasses=pd.Series(preds_test_or))

"""#### Observation
Original Data is not distributed properly to the actual segments. i.e there are no patterns. 

**`But the Kmeans groups the data well`**.

This is shown in the classification algorithms' handling of them.
"""