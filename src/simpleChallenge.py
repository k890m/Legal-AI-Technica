import pandas as pd

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
