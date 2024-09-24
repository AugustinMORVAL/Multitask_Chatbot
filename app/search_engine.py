from serpapi import GoogleSearch

class SerpAPISearchEngine:
    def __init__(self, api_key):
        self.api_key = api_key

    def run(self, query, search_type="web", num_results=10):
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": num_results
        }
        
        if search_type == "news":
            params["tbm"] = "nws"
        elif search_type == "images":
            params["tbm"] = "isch"
        elif search_type == "videos":
            params["tbm"] = "vid"
        elif search_type == "linkedin":
            params["q"] = f"site:linkedin.com {query}"
        elif search_type == "facebook":
            params["q"] = f"site:facebook.com {query}"
        
        search = GoogleSearch(params)
        results = search.get_dict()
        return results.get("organic_results", [])