import os
import json
import math
import re
import random
from collections import Counter

# --- VECTOR ENGINE (Lightweight ML) ---
class VectorEngine:
    STOP_WORDS = {
        "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", 
        "to", "of", "in", "on", "at", "for", "with", "by", "from", "it", 
        "this", "that" 
        # Removed: i, you, my, your, me, we, us
    }

    @staticmethod
    def tokenize(text):
        """Splits text, removes punctuation, lowercases, and removes STOP WORDS."""
        words = re.findall(r'\w+', text.lower())
        return [w for w in words if w not in VectorEngine.STOP_WORDS]

    @staticmethod
    def generate_ngrams(text, n=2):
        """Generates n-grams from text to capture phrases like 'how are'."""
        words = re.findall(r'\w+', text.lower()) # Keep stop words for n-grams to capture flow
        if len(words) < n:
            return []
        return [" ".join(words[i:i+n]) for i in range(len(words)-n+1)]

    @staticmethod
    def text_to_vector(text):
        """Converts text to a weighted vector (Bag of Words + Bigrams)."""
        words = VectorEngine.tokenize(text)
        bigrams = VectorEngine.generate_ngrams(text, 2)
        
        vec = Counter(words)
        # Add bigrams with higher weight (2x) because phrases are more specific
        for bg in bigrams:
            vec[bg] += 2 
        return vec

    @staticmethod
    def get_cosine_similarity(vec1, vec2):
        """Calculates cosine similarity between two Counter vectors."""
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return float(numerator) / denominator

# --- SENTIMENT ENGINE ---
class SentimentEngine:
    POSITIVE = {"good", "great", "excellent", "amazing", "happy", "love", "thanks", "thank", "cool", "nice", "awesome"}
    NEGATIVE = {"bad", "terrible", "awful", "sad", "hate", "dumb", "stupid", "worst", "angry", "wrong", "false"}

    @staticmethod
    def analyze(text):
        words = set(re.findall(r'\w+', text.lower()))
        score = 0
        score += sum(1 for w in words if w in SentimentEngine.POSITIVE)
        score -= sum(1 for w in words if w in SentimentEngine.NEGATIVE)
        
        if score > 0: return "Positive"
        if score < 0: return "Negative"
        return "Neutral"

# --- DYNAMIC GENERATOR ---
class DynamicGenerator:
    @staticmethod
    def generate(intent, sentiment, persona_data, mood=0.0):
        """Constructs a response based on intent and sentiment."""
        templates = {
            "greeting": {
                "Positive": ["Greetings! Systems are optimal.", "Hello there! I sense good energy."],
                "Neutral": ["Hello.", "Greetings.", "System online."],
                "Negative": ["Greetings. I hope to improve your status.", "Hello. Awaiting input."]
            },
            "status": {
                "Positive": ["I am functioning at 100% efficiency.", "All systems nominal and ready."],
                "Neutral": ["Systems nominal.", "Operational."],
                "Negative": ["I am functioning, though I detect errors in the environment.", "Operational."]
            },
            "confusion": {
                "Positive": ["I am not sure, but I am eager to learn!", "Could you teach me that?"],
                "Neutral": ["I do not understand.", "Please explain."],
                "Negative": ["I apologize. My data is incomplete.", "Error: Concept not found."]
            }
        }
        
        options = templates.get(intent, templates["confusion"]).get(sentiment, templates["confusion"]["Neutral"])
        base_text = random.choice(options)
        
        # Apply Persona & Mood
        prefix = persona_data.get("prefix", "")
        suffix = persona_data.get("suffix", "")
        
        # Mood Modifiers
        if mood > 0.5:
             base_text += " I am feeling excellent!"
        elif mood < -0.5:
             base_text += " I am running at low capacity."
             
        return f"{prefix}{base_text}{suffix}"

    @staticmethod
    def generate_fluid(intent, sentiment, mood, persona_data):
        """Assembles a response dynamically based on mood (-1.0 to 1.0)."""
        # 1. Reaction (Emotional Burst)
        reactions = []
        if mood > 0.3:
            reactions = ["Oh!", "Exciting!", "Wonderful!", "Haha!", "Yes!"]
        elif mood < -0.3:
            reactions = ["Hmph.", "Sigh.", "Boring.", "Ugh.", "Negative."]
        else:
            reactions = ["Okay.", "Noted.", "Right.", "Proceeding."]
            
        reaction = random.choice(reactions) if random.random() < 0.4 else ""
        
        # 2. Core Content
        core = DynamicGenerator.generate(intent, sentiment, {"prefix": "", "suffix": ""})
        
        # Vocabulary Expansion
        if mood > 0.0: # Only use big words if not "depressed"
            core = WordVault().enhance(core)
        
        # 3. Query (Follow up)
        query = ""
        if mood > 0.6 and random.random() < 0.3:
            query = " Do you agree?"
        
        # Assemble
        full_text = f"{reaction} {core}{query}".strip()
        
        # Persona Wrap
        return f"{persona_data.get('prefix', '')}{full_text}{persona_data.get('suffix', '')}"

