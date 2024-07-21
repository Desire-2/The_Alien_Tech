import subprocess

class AIProjectScoring:
    def __init__(self):
        pass

    def run_code(self, repo_url):
        # Clone the repo
        subprocess.run(["git", "clone", repo_url, "repo"])
        # Run the code and capture the output
        result = subprocess.run(["python", "repo/main.py"], capture_output=True, text=True)
        # Clean up by removing the cloned repo
        subprocess.run(["rm", "-rf", "repo"])
        return result.stdout, result.stderr

    def score_and_suggest(self, repo_url):
        output, errors = self.run_code(repo_url)
        score, details = self.calculate_score(output, errors)
        suggestions = self.generate_suggestions(errors)
        return score, details, suggestions

    def calculate_score(self, output, errors):
        score = 100
        details = []
        
        if errors:
            details.append('Errors detected in the code execution.')
            score -= 50  # Major penalty for errors
        
        if "SyntaxError" in errors:
            details.append('Syntax Error detected.')
            score -= 30
        
        if "NameError" in errors:
            details.append('Name Error detected.')
            score -= 20
        
        # Example: Check for specific output in stdout
        if "expected_output" not in output:
            details.append('Expected output not found.')
            score -= 10
        
        return max(score, 0), details

    def generate_suggestions(self, errors):
        suggestions = []
        
        if "SyntaxError" in errors:
            suggestions.append("There is a syntax error in your code. Please check your syntax.")
        if "NameError" in errors:
            suggestions.append("There is a name error. Did you use a variable that is not defined?")
        
        if not errors:
            suggestions.append("Your code ran successfully.")
        
        return suggestions

ai_project_scoring = AIProjectScoring()
