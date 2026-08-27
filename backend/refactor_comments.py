import re
from pathlib import Path

def process_fetch():
    fp = Path('backend/scripts/fetch_news_dataset.py')
    content = fp.read_text(encoding='utf-8')
    
    # Remove large docstring
    content = re.sub(r'\"\"\"Collect a Task 2 clustering dataset.*?\"\"\"', '# script to scrape bbc news feeds for the clustering task', content, flags=re.DOTALL)
    
    # Remove block dividers
    content = re.sub(r'# -+\n# (.*?)\n# -+', r'# \1', content)
    
    # Replace numbered verbose comments
    content = content.replace('# 1. Fetch all feeds', '# get all feeds')
    content = content.replace('# 2. Apply the Economics relevance test to the RSS title + summary BEFORE\n    # downloading full articles.  Using the full rendered BBC page here can\n    # accidentally match unrelated related-story/footer text and mislabel\n    # general Business stories as Economics.', '# check if it actually belongs in economics before downloading the whole article to save time')
    content = content.replace('# 3. Fetch full article text, fall back to RSS title + description', '# try to grab full text, fallback to summary if bbc blocks us')
    content = content.replace('# 3. Deduplicate by canonical URL (exact match)', '# drop duplicate urls')
    content = content.replace('# 4. Deduplicate by normalised title (exact match)', '# drop duplicate titles')
    content = content.replace('# 6. The Economics filter was intentionally applied before article\n    # fetching, so deduplicated entries are now ready for the final corpus.', '# entries are filtered and ready now')
    content = content.replace('# 7. Build final documents', '# format for csv')
    content = content.replace('# 8. Category distribution', '# count categories')
    content = content.replace('# 9. Document length statistics', '# stats')
    content = content.replace('# 10. Validate', '# check if we have enough data')
    content = content.replace('# 11. Save CSV', '# save to csv')
    content = content.replace('# 12. Save metadata', '# save stats to json')
    content = content.replace('# Entry point', '# run it')
    
    fp.write_text(content, encoding='utf-8')

def process_search():
    fp = Path('backend/search/search_engine.py')
    content = fp.read_text(encoding='utf-8')
    
    content = content.replace('\"\"\"Point the long-lived query processor at the latest rebuilt indexes.\"\"\"', '# point query processor to the new indexes after a crawl')
    content = content.replace('\"\"\"Ranked keyword search using TF-IDF + cosine similarity.\"\"\"', '# standard search using tfidf and cosine similarity')
    content = content.replace('# Generate snippet from title + abstract', '# make snippet from title and abstract')
    
    content = re.sub(r'\"\"\"Exact phrase search using the positional index.*?\"\"\"', '# exact phrase search using the positional index (stopwords kept in so positions stay accurate)', content, flags=re.DOTALL)
    content = re.sub(r'\"\"\"Boolean search using sorted posting list operations.*?\"\"\"', '# boolean search using sorted sets', content, flags=re.DOTALL)
    content = re.sub(r'\"\"\"NEAR-k proximity search using the positional index.*?\"\"\"', '# find docs where terms are close to each other', content, flags=re.DOTALL)
    
    # inverted index
    fp_inv = Path('backend/indexing/inverted_index.py')
    c_inv = fp_inv.read_text(encoding='utf-8')
    c_inv = re.sub(r'\"\"\"Inverted index with frequency-based.*?\"\"\"', '# inverted index mapping words to doc ids', c_inv, flags=re.DOTALL)
    fp_inv.write_text(c_inv, encoding='utf-8')

    # pos index
    fp_pos = Path('backend/indexing/positional_index.py')
    c_pos = fp_pos.read_text(encoding='utf-8')
    c_pos = re.sub(r'\"\"\"Positional inverted index.*?\"\"\"', '# positional index for phrase and proximity searches', c_pos, flags=re.DOTALL)
    c_pos = c_pos.replace('# term -> {doc_id: [pos0, pos1, ...], ...}', '# maps terms to a dict of doc_ids and their positions')
    fp_pos.write_text(c_pos, encoding='utf-8')

def process_text():
    fp = Path('backend/preprocessing/text_preprocessor.py')
    content = fp.read_text(encoding='utf-8')
    content = re.sub(r'\"\"\"Tokenize text preserving original word positions.*?\"\"\"', '# tokenize but keep stopwords so positions dont get messed up for positional index', content, flags=re.DOTALL)
    content = re.sub(r'\"\"\"Tokenize a phrase query WITHOUT stopword removal.*?\"\"\"', '# tokenize a phrase query without dropping stopwords', content, flags=re.DOTALL)
    content = re.sub(r'\"\"\"Like :meth:preprocess_fields but returns position-tagged tokens.*?\"\"\"', '# preprocess fields but keep positions intact', content, flags=re.DOTALL)
    fp.write_text(content, encoding='utf-8')

def process_snippet():
    fp = Path('backend/search/snippet_generator.py')
    content = fp.read_text(encoding='utf-8')
    content = re.sub(r'\"\"\"Query-term-aware snippet extraction.*?\"\"\"', '# grabs the best sentence matching the query for search results', content, flags=re.DOTALL)
    content = content.replace('# Tokenize the raw text to find positions of query terms', '# find where the query terms are in the text')
    content = content.replace('# Find word boundaries in the original text (case-insensitive)', '# find word boundaries')
    content = content.replace('# Stem each word for matching', '# stem words to match query')
    content = content.replace('# Find sentences containing at least one query term', '# grab sentences with query terms')
    fp.write_text(content, encoding='utf-8')

try:
    process_fetch()
    process_search()
    process_text()
    process_snippet()
    print('Comments successfully refactored!')
except Exception as e:
    print(e)
