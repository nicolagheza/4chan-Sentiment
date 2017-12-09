# 4chan-Sentiment

#### pull data loop:

1. get all threads 
2. for all threads, put their id's on a stack
3. for all id's on stack, fetch thread contents and sleep for 1 s
4. if no id's are left on the stack, go back to step 1