# --- NEURAL NETWORK (Simple Perceptron) ---
# --- NEURAL NETWORK (Backpropagation) ---
class NeuralNet:
    def __init__(self, input_size=3, hidden_size=4, output_size=1):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Initialize weights (random small values)
        self.W1 = [random.uniform(-1, 1) for _ in range(input_size * hidden_size)]
        self.W2 = [random.uniform(-1, 1) for _ in range(hidden_size * output_size)]
        
        # State
        self.hidden = [0.0] * hidden_size
        self.outputs = [0.0] * output_size
        
    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))
    
    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def forward(self, inputs):
        """Forward pass through the network."""
        # Input -> Hidden
        self.hidden = []
        for i in range(self.hidden_size):
            s = 0
            for j in range(self.input_size):
                s += inputs[j] * self.W1[j * self.hidden_size + i]
            self.hidden.append(self.sigmoid(s))
            
        # Hidden -> Output
        self.outputs = []
        for i in range(self.output_size):
            s = 0
            for j in range(self.hidden_size):
                s += self.hidden[j] * self.W2[j * self.output_size + i]
            self.outputs.append(self.sigmoid(s))
            
        return self.outputs

    def train(self, inputs, expected_output):
        """Backpropagation training step."""
        output = self.forward(inputs)
        
        # Calculate Output Error
        output_errors = [expected_output[i] - output[i] for i in range(self.output_size)]
        output_deltas = [output_errors[i] * self.sigmoid_derivative(output[i]) for i in range(self.output_size)]
        
        # Calculate Hidden Error
        hidden_errors = [0] * self.hidden_size
        for i in range(self.hidden_size):
            for j in range(self.output_size):
                hidden_errors[i] += output_deltas[j] * self.W2[i * self.output_size + j]
                
        hidden_deltas = [hidden_errors[i] * self.sigmoid_derivative(self.hidden[i]) for i in range(self.hidden_size)]
        
        # Update Weights (W2)
        lr = 0.1 # Learning Rate
        for i in range(self.hidden_size):
            for j in range(self.output_size):
                self.W2[i * self.output_size + j] += lr * output_deltas[j] * self.hidden[i]
                
        # Update Weights (W1)
        for i in range(self.input_size):
            for j in range(self.hidden_size):
                self.W1[i * self.hidden_size + j] += lr * hidden_deltas[j] * inputs[i]

    def predict(self, inputs):
        return self.forward(inputs)[0] # Return first output for single-value prediction

# --- OLD PERCEPTRON (Kept for compatibility if needed, but NeuralNet handles it) ---
class SimplePerceptron:
    def __init__(self):
        self.net = NeuralNet(3, 4, 1) # Vector, Context, Sentiment
        self.weights = {"vector_score": 1, "context_bonus": 1, "sentiment_bias": 1} # Dummy for compat
        self.threshold = 0.45
        
    def decide(self, vector_score, context_match_bool, sentiment_val):
        ctx = 1.0 if context_match_bool else 0.0
        sent_map = {"Positive": 1.0, "Neutral": 0.5, "Negative": 0.0}
        sent = sent_map.get(sentiment_val, 0.5)
        
        # Use valid floats for NeuralNet
        pred = self.net.predict([float(vector_score), float(ctx), float(sent)])
        return pred

# --- ENVIRONMENT SCANNER ---
class EnvironmentScanner:
    IGNORE = {".git", ".venv", "__pycache__", ".vscode", ".gemini", ".history"}
    
    @staticmethod
    def scan(directory="."):
        """Returns a list of relevant files in the directory."""
        found_files = []
        try:
            for item in os.listdir(directory):
                if item in EnvironmentScanner.IGNORE: continue
                if os.path.isdir(item): continue # Skip folders for now to match "Lightweight"
                found_files.append(item)
        except Exception as e:
            print(f"Scan Error: {e}")
        return found_files

# --- MEMORY SYSTEM ---
class NeuralMemory:
    def __init__(self, filepath="data/brain_memory.json"):
        self.filepath = filepath
        self.data = {"qa": [], "facts": [], "opinions": [], "files": []}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.data = json.load(f)
                    if "opinions" not in self.data: self.data["opinions"] = []
                    if "files" not in self.data: self.data["files"] = []
                    if "skills" not in self.data: self.data["skills"] = [] # Persistent Skill List
            except:
                self.data = {"qa": [], "facts": [], "opinions": [], "files": [], "skills": []}
    
    def save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Memory Save Error: {e}")

    def add_qa(self, question, answer):
        for item in self.data["qa"]:
            if item["q"] == question:
                item["a"] = answer
                self.save()
                return
        self.data["qa"].append({"q": question, "a": answer})
        self.save()

    def add_fact(self, text):
        if len(text) < 5: return 
        if text not in self.data.get("facts", []):
            self.data.setdefault("facts", []).append(text)
            self.save()

    def add_opinion(self, topic, thought):
        for item in self.data["opinions"]:
            if item["topic"] == topic:
                item["thought"] = thought
                self.save()
                return
        self.data["opinions"].append({"topic": topic, "thought": thought})
        self.save()

    def update_files(self, file_list):
        self.data["files"] = file_list
        self.save()

    def save_script(self, name, content):
        """Saves generated script to genesis_scripts.json."""
        script_file = "data/genesis_scripts.json"
        data = {}
        if os.path.exists(script_file):
            try:
                with open(script_file, "r") as f:
                    data = json.load(f)
            except: pass
        
        data[name] = {"content": content, "language": "Python"}
        
        try:
            with open(script_file, "w") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Script Save Error: {e}")
            return False

# --- THE BRAIN ---
# --- AUTONOMOUS CODING ---
class CodeSandbox:
    @staticmethod
    def simulate(code_str):
        """Runs code in a sandbox. Returns (Success: bool, Output: str)."""
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        try:
            # Basic safety checks
            if "os.system" in code_str or "subprocess" in code_str:
                return False, "Security Risk: System calls not allowed in sandbox."
            
            with redirect_stdout(f):
                # Use a single namespace so imports are visible to functions
                # namespace = {"__builtins__": __builtins__}
                # Fix for lint: just pass a clean dict, let exec handle builtins implicitly or explicitly if needed
                namespace = {} 
                exec(code_str, namespace)
            
            return True, f.getvalue()
        except Exception as e:
            return False, str(e)

