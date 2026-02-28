import time  
from app.core.database import SessionLocal  
from app.ml.hybrid_recommender import HybridRecommender  
start = time.time()  
db = SessionLocal()  
recommender = HybridRecommender(db)  
res = recommender.recommend(user_id=1, top_n=10)  
end = time.time()  
print(f'Total Response Time: {end - start:.4f} seconds')  
