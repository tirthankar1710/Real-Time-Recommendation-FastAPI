import os
from pathlib import Path
import pandas as pd
import numpy as np
from surprise import dump

from src.utils import read_yaml
from src.utils import create_folder_from_config, download_s3_folder

def load_model(config_file_path, job_id):
    # Creating the root directory
    folder_path = create_folder_from_config(config_file_path)
    if job_id == None:
        download_s3_folder(
            bucket_name='ml-recommendation-capstone',
            s3_folder=f'baseline-recommendation-artifacts/model_trainer',
            local_dir=folder_path
            )
    else:
        download_s3_folder(
            bucket_name='ml-recommendation-capstone',
            s3_folder=f'{job_id}/model_trainer',
            local_dir=folder_path
            )

class PredictionPipeline:
    def __init__(self, config_path):
        config = read_yaml(config_path)
        self._, self.model = dump.load(config.get("prediction").get("colab_model_path"))
        self.cosine_sim = np.load(config.get("prediction").get("cosine_sim_path"))
        self.indices = pd.read_pickle(config.get("prediction").get("indices_path"))
        self.content_df = pd.read_csv(config.get("prediction").get("content_df_path"))

    def get_hybrid_recommendations(self, user_id, parent_asin):
        """
        Using both content and collobarative filtering.
        """
        idx = self.indices[int(parent_asin)]
        idx = idx
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:31]
        product_indices = [i[0] for i in sim_scores]
        products = self.content_df.iloc[product_indices][['title_y', 'parent_asin']]
        products['estimate'] = 0

        for index, row in products.iterrows():
            product = row['parent_asin']
            estimate = self.model.predict(uid=user_id, iid=product).est
            products.at[index, 'estimate'] = estimate
        products = products.sort_values('estimate', ascending=False)
        top_5 = products.head(5)      
       
        return top_5.to_dict(orient='records')

if __name__ == "__main__":
    config_path = Path("src/config.yaml")
    load_model(config_path)