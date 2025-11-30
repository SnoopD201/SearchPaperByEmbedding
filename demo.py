from search import PaperSearcher

# Use local model (free)
searcher = PaperSearcher('nips2025_papers.json', model_type='local')

# Or use OpenAI (better quality)
# searcher = PaperSearcher('iclr2026_papers.json', model_type='openai')

searcher.compute_embeddings()

examples = [
    {
        "title": "Combinatorial Optimization",
        "abstract": "Large Language Model for Combinatorial Optimization"
    },
]

results = searcher.search(examples=examples, top_k=200)

searcher.display(results, n=200)
searcher.save(results, 'results.json')

