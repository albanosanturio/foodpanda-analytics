# If you haven't already set up Kaggle auth:
# 1. Go to https://www.kaggle.com/settings/account
# 2. Click "Create New API Token" (downloads kaggle.json)
# 3. Place it at: C:\Users\alban\.kaggle\kaggle.json

# Download the dataset
import kagglehub
import os

# Create data folder if it doesn't exist
#os.environ["KAGGLEHUB_CACHE"] = "/data"

# Download latest version
path = kagglehub.dataset_download("faheem113141/foodpanda-pakistan-customer-orders-and-churn-dataset", output_dir='./data')

#print("Path to dataset files:", path)
