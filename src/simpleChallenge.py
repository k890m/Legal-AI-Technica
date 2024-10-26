import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt

train_data = pd.read_json('data/unzipped_data/train.json')
test_data = pd.read_json('data/unzipped_data/test.json')

print("Training Data Sample:\n", train_data.head())
print("Test Data Sample:\n", test_data.head())

# Checking if there are duplicates in the training dataset
train_duplicates = train_data[train_data.duplicated(subset=['data'], keep=False)]
print(f"Duplicate Entries in Training Data: {len(train_duplicates)}")

# Checking if there are duplicates in the testing dataset
test_duplicates = test_data[test_data.duplicated(subset=['data'], keep=False)]
print(f"Duplicate Entries in Testing Data: {len(test_duplicates)}")

train_data['data_str'] = train_data['data'].astype(str)
test_data['data_str'] = test_data['data'].astype(str)

# Checking if there are duplicates between the dataset that could affect the training process
contamination = pd.merge(
    train_data[['data_str']],
    test_data[['data_str']],
    on='data_str',
    how='inner'
)

print(f"Contaminated Entries between Training and Test Sets: {len(contamination)}")

# Convert data to TF-IDF vectors
vectorizer = TfidfVectorizer()
train_vectors = vectorizer.fit_transform(train_data['data_str'])
test_vectors = vectorizer.transform(test_data['data_str'])

# Calculate cosine similarity between training and test data
similarity_matrix = cosine_similarity(test_vectors, train_vectors)

threshold = 0.9 
similar_entries_count = (similarity_matrix > threshold).sum(axis=1)
num_similar = (similar_entries_count > 0).sum()
print(f"Number of test entries similar to any training entry (similarity > {threshold}): {num_similar}")

similarity_scores_df = pd.DataFrame(similar_entries_count, columns=['Similarity Count'])
score_bins = pd.cut(similarity_scores_df['Similarity Count'], bins=[0, 1, 2, 3, 4, 5], right=False)
similarity_counts = score_bins.value_counts().sort_index()

# Visualize similarity counts
plt.figure(figsize=(10, 6))
similarity_counts.plot(kind='bar', color='skyblue')
plt.title('Count of Test Entries by Similarity Score Range')
plt.xlabel('Similarity Score Range')
plt.ylabel('Number of Entries')
plt.xticks(rotation=45)
plt.show()

