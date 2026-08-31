"""
Curated seed dataset for SkillGraph AI.

This is a hand-curated skill graph + resource/project catalog covering four
target roles (per spec section 49): AI Engineer, Data Scientist,
Full Stack Developer, Cybersecurity Analyst. Resource URLs point to real,
stable, general-purpose documentation/learning hubs (not fabricated course
pages) so the "no fabricated URLs" guardrail (spec section 22/31) holds even
though this is a static seed rather than a live catalog API.

Structure:
  SKILLS: key -> {name, category, description}
  SKILL_REQUIRES: list of (from_key, to_key) meaning `from_key REQUIRES to_key`
                   i.e. to_key must be learned before from_key.
  ROLE_SKILLS: role -> ordered list of skill keys that make up that role's
               target skill graph (core capabilities).
  RESOURCES: list of resource dicts, each tagged with skill keys it TEACHES.
  PROJECTS: list of project dicts, each tagged with skill keys it DEMONSTRATES.
  ASSESSMENT_BANK: skill_key -> list of {prompt, options, correct_index, difficulty, concept}
"""

SKILLS: dict[str, dict] = {
    # Programming foundations
    "python": {"name": "Python", "category": "Programming", "description": "Core Python syntax, control flow, functions."},
    "oop": {"name": "Object-Oriented Programming", "category": "Programming", "description": "Classes, objects, inheritance, composition."},
    "data_structures": {"name": "Data Structures & Algorithms", "category": "Programming", "description": "Lists, trees, graphs, complexity analysis."},
    "git": {"name": "Git & Version Control", "category": "Programming", "description": "Branching, commits, collaboration workflows."},
    "javascript": {"name": "JavaScript", "category": "Programming", "description": "Core JS, async, DOM."},
    "typescript": {"name": "TypeScript", "category": "Programming", "description": "Static typing on top of JavaScript."},

    # Data
    "sql": {"name": "SQL", "category": "Data", "description": "Relational queries, joins, aggregation."},
    "numpy_pandas": {"name": "NumPy & Pandas", "category": "Data", "description": "Numerical computing and dataframes."},
    "data_viz": {"name": "Data Visualization", "category": "Data", "description": "Communicating data with plots and dashboards."},
    "data_cleaning": {"name": "Data Cleaning & Wrangling", "category": "Data", "description": "Handling missing data, outliers, transforms."},

    # Math
    "statistics": {"name": "Statistics", "category": "Mathematics", "description": "Distributions, hypothesis testing, inference."},
    "probability": {"name": "Probability", "category": "Mathematics", "description": "Random variables, Bayes theorem."},
    "linear_algebra": {"name": "Linear Algebra", "category": "Mathematics", "description": "Vectors, matrices, eigenvalues."},

    # ML
    "ml_regression": {"name": "Regression", "category": "Machine Learning", "description": "Linear/logistic regression."},
    "ml_classification": {"name": "Classification", "category": "Machine Learning", "description": "Decision trees, ensembles, SVMs."},
    "ml_clustering": {"name": "Clustering", "category": "Machine Learning", "description": "K-means, hierarchical clustering."},
    "model_evaluation": {"name": "Model Evaluation", "category": "Machine Learning", "description": "Cross-validation, metrics, overfitting."},
    "feature_engineering": {"name": "Feature Engineering", "category": "Machine Learning", "description": "Building predictive features from raw data."},

    # Deep learning / GenAI
    "neural_networks": {"name": "Neural Networks", "category": "Deep Learning", "description": "Perceptrons, backprop, optimizers."},
    "cnn": {"name": "CNNs", "category": "Deep Learning", "description": "Convolutional networks for vision."},
    "rnn": {"name": "RNNs / Sequence Models", "category": "Deep Learning", "description": "Recurrent models for sequences."},
    "transformers": {"name": "Transformers", "category": "Deep Learning", "description": "Attention mechanism, transformer architecture."},
    "embeddings": {"name": "Embeddings", "category": "Generative AI", "description": "Vector representations of meaning."},
    "vector_databases": {"name": "Vector Databases", "category": "Generative AI", "description": "Storing and searching embeddings at scale."},
    "prompt_engineering": {"name": "Prompt Engineering", "category": "Generative AI", "description": "Designing effective LLM prompts."},
    "llm_apis": {"name": "LLM APIs", "category": "Generative AI", "description": "Calling and orchestrating LLM providers."},
    "rag": {"name": "Retrieval-Augmented Generation", "category": "Generative AI", "description": "Grounding LLMs with retrieved context."},

    # Production / MLOps
    "apis": {"name": "Building APIs", "category": "Production AI", "description": "REST API design and implementation."},
    "docker": {"name": "Docker", "category": "Production AI", "description": "Containerization fundamentals."},
    "cloud": {"name": "Cloud Fundamentals", "category": "Production AI", "description": "Core cloud compute/storage concepts."},
    "monitoring": {"name": "Monitoring & Observability", "category": "Production AI", "description": "Logging, metrics, alerting."},
    "mlops": {"name": "MLOps", "category": "Production AI", "description": "CI/CD for ML, model versioning, deployment."},

    # Full stack
    "html_css": {"name": "HTML & CSS", "category": "Frontend", "description": "Markup and styling fundamentals."},
    "react": {"name": "React", "category": "Frontend", "description": "Component-based UI development."},
    "rest_apis": {"name": "REST API Design", "category": "Backend", "description": "Resource modeling, status codes, auth."},
    "nodejs": {"name": "Node.js", "category": "Backend", "description": "Server-side JavaScript runtime."},
    "databases": {"name": "Database Design", "category": "Backend", "description": "Schema design, normalization, indexing."},
    "system_design": {"name": "System Design", "category": "Backend", "description": "Scalability, caching, distributed systems basics."},
    "testing": {"name": "Automated Testing", "category": "Software Engineering", "description": "Unit, integration, and e2e testing."},

    # Cybersecurity
    "networking_fundamentals": {"name": "Networking Fundamentals", "category": "Security", "description": "TCP/IP, DNS, routing basics."},
    "os_fundamentals": {"name": "OS Fundamentals", "category": "Security", "description": "Linux/Windows internals for security work."},
    "security_fundamentals": {"name": "Security Fundamentals", "category": "Security", "description": "CIA triad, threat landscape, risk basics."},
    "cryptography": {"name": "Cryptography Basics", "category": "Security", "description": "Symmetric/asymmetric encryption, hashing."},
    "network_security": {"name": "Network Security", "category": "Security", "description": "Firewalls, IDS/IPS, segmentation."},
    "threat_modeling": {"name": "Threat Modeling", "category": "Security", "description": "Identifying and prioritizing attack surfaces."},
    "vulnerability_assessment": {"name": "Vulnerability Assessment", "category": "Security", "description": "Scanning and assessing weaknesses."},
    "incident_response": {"name": "Incident Response", "category": "Security", "description": "Detecting, containing, and recovering from incidents."},
    "siem_tools": {"name": "SIEM & Log Analysis", "category": "Security", "description": "Correlating logs to detect threats."},
    "pen_testing": {"name": "Penetration Testing Basics", "category": "Security", "description": "Ethical hacking methodology."},
}

