import time  
from app.agents.conversational_agent import run_conversational_agent_llm  
start = time.time()  
res = run_conversational_agent_llm(1, 'I want to watch a really good French sci-fi movie that is less than 2 hours long.')  
end = time.time()  
print(f'\nTotal Time (2 LLM Calls + SQL Match): {end - start:.4f} seconds')  
