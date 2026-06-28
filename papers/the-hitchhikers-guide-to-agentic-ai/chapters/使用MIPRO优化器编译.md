# 使用 MIPRO 优化器编译  
optimizer = MIPROv2(  
    metric=answer_metric,  
    auto="medium",  # Controls optimization budget  
    auto="medium",  # 控制优化预算  
)  

compiled_agent = optimizer.compile(  
    RAGAgent(),  
    trainset=train_examples,  
    num_candidates=30,  
    max_bootstrapped_demos=4,  
    max_labeled_demos=16,  
)  

