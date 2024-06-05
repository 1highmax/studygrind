# Studygrind
creating manim videos from abstract science topics for students

```bash
git clone https://github.com/ManimCommunity/manim.git # clone manim
(cd manim ; rm -r .git) # deleting the git folder to avoid clogging the embedding api with copies of all files
export DOCS_PATH=/where/you/cloned/manim
export OPENAI_API_KEY=sk-proj-......... 
python3 create.py # creates the embeddings vector database, takes very long, costs around 10cts
python3 ask.py # uses the vector database to write manim scripts
```