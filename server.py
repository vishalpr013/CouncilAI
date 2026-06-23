from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph.builder import graph
import uvicorn

app = FastAPI(title="CouncilAI API", description="FastAPI Backend for CouncilAI Agent Workflow")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    research: str
    analysis: str
    critique: str
    final_answer: str

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    try:
        # Invoke the LangGraph agent
        result = graph.invoke({"question": request.question})
        return QueryResponse(
            question=result.get("question", request.question),
            research=result.get("research", ""),
            analysis=result.get("analysis", ""),
            critique=result.get("critique", ""),
            final_answer=result.get("final_answer", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CouncilAI - Agentic Research Dashboard</title>
    <!-- Outfit Font -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- Tailwind CSS (via CDN) -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Marked JS for markdown parsing -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body {
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, #090d16 0%, #0d1527 50%, #1b0a24 100%);
            min-height: 100vh;
        }
        .glass-panel {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px rgba(255, 255, 255, 0.08) solid;
        }
        .glass-card {
            background: rgba(15, 23, 42, 0.35);
            border: 1px rgba(255, 255, 255, 0.04) solid;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .glass-card:hover {
            background: rgba(15, 23, 42, 0.5);
            border-color: rgba(139, 92, 246, 0.2);
            transform: translateY(-2px);
        }
        .glowing-btn {
            background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
            box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
            transition: all 0.3s ease;
        }
        .glowing-btn:hover {
            box-shadow: 0 0 25px rgba(139, 92, 246, 0.7);
            transform: scale(1.02);
        }
        .glow-text {
            text-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(15, 23, 42, 0.2);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(139, 92, 246, 0.3);
            border-radius: 9999px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(139, 92, 246, 0.5);
        }
        /* Prose customization */
        .prose-custom h3 {
            color: #e2e8f0;
            font-size: 1.125rem;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 0.25rem;
        }
        .prose-custom p {
            color: #94a3b8;
            line-height: 1.625;
            margin-bottom: 0.75rem;
        }
        .prose-custom ul, .prose-custom ol {
            margin-left: 1.25rem;
            margin-bottom: 0.75rem;
            list-style-type: disc;
            color: #94a3b8;
        }
        .prose-custom li {
            margin-bottom: 0.25rem;
        }
        .prose-custom strong {
            color: #f1f5f9;
        }
    </style>
</head>
<body class="text-slate-200 antialiased py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <header class="mb-10 text-center">
            <div class="inline-flex items-center gap-3 px-4 py-1.5 rounded-full glass-panel border border-violet-500/20 text-xs font-semibold text-violet-300 uppercase tracking-wider mb-4 animate-pulse">
                <span class="w-2 h-2 rounded-full bg-violet-400"></span>
                Active Agentic Graph
            </div>
            <h1 class="text-4xl sm:text-5xl font-bold tracking-tight text-white glow-text mb-3">
                Council<span class="text-violet-400">AI</span>
            </h1>
            <p class="text-slate-400 max-w-lg mx-auto text-sm sm:text-base">
                An orchestrating consensus of Researcher, Analyst, Critic, and Reporter agent nodes.
            </p>
        </header>

        <!-- Main Query Section -->
        <main class="space-y-8">
            <div class="glass-panel rounded-3xl p-6 sm:p-8">
                <form id="query-form" class="space-y-4">
                    <label for="question" class="block text-sm font-semibold text-slate-300">Ask the Council</label>
                    <div class="flex flex-col sm:flex-row gap-3">
                        <input 
                            type="text" 
                            id="question" 
                            name="question"
                            required
                            placeholder="Should Nvidia be a long term investment?" 
                            class="flex-1 px-5 py-3.5 rounded-xl bg-slate-950/60 border border-slate-800 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent text-sm sm:text-base transition-all duration-350"
                        >
                        <button 
                            type="submit" 
                            id="submit-btn"
                            class="glowing-btn text-white px-8 py-3.5 rounded-xl font-semibold text-sm sm:text-base flex items-center justify-center gap-2"
                        >
                            <span>Analyze</span>
                            <svg id="btn-icon" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                        </button>
                    </div>
                </form>

                <!-- Processing / Loading state -->
                <div id="loader" class="hidden mt-8 space-y-6">
                    <div class="h-[2px] w-full bg-slate-800 overflow-hidden rounded">
                        <div class="h-full bg-gradient-to-r from-violet-500 to-indigo-500 animate-[loading_1.5s_infinite_linear]" style="width: 30%; animation: loading 1.8s infinite ease-in-out;"></div>
                    </div>
                    <style>
                        @keyframes loading {
                            0% { transform: translateX(-100%); }
                            100% { transform: translateX(300%); }
                        }
                    </style>
                    <div class="flex flex-wrap justify-center items-center gap-4 text-xs font-medium text-slate-400">
                        <div class="flex items-center gap-2" id="step-researcher">
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-700 animate-pulse"></span>
                            Researcher
                        </div>
                        <svg class="w-3 h-3 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7"/></svg>
                        <div class="flex items-center gap-2" id="step-analyst">
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-700"></span>
                            Analyst
                        </div>
                        <svg class="w-3 h-3 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7"/></svg>
                        <div class="flex items-center gap-2" id="step-critic">
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-700"></span>
                            Critic
                        </div>
                        <svg class="w-3 h-3 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7"/></svg>
                        <div class="flex items-center gap-2" id="step-reporter">
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-700"></span>
                            Reporter
                        </div>
                    </div>
                </div>
            </div>

            <!-- Results Section -->
            <div id="results-container" class="hidden space-y-8">
                <!-- Final Answer (Highlighted) -->
                <div class="glass-panel rounded-3xl p-6 sm:p-8 border border-violet-500/20 shadow-2xl relative overflow-hidden">
                    <div class="absolute -right-16 -top-16 w-36 h-36 bg-violet-600/10 rounded-full blur-3xl pointer-events-none"></div>
                    <h2 class="text-lg font-bold text-violet-300 flex items-center gap-2 mb-4 uppercase tracking-wide">
                        <svg class="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                        Executive Report
                    </h2>
                    <div id="final-answer-content" class="prose-custom text-slate-100 text-base sm:text-lg leading-relaxed"></div>
                </div>

                <!-- Tabs for agent details -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- Researcher Card -->
                    <div class="glass-card rounded-2xl p-6 flex flex-col">
                        <h3 class="text-sm font-bold text-slate-400 tracking-wider uppercase mb-3 flex items-center gap-2">
                            <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                            1. Researcher Node
                        </h3>
                        <div id="research-content" class="prose-custom text-xs sm:text-sm overflow-y-auto max-h-[300px] flex-1 pr-1"></div>
                    </div>

                    <!-- Analyst Card -->
                    <div class="glass-card rounded-2xl p-6 flex flex-col">
                        <h3 class="text-sm font-bold text-slate-400 tracking-wider uppercase mb-3 flex items-center gap-2">
                            <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                            2. Analyst Node
                        </h3>
                        <div id="analysis-content" class="prose-custom text-xs sm:text-sm overflow-y-auto max-h-[300px] flex-1 pr-1"></div>
                    </div>

                    <!-- Critic Card -->
                    <div class="glass-card rounded-2xl p-6 flex flex-col">
                        <h3 class="text-sm font-bold text-slate-400 tracking-wider uppercase mb-3 flex items-center gap-2">
                            <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                            3. Critic Node
                        </h3>
                        <div id="critique-content" class="prose-custom text-xs sm:text-sm overflow-y-auto max-h-[300px] flex-1 pr-1"></div>
                    </div>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="mt-16 text-center text-xs text-slate-600">
            CouncilAI Engine &bull; Built with LangGraph & FastAPI
        </footer>
    </div>

    <script>
        const form = document.getElementById('query-form');
        const submitBtn = document.getElementById('submit-btn');
        const loader = document.getElementById('loader');
        const resultsContainer = document.getElementById('results-container');
        
        // Progress steps
        const stepResearcher = document.getElementById('step-researcher');
        const stepAnalyst = document.getElementById('step-analyst');
        const stepCritic = document.getElementById('step-critic');
        const stepReporter = document.getElementById('step-reporter');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const question = document.getElementById('question').value.trim();
            if (!question) return;

            // UI state: loading
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
            loader.classList.remove('hidden');
            resultsContainer.classList.add('hidden');

            // Reset step colors
            resetSteps();
            simulateSteps();

            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                });

                if (!response.ok) {
                    throw new Error('Server responded with an error');
                }

                const data = await response.json();
                
                // Set step active to done
                markAllStepsCompleted();

                // Render Markdown content
                document.getElementById('final-answer-content').innerHTML = marked.parse(data.final_answer || '');
                document.getElementById('research-content').innerHTML = marked.parse(data.research || '');
                document.getElementById('analysis-content').innerHTML = marked.parse(data.analysis || '');
                document.getElementById('critique-content').innerHTML = marked.parse(data.critique || '');

                // Reveal results
                resultsContainer.classList.remove('hidden');
            } catch (error) {
                alert('Error querying the agent: ' + error.message);
            } finally {
                submitBtn.disabled = false;
                submitBtn.classList.remove('opacity-75', 'cursor-not-allowed');
                loader.classList.add('hidden');
            }
        });

        function resetSteps() {
            [stepResearcher, stepAnalyst, stepCritic, stepReporter].forEach(step => {
                const badge = step.querySelector('span');
                badge.className = 'w-2.5 h-2.5 rounded-full bg-slate-700';
                step.className = 'flex items-center gap-2 text-slate-400';
            });
        }

        let simulationInterval;
        function simulateSteps() {
            let current = 0;
            const steps = [
                { el: stepResearcher, color: 'bg-blue-500' },
                { el: stepAnalyst, color: 'bg-amber-500' },
                { el: stepCritic, color: 'bg-rose-500' },
                { el: stepReporter, color: 'bg-violet-500' }
            ];

            if (simulationInterval) clearInterval(simulationInterval);

            // Turn on first step immediately
            activateStep(steps[0].el, steps[0].color);

            simulationInterval = setInterval(() => {
                current++;
                if (current < steps.length) {
                    // Complete previous
                    completeStep(steps[current-1].el);
                    // Activate current
                    activateStep(steps[current].el, steps[current].color);
                } else {
                    clearInterval(simulationInterval);
                }
            }, 6000); // Progress roughly every 6 seconds as a visual placeholder during the request
        }

        function activateStep(el, colorClass) {
            const badge = el.querySelector('span');
            badge.className = `w-2.5 h-2.5 rounded-full ${colorClass} animate-pulse`;
            el.className = 'flex items-center gap-2 text-white font-semibold';
        }

        function completeStep(el) {
            const badge = el.querySelector('span');
            badge.className = 'w-2.5 h-2.5 rounded-full bg-emerald-500';
            el.className = 'flex items-center gap-2 text-emerald-400';
        }

        function markAllStepsCompleted() {
            if (simulationInterval) clearInterval(simulationInterval);
            [stepResearcher, stepAnalyst, stepCritic, stepReporter].forEach(el => {
                completeStep(el);
            });
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTML_CONTENT

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