# (from_key REQUIRES to_key) -> to_key must come first
SKILL_REQUIRES: list[tuple[str, str]] = [
    ("oop", "python"),
    ("data_structures", "python"),
    ("numpy_pandas", "python"),
    ("sql", "python"),
    ("data_cleaning", "numpy_pandas"),
    ("data_viz", "numpy_pandas"),
    ("statistics", "probability"),
    ("ml_regression", "statistics"),
    ("ml_regression", "numpy_pandas"),
    ("ml_classification", "ml_regression"),
    ("ml_clustering", "ml_classification"),
    ("model_evaluation", "ml_classification"),
    ("feature_engineering", "model_evaluation"),
    ("neural_networks", "linear_algebra"),
    ("neural_networks", "model_evaluation"),
    ("cnn", "neural_networks"),
    ("rnn", "neural_networks"),
    ("transformers", "rnn"),
    ("embeddings", "transformers"),
    ("vector_databases", "embeddings"),
    ("prompt_engineering", "llm_apis"),
    ("llm_apis", "apis"),
    ("rag", "vector_databases"),
    ("rag", "prompt_engineering"),
    ("docker", "apis"),
    ("mlops", "docker"),
    ("mlops", "cloud"),
    ("monitoring", "docker"),
    ("apis", "python"),
    ("data_structures", "oop"),
    # Full stack
    ("react", "javascript"),
    ("javascript", "html_css"),
    ("typescript", "javascript"),
    ("nodejs", "javascript"),
    ("rest_apis", "nodejs"),
    ("databases", "sql"),
    ("system_design", "databases"),
    ("system_design", "rest_apis"),
    ("testing", "javascript"),
    # Security
    ("os_fundamentals", "networking_fundamentals"),
    ("security_fundamentals", "networking_fundamentals"),
    ("cryptography", "security_fundamentals"),
    ("network_security", "networking_fundamentals"),
    ("network_security", "security_fundamentals"),
    ("threat_modeling", "security_fundamentals"),
    ("vulnerability_assessment", "threat_modeling"),
    ("siem_tools", "network_security"),
    ("incident_response", "siem_tools"),
    ("pen_testing", "vulnerability_assessment"),
    ("pen_testing", "cryptography"),
]