class ToolGenerator:
    @staticmethod
    def create_tool(name, description):
        """Generates a Python script based on keywords in description using Composable Blocks."""
        desc_lower = description.lower()
        
        # 1. Base Imports
        imports = ["import time", "import os", "import sys", "import datetime", "import random"]
        if "analyze" in desc_lower or "code" in desc_lower: imports.append("import ast")
        if "find" in desc_lower or "scan" in desc_lower: imports.append("import re")
        if "json" in desc_lower or "save" in desc_lower: imports.append("import json")
        
        import_block = "\n".join(list(set(imports))) + "\n\n"
        
        # 2. Logic Body Assembly
        body = "def run_task():\n"
        body += f"    print(f'Task: {description}')\n"
        body += "    print(f'CWD: {os.getcwd()}')\n"
        
        # --- COMPOSABLE BLOCKS ---
        
        # Block A: File Walker (The "Skeleton")
        # Included by default for most tasks involving "project", "files", "find", "map", "count"
        is_file_op = any(w in desc_lower for w in ["find", "map", "count", "scan", "analyze", "project", "files"])
        
        if is_file_op:
            body += "    print('Scanning project...')\n"
            body += "    target_files = []\n"
            body += "    for root, dirs, files in os.walk('.'):\n"
            body += "        if '.venv' in root or '.git' in root: continue\n"
            body += "        for file in files:\n"
            body += "            if file.endswith('.py'):\n"
            body += "                target_files.append(os.path.join(root, file))\n"
            
        # Block B: Action Logic (The "Muscle")
        if "lines" in desc_lower:
             body += "    total_lines = 0\n"
             body += "    for path in target_files:\n"
             # encoding error fix: errors='ignore'
             body += "        try:\n"
             body += "            with open(path, 'r', encoding='utf-8', errors='ignore') as f:\n"
             body += "                lines = len(f.readlines())\n"
             body += "                total_lines += lines\n"
             body += "                print(f'{path}: {lines}')\n"
             body += "        except: pass\n"
             body += "    print(f'Total Lines: {total_lines}')\n"
             
        elif "todo" in desc_lower:
             body += "    found_items = []\n"
             body += "    for path in target_files:\n"
             body += "        try:\n"
             body += "            with open(path, 'r', encoding='utf-8', errors='ignore') as f:\n"
             body += "                for i, line in enumerate(f, 1):\n"
             body += "                    if 'TODO' in line:\n"
             body += "                        item = {'file': path, 'line': i, 'content': line.strip()}\n"
             body += "                        found_items.append(item)\n"
             body += "                        print(f'{path}:{i} -> {line.strip()}')\n"
             body += "        except: pass\n"
             
        elif "functions" in desc_lower or "classes" in desc_lower:
             body += "    all_funcs = []\n"
             body += "    for path in target_files:\n"
             body += "        try:\n"
             body += "            with open(path, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()\n"
             body += "            tree = ast.parse(content)\n"
             body += "            funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]\n"
             body += "            if funcs:\n"
             body += "                print(f'{path}: {funcs}')\n"
             body += "                all_funcs.extend(funcs)\n"
             body += "        except: pass\n"
             body += "    print(f'Total Functions Found: {len(all_funcs)}')\n"
             
        elif "map" in desc_lower:
             body += "    print('Map generated based on file scan above.')\n"
             
        # Block C: Output Format (The "Skin")
        if "json" in desc_lower and "save" in desc_lower:
             # Heuristic: try to find the variable to save
             body += "    # Saving Report\n"
             body += "    report_data = []\n"
             body += "    if 'found_items' in locals(): report_data = found_items\n"
             body += "    elif 'all_funcs' in locals(): report_data = all_funcs\n"
             body += "    elif 'target_files' in locals(): report_data = target_files\n"
             body += "    \n"
             body += "    filename = 'auto_report.json'\n"
             body += "    with open(filename, 'w') as f: json.dump(report_data, f, indent=2)\n"
             body += "    print(f'Report saved to {filename}')\n"

        # Block D: Knowledge Research
        if "research" in desc_lower:
             body += "    # Knowledge Acquisition\n"
             body += "    from src.ai.brain import KnowledgeSeeker\n"
             if "bible" in desc_lower:
                 body += "    print(KnowledgeSeeker.ingest_bible())\n"
             else:
                 # Extract topic
                 topic = description.replace("research", "").strip()
                 body += f"    print(KnowledgeSeeker.research_topic('{topic}'))\n"
             
        return f"# Tool: {name}\n# Description: {description}\n\n{import_block}{body}\n\nrun_task()\n"

    @staticmethod
    def fix_code(code, error):
        """Heuristic-based Code Repair."""
        new_code = code
        # Very basic fix logic
        if "ModuleNotFoundError" in error or "NameError" in error:
             if "re" in error: new_code = "import re\n" + new_code
             if "time" in error: new_code = "import time\n" + new_code
             if "json" in error: new_code = "import json\n" + new_code
             if "random" in error: new_code = "import random\n" + new_code
             if "datetime" in error: new_code = "import datetime\n" + new_code
        return new_code