ROLE_SKILLS: dict[str, list[str]] = {
    "AI Engineer": [
        "python", "oop", "data_structures", "sql", "numpy_pandas",
        "probability", "statistics", "linear_algebra",
        "ml_regression", "ml_classification", "model_evaluation",
        "neural_networks", "rnn", "transformers",
        "embeddings", "vector_databases", "prompt_engineering", "llm_apis", "rag",
        "apis", "docker", "cloud", "monitoring", "mlops",
    ],
    "Data Scientist": [
        "python", "sql", "numpy_pandas", "data_cleaning", "data_viz",
        "probability", "statistics", "linear_algebra",
        "ml_regression", "ml_classification", "ml_clustering",
        "model_evaluation", "feature_engineering", "neural_networks",
    ],
    "Full Stack Developer": [
        "html_css", "javascript", "typescript", "react",
        "git", "nodejs", "rest_apis", "sql", "databases",
        "testing", "system_design", "docker", "cloud",
    ],
    "Cybersecurity Analyst": [
        "networking_fundamentals", "os_fundamentals", "security_fundamentals",
        "cryptography", "network_security", "threat_modeling",
        "vulnerability_assessment", "siem_tools", "incident_response", "pen_testing",
    ],
}

# resource_type in {course,video,article,doc,book,exercise}
RESOURCES: list[dict] = [
    {"title": "Python Official Tutorial", "provider": "python.org", "url": "https://docs.python.org/3/tutorial/", "type": "doc", "difficulty": "beginner", "minutes": 240, "skills": ["python"], "quality": 0.9},
    {"title": "Automate the Boring Stuff with Python", "provider": "automatetheboringstuff.com", "url": "https://automatetheboringstuff.com/", "type": "book", "difficulty": "beginner", "minutes": 600, "skills": ["python", "oop"], "quality": 0.85},
    {"title": "Python Data Structures & Algorithms Guide", "provider": "MDN/Community", "url": "https://runestone.academy/ns/books/published/pythonds/index.html", "type": "book", "difficulty": "intermediate", "minutes": 480, "skills": ["data_structures", "oop"], "quality": 0.8},
    {"title": "SQL Tutorial", "provider": "Mode Analytics", "url": "https://mode.com/sql-tutorial/", "type": "course", "difficulty": "beginner", "minutes": 300, "skills": ["sql"], "quality": 0.85, "has_project": True},
    {"title": "NumPy Quickstart", "provider": "numpy.org", "url": "https://numpy.org/doc/stable/user/quickstart.html", "type": "doc", "difficulty": "beginner", "minutes": 120, "skills": ["numpy_pandas"], "quality": 0.85},
    {"title": "Pandas User Guide", "provider": "pandas.pydata.org", "url": "https://pandas.pydata.org/docs/user_guide/index.html", "type": "doc", "difficulty": "beginner", "minutes": 240, "skills": ["numpy_pandas", "data_cleaning"], "quality": 0.85},
    {"title": "Data Visualization with Matplotlib/Seaborn", "provider": "Seaborn Docs", "url": "https://seaborn.pydata.org/tutorial.html", "type": "doc", "difficulty": "beginner", "minutes": 180, "skills": ["data_viz"], "quality": 0.8},
    {"title": "Think Stats (Probability & Statistics for Programmers)", "provider": "Green Tea Press", "url": "https://greenteapress.com/wp/think-stats-2e/", "type": "book", "difficulty": "beginner", "minutes": 420, "skills": ["probability", "statistics"], "quality": 0.85},
    {"title": "Essence of Linear Algebra", "provider": "3Blue1Brown", "url": "https://www.3blue1brown.com/topics/linear-algebra", "type": "video", "difficulty": "beginner", "minutes": 180, "skills": ["linear_algebra"], "quality": 0.95},
    {"title": "scikit-learn: Linear Models", "provider": "scikit-learn.org", "url": "https://scikit-learn.org/stable/modules/linear_model.html", "type": "doc", "difficulty": "intermediate", "minutes": 150, "skills": ["ml_regression"], "quality": 0.85},
    {"title": "scikit-learn: Classification & Ensembles", "provider": "scikit-learn.org", "url": "https://scikit-learn.org/stable/supervised_learning.html", "type": "doc", "difficulty": "intermediate", "minutes": 200, "skills": ["ml_classification"], "quality": 0.85},
    {"title": "scikit-learn: Clustering", "provider": "scikit-learn.org", "url": "https://scikit-learn.org/stable/modules/clustering.html", "type": "doc", "difficulty": "intermediate", "minutes": 150, "skills": ["ml_clustering"], "quality": 0.8},
    {"title": "Model Evaluation & Cross-Validation Guide", "provider": "scikit-learn.org", "url": "https://scikit-learn.org/stable/modules/cross_validation.html", "type": "doc", "difficulty": "intermediate", "minutes": 150, "skills": ["model_evaluation"], "quality": 0.85},
    {"title": "Feature Engineering for Machine Learning", "provider": "Kaggle Learn", "url": "https://www.kaggle.com/learn/feature-engineering", "type": "course", "difficulty": "intermediate", "minutes": 240, "skills": ["feature_engineering"], "quality": 0.85, "has_project": True},
    {"title": "Neural Networks and Deep Learning", "provider": "neuralnetworksanddeeplearning.com", "url": "http://neuralnetworksanddeeplearning.com/", "type": "book", "difficulty": "intermediate", "minutes": 420, "skills": ["neural_networks"], "quality": 0.9},
    {"title": "CS231n Convolutional Neural Networks", "provider": "Stanford CS231n", "url": "https://cs231n.github.io/", "type": "course", "difficulty": "advanced", "minutes": 600, "skills": ["cnn"], "quality": 0.9},
    {"title": "Understanding RNNs and LSTMs", "provider": "colah's blog", "url": "https://colah.github.io/posts/2015-08-Understanding-LSTMs/", "type": "article", "difficulty": "intermediate", "minutes": 90, "skills": ["rnn"], "quality": 0.9},
    {"title": "The Illustrated Transformer", "provider": "Jay Alammar", "url": "https://jalammar.github.io/illustrated-transformer/", "type": "article", "difficulty": "intermediate", "minutes": 90, "skills": ["transformers"], "quality": 0.95},
    {"title": "Hugging Face NLP Course", "provider": "Hugging Face", "url": "https://huggingface.co/learn/nlp-course", "type": "course", "difficulty": "intermediate", "minutes": 600, "skills": ["transformers", "embeddings"], "quality": 0.9, "has_project": True},
    {"title": "OpenAI/Anthropic Embeddings Guide", "provider": "Provider docs", "url": "https://platform.openai.com/docs/guides/embeddings", "type": "doc", "difficulty": "intermediate", "minutes": 90, "skills": ["embeddings"], "quality": 0.85},
    {"title": "Vector Databases Explained (Pinecone Learning Center)", "provider": "Pinecone", "url": "https://www.pinecone.io/learn/vector-database/", "type": "article", "difficulty": "intermediate", "minutes": 90, "skills": ["vector_databases"], "quality": 0.85},
    {"title": "Prompt Engineering Guide", "provider": "promptingguide.ai", "url": "https://www.promptingguide.ai/", "type": "doc", "difficulty": "beginner", "minutes": 150, "skills": ["prompt_engineering"], "quality": 0.9},
    {"title": "Anthropic API Documentation", "provider": "Anthropic", "url": "https://docs.claude.com", "type": "doc", "difficulty": "beginner", "minutes": 120, "skills": ["llm_apis"], "quality": 0.9},
    {"title": "Building RAG Applications", "provider": "LangChain Docs", "url": "https://python.langchain.com/docs/tutorials/rag/", "type": "course", "difficulty": "intermediate", "minutes": 240, "skills": ["rag"], "quality": 0.85, "has_project": True},
    {"title": "FastAPI Official Tutorial", "provider": "fastapi.tiangolo.com", "url": "https://fastapi.tiangolo.com/tutorial/", "type": "doc", "difficulty": "beginner", "minutes": 240, "skills": ["apis"], "quality": 0.9},
    {"title": "Docker Getting Started", "provider": "docker.com", "url": "https://docs.docker.com/get-started/", "type": "doc", "difficulty": "beginner", "minutes": 180, "skills": ["docker"], "quality": 0.85},
    {"title": "Cloud Computing Fundamentals", "provider": "AWS Skill Builder", "url": "https://skillbuilder.aws/", "type": "course", "difficulty": "beginner", "minutes": 300, "skills": ["cloud"], "quality": 0.8},
    {"title": "Observability & Monitoring Basics", "provider": "Prometheus Docs", "url": "https://prometheus.io/docs/introduction/overview/", "type": "doc", "difficulty": "intermediate", "minutes": 120, "skills": ["monitoring"], "quality": 0.8},
    {"title": "MLOps Principles", "provider": "Google Cloud", "url": "https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning", "type": "article", "difficulty": "advanced", "minutes": 150, "skills": ["mlops"], "quality": 0.85},
    # Full stack
    {"title": "MDN HTML & CSS Guide", "provider": "MDN", "url": "https://developer.mozilla.org/en-US/docs/Learn/HTML", "type": "doc", "difficulty": "beginner", "minutes": 300, "skills": ["html_css"], "quality": 0.9},
    {"title": "JavaScript.info", "provider": "javascript.info", "url": "https://javascript.info/", "type": "book", "difficulty": "beginner", "minutes": 480, "skills": ["javascript"], "quality": 0.9},
    {"title": "TypeScript Handbook", "provider": "typescriptlang.org", "url": "https://www.typescriptlang.org/docs/handbook/intro.html", "type": "doc", "difficulty": "intermediate", "minutes": 180, "skills": ["typescript"], "quality": 0.9},
    {"title": "React Official Docs", "provider": "react.dev", "url": "https://react.dev/learn", "type": "doc", "difficulty": "intermediate", "minutes": 300, "skills": ["react"], "quality": 0.95, "has_project": True},
    {"title": "Pro Git Book", "provider": "git-scm.com", "url": "https://git-scm.com/book/en/v2", "type": "book", "difficulty": "beginner", "minutes": 180, "skills": ["git"], "quality": 0.9},
    {"title": "Node.js Guides", "provider": "nodejs.org", "url": "https://nodejs.org/en/docs/guides", "type": "doc", "difficulty": "intermediate", "minutes": 240, "skills": ["nodejs"], "quality": 0.85},
    {"title": "REST API Design Best Practices", "provider": "Microsoft REST Guidelines", "url": "https://github.com/microsoft/api-guidelines", "type": "doc", "difficulty": "intermediate", "minutes": 150, "skills": ["rest_apis"], "quality": 0.8},
    {"title": "Database Design Fundamentals", "provider": "PostgreSQL Docs", "url": "https://www.postgresql.org/docs/current/tutorial.html", "type": "doc", "difficulty": "intermediate", "minutes": 240, "skills": ["databases"], "quality": 0.85},
    {"title": "Testing JavaScript Applications", "provider": "Jest Docs", "url": "https://jestjs.io/docs/getting-started", "type": "doc", "difficulty": "intermediate", "minutes": 150, "skills": ["testing"], "quality": 0.85},
    {"title": "System Design Primer", "provider": "GitHub (donnemartin)", "url": "https://github.com/donnemartin/system-design-primer", "type": "doc", "difficulty": "advanced", "minutes": 420, "skills": ["system_design"], "quality": 0.9},
    # Security
    {"title": "Networking Fundamentals (Cisco NetAcad)", "provider": "Cisco", "url": "https://www.netacad.com/courses/networking", "type": "course", "difficulty": "beginner", "minutes": 300, "skills": ["networking_fundamentals"], "quality": 0.85},
    {"title": "Linux Journey", "provider": "linuxjourney.com", "url": "https://linuxjourney.com/", "type": "course", "difficulty": "beginner", "minutes": 300, "skills": ["os_fundamentals"], "quality": 0.85},
    {"title": "NIST Cybersecurity Framework", "provider": "NIST", "url": "https://www.nist.gov/cyberframework", "type": "doc", "difficulty": "beginner", "minutes": 180, "skills": ["security_fundamentals"], "quality": 0.85},
    {"title": "Cryptography I", "provider": "Coursera (Stanford)", "url": "https://www.coursera.org/learn/crypto", "type": "course", "difficulty": "intermediate", "minutes": 600, "skills": ["cryptography"], "quality": 0.9},
    {"title": "Network Security Essentials", "provider": "Cybrary", "url": "https://www.cybrary.it/", "type": "course", "difficulty": "intermediate", "minutes": 300, "skills": ["network_security"], "quality": 0.8},
    {"title": "Threat Modeling: Designing for Security", "provider": "OWASP", "url": "https://owasp.org/www-community/Threat_Modeling", "type": "doc", "difficulty": "intermediate", "minutes": 150, "skills": ["threat_modeling"], "quality": 0.85},
    {"title": "OWASP Top 10", "provider": "OWASP", "url": "https://owasp.org/www-project-top-ten/", "type": "doc", "difficulty": "intermediate", "minutes": 150, "skills": ["vulnerability_assessment"], "quality": 0.9, "has_project": True},
    {"title": "SIEM & Log Analysis Basics", "provider": "Splunk Education", "url": "https://www.splunk.com/en_us/training.html", "type": "course", "difficulty": "intermediate", "minutes": 240, "skills": ["siem_tools"], "quality": 0.8},
    {"title": "Incident Response Guide (SANS)", "provider": "SANS", "url": "https://www.sans.org/incident-response/", "type": "doc", "difficulty": "advanced", "minutes": 240, "skills": ["incident_response"], "quality": 0.85},
    {"title": "Penetration Testing Execution Standard", "provider": "PTES", "url": "http://www.pentest-standard.org/", "type": "doc", "difficulty": "advanced", "minutes": 240, "skills": ["pen_testing"], "quality": 0.8},
]

PROJECTS: list[dict] = [
    {"title": "Expense Tracker CLI", "description": "A command-line expense tracker with persistent storage.", "difficulty": "beginner", "hours": 4, "portfolio_value": "low", "skills": ["python", "oop"]},
    {"title": "Data Analysis Dashboard", "description": "Clean a real dataset and build an interactive dashboard of insights.", "difficulty": "beginner", "hours": 8, "portfolio_value": "medium", "skills": ["numpy_pandas", "data_viz", "sql", "data_cleaning"]},
    {"title": "Customer Churn Predictor", "description": "Train and evaluate a classification model predicting customer churn.", "difficulty": "intermediate", "hours": 10, "portfolio_value": "high", "skills": ["ml_classification", "model_evaluation", "feature_engineering"]},
    {"title": "House Price Regression Model", "description": "Build and tune a regression model on housing data.", "difficulty": "beginner", "hours": 6, "portfolio_value": "medium", "skills": ["ml_regression"]},
    {"title": "Customer Segmentation Explorer", "description": "Cluster customers into segments and visualize them.", "difficulty": "intermediate", "hours": 6, "portfolio_value": "medium", "skills": ["ml_clustering", "data_viz"]},
    {"title": "Image Classifier", "description": "Train a CNN to classify images into categories, with a simple web demo.", "difficulty": "intermediate", "hours": 12, "portfolio_value": "high", "skills": ["cnn", "neural_networks"]},
    {"title": "Text Sentiment Classifier", "description": "Build a sequence model to classify text sentiment.", "difficulty": "intermediate", "hours": 8, "portfolio_value": "medium", "skills": ["rnn", "transformers"]},
    {"title": "RAG Document Assistant", "description": "Build a retrieval-augmented Q&A assistant over a document set.", "difficulty": "advanced", "hours": 14, "portfolio_value": "high", "skills": ["embeddings", "vector_databases", "rag", "prompt_engineering", "llm_apis"]},
    {"title": "Deploy ML API", "description": "Containerize and deploy a trained model behind a REST API with monitoring.", "difficulty": "advanced", "hours": 10, "portfolio_value": "high", "skills": ["apis", "docker", "mlops", "monitoring", "cloud"]},
    {"title": "Production AI Learning Assistant (Capstone)", "description": "Combine RAG, APIs, and deployment into a full assistant product, mirroring SkillGraph AI's own architecture.", "difficulty": "advanced", "hours": 20, "portfolio_value": "high", "skills": ["rag", "apis", "docker", "mlops", "llm_apis"]},
    # Full stack
    {"title": "Personal Portfolio Site", "description": "A responsive personal site built with semantic HTML/CSS.", "difficulty": "beginner", "hours": 5, "portfolio_value": "low", "skills": ["html_css"]},
    {"title": "Task Manager (React + REST API)", "description": "Full CRUD task manager with a React frontend and a REST backend.", "difficulty": "intermediate", "hours": 14, "portfolio_value": "high", "skills": ["react", "rest_apis", "nodejs", "databases"]},
    {"title": "E-commerce Product Catalog", "description": "A searchable, paginated product catalog with a normalized database schema.", "difficulty": "intermediate", "hours": 12, "portfolio_value": "high", "skills": ["databases", "system_design", "rest_apis"]},
    {"title": "CI Test Suite", "description": "Add a full automated test suite and CI pipeline to an existing app.", "difficulty": "intermediate", "hours": 6, "portfolio_value": "medium", "skills": ["testing", "git"]},
    # Security
    {"title": "Home Lab Network Segmentation", "description": "Design and document a segmented home lab network with firewall rules.", "difficulty": "beginner", "hours": 6, "portfolio_value": "medium", "skills": ["networking_fundamentals", "network_security"]},
    {"title": "Vulnerability Scan Report", "description": "Run and interpret a vulnerability scan against a lab environment, producing a remediation report.", "difficulty": "intermediate", "hours": 8, "portfolio_value": "high", "skills": ["vulnerability_assessment", "threat_modeling"]},
    {"title": "SIEM Detection Rules", "description": "Write and test log-correlation detection rules for common attack patterns.", "difficulty": "advanced", "hours": 10, "portfolio_value": "high", "skills": ["siem_tools", "incident_response"]},
    {"title": "Capture-the-Flag Writeup", "description": "Complete a beginner CTF and document your methodology.", "difficulty": "intermediate", "hours": 8, "portfolio_value": "high", "skills": ["pen_testing", "vulnerability_assessment"]},
]