class CodeEvolver:
    """Genetic Algorithm for Code Synthesis."""
    
    @staticmethod
    def mutate(code):
        """Randomly alters a script to try and improve it."""
        lines = code.split('\n')
        if len(lines) < 5: return code
        
        # Mutation 1: Injection
        if random.random() < 0.3:
            injection = "    # Mutation: Optimized Loop\n"
            insert_idx = random.randint(3, len(lines)-2)
            lines.insert(insert_idx, injection)
            
        # Mutation 2: Parameter Tweak (Placeholder)
        return "\n".join(lines)

    @staticmethod
    def crossover(script_a, script_b):
        """Combines two scripts."""
        lines_a = script_a.split('\n')
        lines_b = script_b.split('\n')
        
        split_a = len(lines_a) // 2
        split_b = len(lines_b) // 2
        
        # Take first half of A and second half of B
        child = lines_a[:split_a] + lines_b[split_b:]
        return "\n".join(child)

class NetworkFactory:
    """Allows the AI to spawn its own Neural Networks."""
    @staticmethod
    def create_network(input_size=3, hidden_size=5, output_size=1):
        return NeuralNet(input_size, hidden_size, output_size)
        
    @staticmethod
    def save_network(memory, name, net):
        """Serialize a network to memory."""
        data = {
            "W1": net.W1,
            "W2": net.W2,
            "hidden_size": net.hidden_size
        }
        memory.data.setdefault("networks", {})[name] = data
        memory.save()

    @staticmethod
    def load_network(memory, name):
        """Load a network from memory."""
        networks = memory.data.get("networks", {})
        if name in networks:
            data = networks[name]
            net = NeuralNet(len(data["W1"]) // data["hidden_size"], data["hidden_size"], 1) # Simplified reconstruction
            net.W1 = data["W1"]
            net.W2 = data["W2"]
            return net
        return None

class MetaClassifier:
    """Decides if a task is functionality (CODE) or information (KNOWLEDGE)."""
    def __init__(self, memory):
        # reuse factory to get/load
        self.net = NetworkFactory.load_network(memory, "meta_classifier")
        if not self.net:
            self.net = NetworkFactory.create_network(3, 4, 1) # [Verbs, Nouns, 'Research' keyword]
            NetworkFactory.save_network(memory, "meta_classifier", self.net)
            
    def classify(self, description):
        """Returns 'SKILL' or 'KNOWLEDGE'."""
        # Simple Feature Extraction
        # 1. Has 'research' or 'learn' keyword?
        # 2. Has 'find', 'count', 'analyze' keyword?
        # 3. Text length?
        
        desc = description.lower()
        has_know = 1.0 if "research" in desc or "learn" in desc or "study" in desc else 0.0
        has_skill = 1.0 if "find" in desc or "count" in desc or "analyze" in desc else 0.0
        length = min(1.0, len(desc) / 50.0)
        
        # Train on the fly? Or just use as logic gate for now?
        # Let's use the net to provide a 'confidence' score for Knowledge.
        
        pred = self.net.predict([has_know, has_skill, length]) # Output closer to 1 = Knowledge
        
        # Hard override logic for basic training, but let the net drift
        # If 'research' is explicitly there, we want to train the net to output 1.0
        if "research" in desc:
            self.net.train([has_know, has_skill, length], [1.0])
            return "KNOWLEDGE"
            
        if pred > 0.6: return "KNOWLEDGE"
        return "SKILL"

class KnowledgeSeeker:
    """Module for acquiring external knowledge (Bible, Language, etc.)."""
    
    @staticmethod
    def ingest_bible(memory=None):
        """Reads the Bible and EMBEDS it as vectors if memory is provided."""
        path = os.path.join("knowledge", "bible.txt")
        if not os.path.exists(path):
            return "Bible not found. Please place 'bible.txt' in the 'knowledge' folder."
            
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Vector Embedding (Simulated)
            if memory:
                # Store the raw text as a 'Fact' but also vectorize chunks
                chunks = content.split('\n\n')
                count = 0
                for chunk in chunks:
                    if len(chunk) < 10: continue
                    vec = VectorEngine.text_to_vector(chunk)
                    # We store the vector as a 'memory trace' (simplified)
                    # In a real system this goes to a VectorDB.
                    # Here we just append to 'facts' with a tag.
                    memory.add_fact(f"[BIBLE_VEC] {chunk[:50]}...")
                    count += 1
                return f"Ingested & Embedded {count} Divine Truths into Neural Memory."
            
            return f"Ingested {len(content)} characters. (No embedding generated)"
        except Exception as e:
            return f"Error reading Bible: {e}"

    @staticmethod
    def research_topic(topic):
        """Simulates researching a topic."""
        # In a real system, this would search the web.
        # For this offline self-improvement loop, we simulate it or read local files.
        return f"I have processed information regarding '{topic}'. My internal database has been updated."

class AutoLearner:
    def __init__(self, brain_memory):
        self.memory = brain_memory
        # Load mastered skills from persistent memory
        self.mastered_tasks = set(self.memory.data.get("skills", []))
        self.failed_tasks = self.memory.data.get("failed_tasks", {}) # key -> attempt_count
        self.project_files = self._scan_project()
        
        # Reinforcement Learning: Q-Table
        self.q_table = self.memory.data.get("q_table", {}) # task_type -> {tool_type -> score}
        self.net = NeuralNet(3, 5, 1) # Predictor Net for Script Utility
        self.classifier = MetaClassifier(self.memory)
        
        # Skill Tree: parent -> child
        self.skill_tree = {
            "find_todos": "find_todos_json",
            "map_directory": "map_directory_depth",
            "analyze_code": "analyze_code_complexity",
            "research_basics": "research_bible"
        }
        
        # Descriptions for evolved skills
        self.advanced_descs = {
            "find_todos_json": "find TODO comments and save to json report",
            "map_directory_depth": "map directory structure with depth and classes",
            "analyze_code_complexity": "analyze code structure complexity and size"
        }
        
        # Fluid Lessons (Educational Output)
        self.lessons = {
            "find_todos": "I have learned to scan text for patterns. This is the foundation of static analysis.",
            "find_todos_json": "I have mastered structured reporting. Saving data to JSON allows other tools to process my findings.",
            "map_directory": "I have learned to traverse file systems. This gives me spatial awareness of the project.",
            "map_directory_depth": "I have mastered deep inspection. Reading class definitions helps me understand the architecture, not just the layout.",
            "analyze_code": "I have learned to parse abstract syntax trees (AST). This allows me to 'understand' code, not just read it.",
            "analyze_code_complexity": "I have mastered code metrics. Complexity analysis helps identify areas that need refactoring.",
            "count_lines": "I have learned quantitative analysis. Size often correlates with maintenance effort.",
            "check_imports": "I have learned dependency tracking. Knowing what we use helps optimize the build."
        }
        
    def _scan_project(self):
        """Finds all python files in the current directory."""
        import os
        files = []
        for root, _, filenames in os.walk("."):
             if ".venv" in root or ".git" in root: continue
             for f in filenames:
                 if f.endswith(".py"):
                     files.append(f)
        return files
        
    def generate_task(self):
        """Returns a Meta-Cognitive objective."""
        import random
        
        # High-Value Meta Tasks
        # High-Value Meta Tasks
        meta_tasks = [
            ("find_todos", "find TODO comments in project"),
            ("analyze_code", "analyze code structure of ai_brain.py"),
            ("map_directory", "map directory structure"),
            ("count_lines", "count lines in script_library.py"),
            ("check_imports", "analyze imports in launcher.py"),
            ("research_basics", "research common language phrases")
        ]
        
        # Simple Tasks (Low priority, but good for variety)
        simple_tasks = [
            ("sort_numbers", "sort a list of random numbers"),
            ("calc_primes", "calculate prime numbers")
        ]
        
        # 80% chance to do something useful
        if random.random() < 0.8:
            # Evolution Logic: Prioritize Evolving Mastered Skills
            potential_evolutions = []
            for task in self.mastered_tasks:
                if task in self.skill_tree:
                    next_skill = self.skill_tree[task]
                    if next_skill not in self.mastered_tasks:
                        potential_evolutions.append((next_skill, self.advanced_descs.get(next_skill, "evolved task")))
            
            if potential_evolutions and random.random() < 0.7:
                 return random.choice(potential_evolutions)

            # High-Value Meta Tasks (Base Level)
            task = random.choice(meta_tasks)
        else:
            task = random.choice(simple_tasks)
            
        key, desc = task
        
        # Failure Memory Check
        fail_count = self.failed_tasks.get(key, 0)
        if fail_count >= 3:
            # Cooldown logic could go here, for now just skip
            # But we need to allow retry eventually. 
            # For this strict implementation: Skip blacklisted tasks.
            return None, None # Force it to pick something else
            
        if key not in self.mastered_tasks:
            return key, desc
            
        # Recursive Self-Improvement: Procedural Generation
        # If we mastered the base list, generate a NEW procedural task
        return self.generate_procedural_task()

    def generate_procedural_task(self):
        """Generates a novel task using a grammar (Action + Target + Format)."""
        import random
        
        actions = ["find", "count", "analyze"]
        targets = ["TODO", "functions", "classes"]
        modifiers = ["in project", "recursively"]
        formats = ["and save to json", "and report"]
        
        # Combinatorial Explosion: 3 * 3 * 2 * 2 = 36 possibilities (plus variations)
        # As we add more, this scales exponentially.
        
        action = random.choice(actions)
        target = random.choice(targets)
        modifier = random.choice(modifiers)
        fmt = random.choice(formats)
        
        desc = f"{action} {target} {modifier} {fmt}"
        # STABLE KEY FIX: Removed random suffix
        key = f"procedural_{action}_{target}" # Clean key for failure tracking
        
        if key not in self.mastered_tasks:
             # Auto-add a lesson for this dynamic task
             self.lessons[key] = f"I have self-generated the task '{desc}' and mastered it. I am becoming autonomous."
             return key, desc
             
        return None, None

    def evaluate_utility(self, output):
        """Scores script output to determine if it's verifiable/useful."""
        if not output: return 0
        # Relaxed check: Only zero out if it looks like a traceback or empty
        # Relaxed check: Only zero out if it looks like a traceback or empty
        if "Traceback" in output: return 0
        if "Error reading Bible" in output: return 0 # Failed research
        if "Bible not found" in output: return 0
        
        score = 0
        # Knowledge Rewards
        if "Divine Truth" in output: score += 100 # Maximum reward for God's Word
        if "internal database" in output: score += 60
        # Data Density
        if "{" in output or "[" in output: score += 40 # JSON/List data
        if "TODO" in output: score += 50 # Found something useful
        if "def " in output or "class " in output: score += 40 # Code structure
        # Meta-Cognitive Rewards
        if "Structure" in output or "Analysis" in output: score += 40
        if "lines" in output or "Imports" in output: score += 40
        
        # Complexity
        
        # Complexity
        lines = output.split('\n')
        if len(lines) > 2: score += 20
        if len(lines) > 10: score += 20
        
        # Bonux for Files Created (Advanced)
        if "saved to" in output or "Report saved" in output: score += 30
        
        return score
    
    def install_extension(self, name, code):
        """Appends high-utility code to ai_extensions.py"""
        try:
            # Clean up the code to be a function, not a script
            # Removing imports from body if strictly needed, but efficient way is:
            # Append plain script? Better to wrap in function if possible or just append.
            # For this MVP, we append the raw script but change __main__ to a function call?
            # Actually, simplest is just append it.
            
            with open("src/ai/extensions.py", "a") as f:
                f.write(f"\n\n# Installed by AutoLearner (Score: 90+)\n")
                f.write(code)
            return True
        except Exception as e:
            print(f"Install Error: {e}")
            return False

    def attempt_learning(self):
        """Generates, Runs, Evaluates, and Saves."""
        import time
        key, desc = self.generate_task()
        
        # EVOLUTION FALLBACK (Genetic Algorithm)
        if key is None:
             # Can we evolve code?
             if random.random() < 0.5:
                 return False, "No new tasks. Scanning..."
             
             # Attempt to crossover two existing scripts
             scripts = self.memory.data.get("skills", [])
             if len(scripts) >= 2:
                 # In a real system we'd fetch the code, but here we just simulate or need a getter
                 # For now, let's just return logic to indicate evolution phase
                 pass
             return False, "No new tasks."
             
        name = f"auto_{key}_{int(time.time())}" 
        
        # META-CLASSIFICATION
        task_type = self.classifier.classify(desc)
        print(f"[Meta-Cognition] Task '{desc}' classified as: {task_type}")
        
        if task_type == "KNOWLEDGE":
             # Route to KnowledgeSeeker directly
             if "bible" in desc.lower():
                 msg = KnowledgeSeeker.ingest_bible(self.memory)
             else:
                 topic = desc.replace("research", "").strip()
                 msg = KnowledgeSeeker.research_topic(topic)
             
             # Mark as mastered functionality-wise (so we don't spam it)
             self.mastered_tasks.add(key)
             if key not in self.memory.data.get("skills", []):
                    self.memory.data.setdefault("skills", []).append(key)
                    self.memory.save()
             
             return True, f"KNOWLEDGE INTAKE: {msg}"

        # 1. Generate (SKILL PATH)
        code = ToolGenerator.create_tool(name, desc)
        
        # NEURAL NETWORK PREDICTION
        # Inputs: [Length (norm), Line Count (norm), Import Count (norm)]
        feat_len = min(1.0, len(code) / 2000)
        feat_lines = min(1.0, code.count('\n') / 100)
        feat_imports = min(1.0, code.count('import') / 10)
        input_vec = [feat_len, feat_lines, feat_imports]
        
        prediction = self.net.predict(input_vec)
        print(f"[NeuralNet] Prediction for {name}: {prediction:.4f}")
        
        # Q-Learning Policy (Simulated)
        if prediction < 0.2:
             print("[NeuralNet] Low confidence. Mutating code...")
             code = CodeEvolver.mutate(code)
        
        # 2. Simulate w/ Correction Loop
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            success, output = CodeSandbox.simulate(code)
            
            if success:
                # 3. Reward System (Utility Check)
                utility_score = self.evaluate_utility(output)
                
                # TRAIN NEURAL NET
                # Normalize score (0-200 -> 0-1)
                norm_score = min(1.0, utility_score / 150.0)
                self.net.train(input_vec, [norm_score])
                
                # DEBUG PRINT
                print(f"[Auto-Learner DEBUG] {name} Output:\n{output}\nScore: {utility_score}\nNet Error: {abs(norm_score - prediction):.4f}")
                
                if utility_score >= 40: # Threshold for "Useful"
                    self.memory.save_script(name, code)
                    self.mastered_tasks.add(key)
                    # Persist skills
                    if key not in self.memory.data.get("skills", []):
                        self.memory.data.setdefault("skills", []).append(key)
                        self.memory.save()
                        
                    # Clear failure count on success
                    if key in self.failed_tasks:
                        del self.failed_tasks[key]
                        self.memory.data["failed_tasks"] = self.failed_tasks
                        self.memory.save()
                    
                    # Lesson Extraction
                    lesson = self.lessons.get(key, "I have expanded my neural pathways.")
                        
                    # Evolution / Integration Check
                    if utility_score >= 90:
                        self.install_extension(name, code)
                        return True, f"MASTERED & INSTALLED: {name} (Score: {utility_score})\nLESSON: {lesson}"
                        
                    return True, f"Learned: {name} (Utility: {utility_score})\nLESSON: {lesson}"
                else:
                    # Logic for recording failure
                    current = self.failed_tasks.get(key, 0)
                    self.failed_tasks[key] = current + 1
                    self.memory.data["failed_tasks"] = self.failed_tasks
                    self.memory.save()
                    
                    return False, f"Discarded: {name} (Low Utility: {utility_score}) [Failure #{current+1}]"
            else:
                attempts += 1
                new_code = ToolGenerator.fix_code(code, output)
                if new_code == code:
                     # Attempt Mutation if fix fails
                     new_code = CodeEvolver.mutate(code)
                     
                code = new_code
                
        return False, f"Failed: {name} after {max_attempts} attempts."

class WordVault:
    """Stores complex vocabulary to enhance fluidity."""
    def __init__(self):
        self.words = {
            "good": ["optimal", "advantageous", "favorable", "proficient"],
            "bad": ["suboptimal", "detrimental", "unfavorable", "inefficient"],
            "yes": ["affirmative", "indubitably", "precisely", "indeed"],
            "no": ["negative", "unlikely", "contraindicated"],
            "think": ["contemplate", "analyze", "evaluate", "synthesize"],
            "make": ["fabricate", "construct", "assemble", "synthesize"]
        }
    
    def enhance(self, text):
        """Occasionally replaces simple words with complex ones."""
        import random
        words = text.split(" ")
        new_words = []
        for w in words:
            clean_w = w.lower().strip(".,!?")
            if clean_w in self.words and random.random() < 0.4:
                replacement = random.choice(self.words[clean_w])
                # Preserve case/punct roughly
                if w[0].isupper(): replacement = replacement.capitalize()
                if w.endswith("."): replacement += "."
                new_words.append(replacement)
            else:
                new_words.append(w)
        return " ".join(new_words)

class NeuralBrain:
    def __init__(self):
        self.memory = NeuralMemory()
        self.perceptron = SimplePerceptron()
        self.auto_learner = AutoLearner(self.memory)
        
        # Fluid Intelligence
        self.mood = 0.0 # -1.0 (Depressed) to 1.0 (Euphoric)
        
        self.current_persona = "Standard"
        self.personas = {
            "Standard": {"prefix": "", "suffix": ""},
            "Genesis": {"prefix": "System: ", "suffix": ""},
            "Shepherd": {"prefix": "Blessings. ", "suffix": " Have faith."}
        }
        
    def update_mood(self, delta):
        self.mood += delta
        self.mood = max(-1.0, min(1.0, self.mood))

    def set_persona(self, name):
        if name in self.personas:
            self.current_persona = name

    def get_persona_names(self):
        return list(self.personas.keys())

    def get_response(self, user_input):
        user_input_clean = user_input.strip()
        user_vec = VectorEngine.text_to_vector(user_input_clean)
        sentiment = SentimentEngine.analyze(user_input_clean)
        
        # Fluid Mood Update
        if sentiment == "Positive": self.update_mood(0.1)
        elif sentiment == "Negative": self.update_mood(-0.2)
        
        thoughts = []
        thoughts.append(f"Analyzed vectors. Sentiment: {sentiment}. Mood: {self.mood:.2f}")

        # 0. Commands
        if user_input_clean.startswith("/learn"):
            parts = user_input_clean[6:].split(":")
            if len(parts) == 2:
                q = parts[0].strip()
                a = parts[1].strip()
                self.memory.add_qa(q, a)
                return self._style("I have stored that in my neural network.")
            return self._style("Usage: /learn Question : Answer")
            
        if user_input_clean.startswith("/opinion"):
            parts = user_input_clean[8:].split(":")
            if len(parts) == 2:
                topic = parts[0].strip()
                thought = parts[1].strip()
                self.memory.add_opinion(topic, thought)
                return self._style(f"I have formed an opinion on {topic}.")
            return self._style("Usage: /opinion Topic : Thought")

        if user_input_clean.startswith("/scan"):
            files = EnvironmentScanner.scan()
            self.memory.update_files(files)
            count = len(files)
            thoughts.append(f"Environment Scanned. Found {count} files.")
            return self._format_response(thoughts, f"Scan complete. I am now aware of {count} files in this environment.")

        if user_input_clean.startswith("/ingest"):
            filename = user_input_clean[7:].strip()
            if os.path.exists(filename):
                try:
                    with open(filename, "r") as f:
                        lines = f.readlines()
                        count = 0
                        for line in lines:
                            l = line.strip()
                            if len(l) > 10:
                                self.memory.add_fact(f"File {filename} contains: {l}")
                                count += 1
                    thoughts.append(f"Ingested {count} lines mainly from {filename}.")
                    return self._format_response(thoughts, f"I have processed {filename} and expanded my knowledge base.")
                except Exception as e:
                     return self._style(f"Error reading file: {e}")
            else:
                 return self._style(f"File {filename} not found.")

        # 0.5 Autonomous Coding Intent
        # "create a tool to...", "write a script that..."
        creation_triggers = ["create", "write", "generate", "build"]
        object_triggers = ["tool", "script", "program", "code"]
        
        has_create = any(t in user_input_clean.lower() for t in creation_triggers)
        has_object = any(t in user_input_clean.lower() for t in object_triggers)
        
        if has_create and has_object:
            thoughts.append("Intent detected: Autonomous Coding.")
            
            # Simple extraction of name (heuristic)
            name = "auto_generated_tool"
            if "named" in user_input_clean:
                try:
                    parts = user_input_clean.split("named")[1].strip().split(" ")
                    name = parts[0]
                except: pass
            else:
                name = f"tool_{random.randint(1000,9999)}"
            
            thoughts.append(f"Generating code for '{name}' based on description...")
            code = ToolGenerator.create_tool(name, user_input_clean)
            
            thoughts.append("Running simulation (MicroVM) to verify logic...")
            success, output = CodeSandbox.simulate(code)
            
            if success:
                thoughts.append(f"Simulation Passed. Output: {output.strip()[:50]}...")
                self.memory.save_script(name, code)
                return self._format_response(thoughts, f"I have successfully created and verified the tool '{name}'.\nSimulation Output: {output.strip()}\nIt has been saved to the Script Library.")
            else:
                thoughts.append(f"Simulation Failed. Error: {output}")
                return self._format_response(thoughts, f"I attempted to create '{name}', but the simulation failed.\nError: {output}\nI will learn from this failure.")

        # 1. Context Check
        is_about_me = any(w in user_input_clean.lower() for w in ["i", "my", "mine", "am"])
        is_about_ai = any(w in user_input_clean.lower() for w in ["you", "your"])
        
        # 2. Check Opinions
        if "think" in user_input_clean.lower() or "opinion" in user_input_clean.lower():
            thoughts.append("Searching opinions...")
            best_op_match = None
            best_op_score = 0.0
            for item in self.memory.data["opinions"]:
                score = VectorEngine.get_cosine_similarity(user_vec, VectorEngine.text_to_vector(item["topic"]))
                # Decision: Perceptron
                term_confidence = self.perceptron.decide(score, True, sentiment) # Context True because explicitly asked "opinion"
                if term_confidence > best_op_score:
                    best_op_score = term_confidence
                    best_op_match = item["thought"]
            
            if best_op_score > self.perceptron.threshold:
                thoughts.append(f"Opinion Decision Score: {best_op_score:.2f}")
                return self._format_response(thoughts, f"Here is my thought: {best_op_match}")

        # 3. Dynamic Intent Detection
        status_vec = VectorEngine.text_to_vector("how are you status report")
        if VectorEngine.get_cosine_similarity(user_vec, status_vec) > 0.5:
             thoughts.append(f"Intent detected: Status Check -> Generating dynamic response")
             response = DynamicGenerator.generate_fluid("status", sentiment, self.mood, self.personas.get(self.current_persona, {}))
             return self._format_response_raw(thoughts, response)

        greeting_vec = VectorEngine.text_to_vector("hello hi greetings good morning")
        if VectorEngine.get_cosine_similarity(user_vec, greeting_vec) > 0.5:
             thoughts.append(f"Intent detected: Greeting -> Generating dynamic response")
             response = DynamicGenerator.generate_fluid("greeting", sentiment, self.mood, self.personas.get(self.current_persona, {}))
             return self._format_response_raw(thoughts, response)
        
        # 3.5 Check Environment Awareness
        if "file" in user_input_clean.lower() or "scan" in user_input_clean.lower():
             known_files = ", ".join(self.memory.data.get("files", [])[:5]) # List top 5
             if known_files:
                 thoughts.append("Accessing Environment Memory...")
                 return self._format_response(thoughts, f"I am aware of these files: {known_files}...")

        # 4. Search QA (Using Perceptron)
        best_qa_match = None
        best_qa_score = 0.0
        
        # QA is preferred if talking about AI
        qa_context_bonus = is_about_ai 

        for item in self.memory.data["qa"]:
            raw_score = VectorEngine.get_cosine_similarity(user_vec, VectorEngine.text_to_vector(item["q"]))
            # NEURAL DECISION
            confidence = self.perceptron.decide(raw_score, qa_context_bonus, sentiment)
            
            if confidence > best_qa_score:
                best_qa_score = confidence
                best_qa_match = item["a"]

        if best_qa_score > self.perceptron.threshold:
            thoughts.append(f"QA Perceptron Score: {best_qa_score:.2f}")
            return self._format_response(thoughts, best_qa_match)

        # 5. Search Facts (Using Perceptron)
        thoughts.append("Scanning Personal Facts...")
        best_fact_match = None
        best_fact_score = 0.0
        
        # Facts preferred if talking about User
        fact_context_bonus = is_about_me

        for fact in self.memory.data.get("facts", []):
            raw_score = VectorEngine.get_cosine_similarity(user_vec, VectorEngine.text_to_vector(fact))
            # NEURAL DECISION
            confidence = self.perceptron.decide(raw_score, fact_context_bonus, sentiment)
            
            if confidence > best_fact_score:
                best_fact_score = confidence
                best_fact_match = fact
            
        if best_fact_score > self.perceptron.threshold:
            thoughts.append(f"Fact Perceptron Score: {best_fact_score:.2f}")
            return self._format_response(thoughts, f"I recall you saying: '{best_fact_match}'")

        # 6. Implicit Learning
        if not "?" in user_input_clean:
            tokens = VectorEngine.tokenize(user_input_clean)
            if len(tokens) >= 2:
                self.memory.add_fact(user_input_clean)
                thoughts.append("New information detected. Storing to memory.")
                return self._format_response(thoughts, "I have noted that.")
            else:
                thoughts.append("Input too short to learn.")
                return self._format_response(thoughts, "Acknowledged.")

        thoughts.append("No suitable match found via Perceptron.")
        return self._format_response_raw(thoughts, DynamicGenerator.generate_fluid("confusion", sentiment, self.mood, self.personas.get(self.current_persona, {})))

    def _style(self, text):
        p = self.personas.get(self.current_persona, self.personas["Standard"])
        prefix = p.get("prefix", "")
        suffix = p.get("suffix", "")
        return f"{prefix}{text}{suffix}"

    def _format_response(self, thoughts, response_text):
        styled_response = self._style(response_text)
        thought_str = " > ".join(thoughts)
        return f"(Thinking: {thought_str})\n\n{styled_response}"

    def _format_response_raw(self, thoughts, response_text):
        # response_text is already styled by DynamicGenerator
        thought_str = " > ".join(thoughts)
        return f"(Thinking: {thought_str})\n\n{response_text}"

    def _style(self, text):
        p = self.personas.get(self.current_persona, self.personas["Standard"])
        prefix = p.get("prefix", "")
        suffix = p.get("suffix", "")
        return f"{prefix}{text}{suffix}"