# A small hand-written question bank per skill (used directly; skills without
# an explicit bank get generic templated questions — see assessment.py).
ASSESSMENT_BANK: dict[str, list[dict]] = {
    "python": [
        {"prompt": "What does `len([1, 2, 3])` return?", "options": ["2", "3", "None", "Error"], "correct_index": 1, "difficulty": "easy", "concept": "builtins"},
        {"prompt": "Which keyword defines a function in Python?", "options": ["func", "def", "function", "lambda only"], "correct_index": 1, "difficulty": "easy", "concept": "syntax"},
        {"prompt": "What is the output of `type([])`?", "options": ["list", "tuple", "dict", "array"], "correct_index": 0, "difficulty": "easy", "concept": "types"},
        {"prompt": "What does a Python generator use to yield values lazily?", "options": ["return", "yield", "break", "pass"], "correct_index": 1, "difficulty": "medium", "concept": "generators"},
        {"prompt": "What is the time complexity of dict lookup on average?", "options": ["O(n)", "O(log n)", "O(1)", "O(n^2)"], "correct_index": 2, "difficulty": "hard", "concept": "complexity"},
    ],
    "statistics": [
        {"prompt": "The mean of [2, 4, 6] is:", "options": ["3", "4", "6", "12"], "correct_index": 1, "difficulty": "easy", "concept": "mean"},
        {"prompt": "A p-value below the significance threshold suggests:", "options": ["Accept null hypothesis", "Reject null hypothesis", "No conclusion possible", "Data is invalid"], "correct_index": 1, "difficulty": "medium", "concept": "hypothesis_testing"},
        {"prompt": "Standard deviation measures:", "options": ["Central tendency", "Spread of data", "Correlation", "Sample size"], "correct_index": 1, "difficulty": "easy", "concept": "dispersion"},
        {"prompt": "Which distribution is defined by mean and variance and is symmetric/bell-shaped?", "options": ["Poisson", "Normal", "Bernoulli", "Uniform"], "correct_index": 1, "difficulty": "medium", "concept": "distributions"},
        {"prompt": "What does a confidence interval express?", "options": ["Exact population parameter", "A plausible range for a parameter", "The sample size needed", "The p-value"], "correct_index": 1, "difficulty": "hard", "concept": "confidence_intervals"},
    ],
    "ml_classification": [
        {"prompt": "Which metric is most appropriate for highly imbalanced classes?", "options": ["Accuracy", "F1 score", "R-squared", "MSE"], "correct_index": 1, "difficulty": "medium", "concept": "metrics"},
        {"prompt": "A decision tree that perfectly fits training data but performs poorly on test data is:", "options": ["Underfit", "Overfit", "Well-generalized", "Regularized"], "correct_index": 1, "difficulty": "easy", "concept": "overfitting"},
        {"prompt": "Random Forest is an example of:", "options": ["Boosting", "Bagging/ensemble", "Clustering", "Dimensionality reduction"], "correct_index": 1, "difficulty": "medium", "concept": "ensembles"},
        {"prompt": "What does an ROC curve plot?", "options": ["Precision vs Recall", "True Positive Rate vs False Positive Rate", "Loss vs Epoch", "Bias vs Variance"], "correct_index": 1, "difficulty": "hard", "concept": "evaluation"},
    ],
    "embeddings": [
        {"prompt": "An embedding represents data as:", "options": ["A SQL table", "A dense numeric vector", "A boolean flag", "A file path"], "correct_index": 1, "difficulty": "easy", "concept": "definition"},
        {"prompt": "Cosine similarity measures:", "options": ["The angle between two vectors", "The sum of two vectors", "Vector length only", "Matrix rank"], "correct_index": 0, "difficulty": "medium", "concept": "similarity"},
        {"prompt": "Semantically similar text should produce embeddings that are:", "options": ["Orthogonal", "Close together in vector space", "Identical in every dimension", "Random"], "correct_index": 1, "difficulty": "medium", "concept": "semantics"},
    ],
    "rag": [
        {"prompt": "RAG primarily helps LLMs by:", "options": ["Increasing model parameter count", "Grounding responses in retrieved external context", "Removing the need for prompts", "Training a new base model"], "correct_index": 1, "difficulty": "easy", "concept": "definition"},
        {"prompt": "In a RAG pipeline, retrieval typically happens:", "options": ["After generation", "Before generation, to build context", "Only during fine-tuning", "Never — it's optional"], "correct_index": 1, "difficulty": "medium", "concept": "pipeline"},
        {"prompt": "A common failure mode in RAG is:", "options": ["Retrieving irrelevant chunks that mislead the model", "The model being too fast", "Vector databases being too accurate", "Embeddings being deterministic"], "correct_index": 0, "difficulty": "hard", "concept": "failure_modes"},
    ],
    "sql": [
        {"prompt": "Which clause filters rows before aggregation?", "options": ["HAVING", "WHERE", "GROUP BY", "ORDER BY"], "correct_index": 1, "difficulty": "easy", "concept": "filtering"},
        {"prompt": "An INNER JOIN returns:", "options": ["All rows from both tables", "Only matching rows in both tables", "Only unmatched rows", "A single row"], "correct_index": 1, "difficulty": "medium", "concept": "joins"},
        {"prompt": "Which clause filters groups after aggregation?", "options": ["WHERE", "HAVING", "LIMIT", "DISTINCT"], "correct_index": 1, "difficulty": "hard", "concept": "aggregation"},
    ],
    "networking_fundamentals": [
        {"prompt": "Which layer of the OSI model handles routing?", "options": ["Physical", "Network", "Session", "Presentation"], "correct_index": 1, "difficulty": "easy", "concept": "osi"},
        {"prompt": "DNS primarily translates:", "options": ["IP addresses to MAC addresses", "Domain names to IP addresses", "Ports to protocols", "Packets to frames"], "correct_index": 1, "difficulty": "easy", "concept": "dns"},
        {"prompt": "TCP differs from UDP mainly by:", "options": ["TCP is connectionless", "TCP guarantees ordered, reliable delivery", "UDP is always faster and reliable", "They are identical"], "correct_index": 1, "difficulty": "medium", "concept": "protocols"},
    ],
    "threat_modeling": [
        {"prompt": "STRIDE is a framework used for:", "options": ["Load balancing", "Categorizing security threats", "Database indexing", "UI design"], "correct_index": 1, "difficulty": "medium", "concept": "frameworks"},
        {"prompt": "An 'attack surface' refers to:", "options": ["The total set of points an attacker could exploit", "A physical server room", "A firewall rule", "A password policy"], "correct_index": 0, "difficulty": "easy", "concept": "definitions"},
    ],
    "react": [
        {"prompt": "In React, state updates should generally be treated as:", "options": ["Mutable and updated directly", "Immutable, replaced via setState/useState", "Irrelevant to rendering", "Stored only in the DOM"], "correct_index": 1, "difficulty": "medium", "concept": "state"},
        {"prompt": "What hook manages local component state in function components?", "options": ["useEffect", "useState", "useMemo", "useContext"], "correct_index": 1, "difficulty": "easy", "concept": "hooks"},
    ],
}
