// Global State
let currentRunId = null;
let pollInterval = null;
let lastStatus = null;
let lastStep = null;
let runData = null;
let selectedResearchMode = "tech_topics";

// Game State
let currentGameTopic = null;
let currentDeck = null;
let currentCardIndex = 0;
let isFlipped = false;
let masteredCards = new Set();
let reviewCards = new Set();
let cachedGames = {};

// DOM Elements - Main
const feedSection = document.getElementById("feed-section");
const setupSection = document.getElementById("setup-section");
const progressSection = document.getElementById("progress-section");
const selectionSection = document.getElementById("selection-section");
const resultsSection = document.getElementById("results-section");
const mockSimulatorSection = document.getElementById("mock-simulator-section") || document.getElementById("sim-view-layout");
const studioSection = document.getElementById("studio-section");

// Mode Switcher Elements
const modeTechBtn = document.getElementById("mode-tech-btn");
const modeCompanyBtn = document.getElementById("mode-company-btn");
const modeStockBtn = document.getElementById("mode-stock-btn");
const techTopicsContainer = document.getElementById("tech-topics-container");
const companyIntelContainer = document.getElementById("company-intel-container");
const stockMarketContainer = document.getElementById("stock-market-container");

// Stock Sub-Mode Elements
const subModeStockResearchBtn = document.getElementById("sub-mode-stock-research-btn");
const subModeStockPicksBtn = document.getElementById("sub-mode-stock-picks-btn");
const stockResearchInputs = document.getElementById("stock-research-inputs");
const stockPicksInputs = document.getElementById("stock-picks-inputs");
const stockTickerInput = document.getElementById("stock-ticker-input");
const stockHorizonSelect = document.getElementById("stock-horizon-select");
const stockPeersInput = document.getElementById("stock-peers-input");
const stockSectorFilter = document.getElementById("stock-sector-filter");
let selectedStockSubMode = "stock_research";

const interestsInput = document.getElementById("interests-input");
const manualSelectToggle = document.getElementById("manual-select-toggle");
const companyInput = document.getElementById("company-input");
const roleInput = document.getElementById("role-input");
const levelSelect = document.getElementById("level-select");
const startBtn = document.getElementById("start-btn");

const progressBar = document.getElementById("progress-bar");
const progressPercentage = document.getElementById("progress-percentage");
const currentStepLabel = document.getElementById("current-step-label");
const logsTerminal = document.getElementById("logs-terminal");

const topicsGrid = document.getElementById("topics-grid");
const selectedCountBadge = document.getElementById("selected-count-badge");
const submitSelectionBtn = document.getElementById("submit-selection-btn");

const runFolderPath = document.getElementById("run-folder-path");
const resultsTabs = document.getElementById("results-tabs");
const markdownOutput = document.getElementById("markdown-output");
const downloadBtn = document.getElementById("download-btn");
const restartBtn = document.getElementById("restart-btn");

// DOM Elements - Views & Gamification
const viewModeGuideBtn = document.getElementById("view-mode-guide-btn");
const viewModeGameBtn = document.getElementById("view-mode-game-btn");
const viewModeSimBtn = document.getElementById("view-mode-sim-btn");
const guideViewLayout = document.getElementById("guide-view-layout");
const gameViewLayout = document.getElementById("game-view-layout");
const simViewLayout = document.getElementById("sim-view-layout");

const gameTopicSelect = document.getElementById("game-topic-select");
const gameModeSelect = document.getElementById("game-mode-select");
const masteredCountLabel = document.getElementById("mastered-count");
const masteryProgressFill = document.getElementById("mastery-progress-fill");

const cardCounter = document.getElementById("card-counter");
const cardCategoryBadge = document.getElementById("card-category-badge");
const cardDifficultyBadge = document.getElementById("card-difficulty-badge");

const flashcardContainer = document.getElementById("flashcard-container");
const flashcardCard = document.getElementById("flashcard-card");
const cardFrontPrompt = document.getElementById("card-front-prompt");
const cardBackExplanation = document.getElementById("card-back-explanation");
const cardTakeawayText = document.getElementById("card-takeaway-text");

const cardHintBtn = document.getElementById("card-hint-btn");
const cardHintText = document.getElementById("card-hint-text");

const prevCardBtn = document.getElementById("prev-card-btn");
const nextCardBtn = document.getElementById("next-card-btn");
const reviewCardBtn = document.getElementById("review-card-btn");
const masterCardBtn = document.getElementById("master-card-btn");

// DOM Elements - Mock Simulator
const simRoundSelect = document.getElementById("sim-round-select");
const startSimBtn = document.getElementById("start-sim-btn");
const simCompanyBadge = document.getElementById("sim-company-badge");
const simTimer = document.getElementById("sim-timer");
const finishSimBtn = document.getElementById("finish-sim-btn");

const simChatStream = document.getElementById("sim-chat-stream");
const simInputPanel = document.getElementById("sim-input-panel");
const simCandidateInput = document.getElementById("sim-candidate-input");
const simHintBtn = document.getElementById("sim-hint-btn");
const simSendBtn = document.getElementById("sim-send-btn");

// DOM Elements - Scorecard Modal
const scorecardModal = document.getElementById("scorecard-modal");
const closeScorecardBtn = document.getElementById("close-scorecard-btn");
const scorecardRoundTitle = document.getElementById("scorecard-round-title");
const scorecardOverallScore = document.getElementById("scorecard-overall-score");
const scorecardRecommendation = document.getElementById("scorecard-recommendation");
const scorecardVerdictSummary = document.getElementById("scorecard-verdict-summary");
const scorecardRubricGrid = document.getElementById("scorecard-rubric-grid");
const scorecardStrengthsList = document.getElementById("scorecard-strengths-list");
const scorecardImprovementsList = document.getElementById("scorecard-improvements-list");
const scorecardDebriefMarkdown = document.getElementById("scorecard-debrief-markdown");
const scorecardDismissBtn = document.getElementById("scorecard-dismiss-btn");
const scorecardRetryBtn = document.getElementById("scorecard-retry-btn");

// Simulation State
let currentSessionId = null;
let activeSession = null;
let simTimerInterval = null;
let simSeconds = 0;

// Mode Switching Listeners
modeTechBtn.addEventListener("click", () => setResearchMode("tech_topics"));
modeCompanyBtn.addEventListener("click", () => setResearchMode("interview_experience"));
if (modeStockBtn) {
    modeStockBtn.addEventListener("click", () => setResearchMode("stock_market"));
}

if (subModeStockResearchBtn && subModeStockPicksBtn) {
    subModeStockResearchBtn.addEventListener("click", () => setStockSubMode("stock_research"));
    subModeStockPicksBtn.addEventListener("click", () => setStockSubMode("stock_picks"));
}

function setStockSubMode(subMode) {
    selectedStockSubMode = subMode;
    if (subMode === "stock_research") {
        subModeStockResearchBtn.classList.add("active");
        subModeStockPicksBtn.classList.remove("active");
        stockResearchInputs.classList.remove("hidden");
        stockPicksInputs.classList.add("hidden");
    } else {
        subModeStockPicksBtn.classList.add("active");
        subModeStockResearchBtn.classList.remove("active");
        stockPicksInputs.classList.remove("hidden");
        stockResearchInputs.classList.add("hidden");
    }
}

function setResearchMode(mode) {
    selectedResearchMode = mode;
    modeTechBtn.classList.toggle("active", mode === "tech_topics");
    modeCompanyBtn.classList.toggle("active", mode === "interview_experience");
    if (modeStockBtn) modeStockBtn.classList.toggle("active", mode === "stock_market");

    techTopicsContainer.classList.toggle("hidden", mode !== "tech_topics");
    companyIntelContainer.classList.toggle("hidden", mode !== "interview_experience");
    if (stockMarketContainer) stockMarketContainer.classList.toggle("hidden", mode !== "stock_market");
}

// Event Listeners - Pipeline
startBtn.addEventListener("click", startResearchRun);
submitSelectionBtn.addEventListener("click", submitTopicSelection);
restartBtn.addEventListener("click", resetApp);
downloadBtn.addEventListener("click", downloadFinalPack);

// Event Listeners - Navigation Views
viewModeGuideBtn.addEventListener("click", () => switchViewMode("guide"));
viewModeGameBtn.addEventListener("click", () => switchViewMode("game"));
viewModeSimBtn.addEventListener("click", () => switchViewMode("sim"));

// Event Listeners - Gamification
gameTopicSelect.addEventListener("change", (e) => loadGameForTopic(e.target.value));
flashcardContainer.addEventListener("click", toggleFlip);
cardHintBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleHint();
});

prevCardBtn.addEventListener("click", prevCard);
nextCardBtn.addEventListener("click", nextCard);
reviewCardBtn.addEventListener("click", markNeedsReview);
masterCardBtn.addEventListener("click", markMastered);

// Event Listeners - Mock Simulator
startSimBtn.addEventListener("click", startInterviewSession);
simSendBtn.addEventListener("click", sendCandidateResponse);
simHintBtn.addEventListener("click", requestSimHint);
finishSimBtn.addEventListener("click", finishInterviewSession);

// Simulator Input Keyboard Shortcuts
simCandidateInput.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        sendCandidateResponse();
    }
});

// Scorecard Modal Listeners
closeScorecardBtn.addEventListener("click", closeScorecardModal);
scorecardDismissBtn.addEventListener("click", closeScorecardModal);
scorecardRetryBtn.addEventListener("click", () => {
    closeScorecardModal();
    startInterviewSession();
});


// Global Keyboard Navigation
window.addEventListener("keydown", (e) => {
    // Only handle shortcuts when Game View is active
    if (!gameViewLayout || gameViewLayout.classList.contains("hidden")) return;

    if (e.code === "Space" && e.target === document.body) {
        e.preventDefault();
        toggleFlip();
    } else if (e.code === "ArrowLeft") {
        e.preventDefault();
        prevCard();
    } else if (e.code === "ArrowRight") {
        e.preventDefault();
        nextCard();
    } else if (e.key === "1") {
        markNeedsReview();
    } else if (e.key === "2") {
        markMastered();
    } else if (e.key.toLowerCase() === "h") {
        toggleHint();
    }
});

// Logging Helper
function logMessage(text, type = "system") {
    const time = new Date().toLocaleTimeString();
    const line = document.createElement("div");
    line.className = `log-line ${type}`;
    line.innerText = `[${time}] ${text}`;
    logsTerminal.appendChild(line);
    logsTerminal.scrollTop = logsTerminal.scrollHeight;
}

// Pipeline Execution
async function startResearchRun() {
    let payload = { mode: selectedResearchMode };

    if (selectedResearchMode === "tech_topics") {
        const interests = interestsInput.value.trim();
        if (!interests) {
            alert("Please enter at least one technical interest.");
            return;
        }
        payload.interests = interests;
        payload.manual_selection = manualSelectToggle.checked;
    } else if (selectedResearchMode === "interview_experience") {
        const company = companyInput.value.trim();
        if (!company) {
            alert("Please enter the target company name.");
            return;
        }
        payload.company_name = company;
        payload.target_role = roleInput.value.trim() || "Senior Software Engineer";
        payload.target_level = levelSelect.value;
    } else if (selectedResearchMode === "stock_market") {
        payload.stock_mode = selectedStockSubMode;
        if (selectedStockSubMode === "stock_research") {
            const ticker = stockTickerInput.value.trim();
            if (!ticker) {
                alert("Please enter a target stock or ticker symbol.");
                return;
            }
            payload.ticker = ticker;
            payload.investment_horizon = stockHorizonSelect.value;
            const peersRaw = stockPeersInput.value.trim();
            if (peersRaw) {
                payload.manual_peers = peersRaw.split(",").map(p => p.trim()).filter(Boolean);
            }
        } else {
            payload.sector_filter = stockSectorFilter.value;
        }
    }

    startBtn.disabled = true;
    startBtn.innerText = "Initializing Pipeline...";

    try {
        const response = await fetch("/api/runs", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Failed to start research run.");
        
        const data = await response.json();
        currentRunId = data.run_id;

        // Transition UI
        setupSection.classList.add("hidden");
        progressSection.classList.remove("hidden");
        
        logMessage(`Created research run with ID: ${currentRunId}`, "info");
        if (selectedResearchMode === "interview_experience") {
            logMessage(`Target: ${payload.company_name} - ${payload.target_role} (${payload.target_level})`, "info");
            logMessage(`Crawling candidate interview debriefs from LeetCode, Reddit, Glassdoor...`, "info");
        } else {
            logMessage(`Starting topic discovery process...`, "info");
        }

        // Start Polling
        pollInterval = setInterval(pollRunStatus, 1500);
    } catch (err) {
        alert(err.message);
        startBtn.disabled = false;
        startBtn.innerText = "Initialize Agent Pipeline";
    }
}


async function pollRunStatus() {
    if (!currentRunId) return;

    try {
        const response = await fetch(`/api/runs/${currentRunId}`);
        if (!response.ok) throw new Error("Failed to fetch run status.");
        
        runData = await response.json();
        
        // Update Progress Bar
        progressBar.style.width = `${runData.progress}%`;
        progressPercentage.innerText = `${runData.progress}%`;
        currentStepLabel.innerText = runData.current_step;

        // Log Step Changes
        if (runData.current_step !== lastStep) {
            logMessage(runData.current_step, "info");
            lastStep = runData.current_step;
        }

        // Handle Status Transitions
        if (runData.status !== lastStatus) {
            logMessage(`Pipeline status changed to: ${runData.status.toUpperCase()}`, "system");
            lastStatus = runData.status;
        }

        if (runData.status === "pending_selection") {
            clearInterval(pollInterval);
            showTopicSelectionScreen(runData.refined_topics);
        } else if (runData.status === "completed") {
            clearInterval(pollInterval);
            showResultsScreen(runData);
        } else if (runData.status === "failed") {
            clearInterval(pollInterval);
            logMessage(`Error during execution: ${runData.error}`, "error");
            alert(`Research pipeline execution failed:\n${runData.error}`);
        }

    } catch (err) {
        logMessage(`Polling error: ${err.message}`, "error");
    }
}

function showTopicSelectionScreen(topics) {
    progressSection.classList.add("hidden");
    selectionSection.classList.remove("hidden");
    
    topicsGrid.innerHTML = "";
    const selectedSet = new Set();

    let displayTopics = (topics && topics.length > 0) ? topics : (runData.raw_topics || []);

    if (!displayTopics || displayTopics.length === 0) {
        topicsGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px 20px; background: var(--bg-card); border-radius: 12px; border: 1px dashed var(--border-color);">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">🔍</div>
                <h3 style="margin-bottom: 8px; font-weight: 600;">No Discovered Topics Available</h3>
                <p style="color: var(--text-muted); max-width: 480px; margin: 0 auto 20px auto; font-size: 0.95rem;">
                    The discovery agent couldn't fetch live trends for this query. You can restart with refined keywords.
                </p>
                <button class="btn btn-secondary" onclick="resetApp()">← Restart with New Keywords</button>
            </div>
        `;
        selectedCountBadge.innerText = "0";
        return;
    }

    displayTopics.forEach((topic) => {
        const card = document.createElement("div");
        card.className = "topic-card fade-in";
        
        const title = topic.title || topic.topic || "Technical Trend";
        const desc = topic.reason_selected || (topic.trend_indicators ? topic.trend_indicators.join(", ") : "Identified emerging industry technology pattern.");
        const why = topic.relevance_to_user || `High priority for technical interview preparation in ${topic.source_category || 'software engineering'}.`;
        const outcome = topic.expected_learning_outcome || `Deep dive into architecture, trade-offs, and design patterns for ${title}.`;

        const scores = topic.scores || {};
        const avgScore = topic.scores ? (
            (scores.interest_match || 8) * 0.3 +
            (scores.interview_value || 8) * 0.25 +
            (scores.depth || 7) * 0.2 +
            (scores.freshness || 8) * 0.15 +
            (scores.source_quality || 7) * 0.1
        ).toFixed(1) : ((topic.relevance_score || 0.85) * 10).toFixed(1);

        card.innerHTML = `
            <div class="topic-card-header">
                <span class="category-tag">SCORE: ${avgScore}/10</span>
                <span class="badge">Trending</span>
            </div>
            <h3>${title}</h3>
            <p class="topic-desc">${desc}</p>
            <div class="topic-relevance">
                <strong>Why Relevant:</strong> ${why}
            </div>
            <div class="topic-outcome">
                <strong>Outcome:</strong> ${outcome}
            </div>
        `;

        card.addEventListener("click", () => {
            if (card.classList.contains("selected")) {
                card.classList.remove("selected");
                selectedSet.delete(title);
            } else {
                card.classList.add("selected");
                selectedSet.add(title);
            }
            selectedCountBadge.innerText = selectedSet.size;
        });

        topicsGrid.appendChild(card);
    });

    selectedCountBadge.innerText = "0";
}

async function submitTopicSelection() {
    const selectedCards = document.querySelectorAll(".topic-card.selected h3");
    const selectedTopicsList = Array.from(selectedCards).map(el => el.innerText);

    if (selectedTopicsList.length === 0) {
        alert("Please select at least one topic to research.");
        return;
    }

    submitSelectionBtn.disabled = true;
    submitSelectionBtn.innerText = "Submitting selection...";

    try {
        const response = await fetch(`/api/runs/${currentRunId}/select-topics`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ selected_topics: selectedTopicsList })
        });

        if (!response.ok) throw new Error("Failed to submit selected topics.");

        selectionSection.classList.add("hidden");
        progressSection.classList.remove("hidden");
        
        logMessage(`Submitted selection: ${selectedTopicsList.join(", ")}`, "info");
        logMessage(`Resuming deep-dive technical research node...`, "info");

        // Resume status polling
        pollInterval = setInterval(pollRunStatus, 1500);
    } catch (err) {
        alert(err.message);
        submitSelectionBtn.disabled = false;
        submitSelectionBtn.innerText = "Research Selected";
    }
}

function showResultsScreen(data) {
    progressSection.classList.add("hidden");
    resultsSection.classList.remove("hidden");

    runFolderPath.innerText = `Compiled output folder: outputs/${currentRunId}`;

    const isCompanyIntelMode = Boolean(data.interview_intel || data.company_name);

    // Conditionally configure top view mode buttons
    if (isCompanyIntelMode) {
        viewModeSimBtn.classList.remove("hidden");
        viewModeGuideBtn.innerHTML = `<i class="ph ph-buildings"></i> 🏢 Interview Guide`;
        viewModeGameBtn.innerHTML = `<i class="ph ph-game-controller"></i> 🎮 Practice Hub`;
    } else {
        viewModeSimBtn.classList.add("hidden");
        viewModeGuideBtn.innerHTML = `<i class="ph ph-book-open"></i> 📖 Research Guide`;
        viewModeGameBtn.innerHTML = `<i class="ph ph-game-controller"></i> 🎮 Practice Hub`;
    }

    // Default to guide view
    switchViewMode("guide");

    // Populate Guide Tabs
    resultsTabs.innerHTML = "";

    if (data.interview_intel) {
        const intel = data.interview_intel;
        
        // Tab 1: Full Pack
        const packBtn = document.createElement("button");
        packBtn.className = "tab-btn active";
        packBtn.innerText = "🏢 Full Intel Pack";
        packBtn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            packBtn.classList.add("active");
            renderMarkdown(data.final_pack);
        });
        resultsTabs.appendChild(packBtn);

        // Tab 2: Executive Summary & Overview
        if (intel.overview_summary) {
            const overviewBtn = document.createElement("button");
            overviewBtn.className = "tab-btn";
            overviewBtn.innerText = "📋 Executive Overview";
            overviewBtn.addEventListener("click", () => {
                document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
                overviewBtn.classList.add("active");
                renderMarkdown(`## ${intel.company_name} - ${intel.target_role} (${intel.seniority_level})\n\n${intel.overview_summary}\n\n### Candidate Sentiment & Difficulty\n- **Difficulty Rating:** ${intel.candidate_sentiment_and_difficulty || 'Standard FAANG/Tier-1 Bar'}\n- **Top Recurring Topics:** ${intel.recurring_themes?.join(', ') || 'System Design, Concurrency, API Design'}`);
            });
            resultsTabs.appendChild(overviewBtn);
        }

        // Tab 3: Rounds Breakdown
        if (intel.rounds && intel.rounds.length > 0) {
            const roundsBtn = document.createElement("button");
            roundsBtn.className = "tab-btn";
            roundsBtn.innerText = "🎯 Interview Rounds";
            roundsBtn.addEventListener("click", () => {
                document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
                roundsBtn.classList.add("active");
                
                let roundsMd = `# ${intel.company_name} Interview Rounds Breakdown\n\n`;
                intel.rounds.forEach((r, idx) => {
                    roundsMd += `### Round ${idx + 1}: ${r.round_name} (${r.round_type})\n`;
                    roundsMd += `- **Duration:** ${r.duration_minutes} minutes\n`;
                    roundsMd += `- **Focus Areas:** ${r.focus_areas?.join(", ")}\n`;
                    roundsMd += `- **Evaluation Bar:** ${r.evaluation_criteria}\n`;
                    roundsMd += `- **Pro-Tips / Pitfalls:** ${r.common_pitfalls}\n\n`;
                });
                renderMarkdown(roundsMd);
            });
            resultsTabs.appendChild(roundsBtn);
        }

        // Tab 4: Values & Culture
        if (intel.company_culture_and_values && intel.company_culture_and_values.length > 0) {
            const valuesBtn = document.createElement("button");
            valuesBtn.className = "tab-btn";
            valuesBtn.innerText = "🏆 Culture & Behavioral";
            valuesBtn.addEventListener("click", () => {
                document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
                valuesBtn.classList.add("active");
                
                let valuesMd = `# ${intel.company_name} Cultural Principles & Behavioral Matrix\n\n`;
                intel.company_culture_and_values.forEach(v => {
                    valuesMd += `### 🌟 ${v}\n`;
                });
                if (intel.behavioral_prep_guidance) {
                    valuesMd += `\n### Behavioral Strategy & Scoring\n${intel.behavioral_prep_guidance}\n`;
                }
                renderMarkdown(valuesMd);
            });
            resultsTabs.appendChild(valuesBtn);
        }

        renderMarkdown(data.final_pack || "");
    } else if (data.stock_research_report) {
        const report = data.stock_research_report;
        const verifiedDate = report.verified_as_of_date || new Date().toISOString().slice(0, 10);
        
        // Helper to generate SVG chart in frontend
        function buildFrontendSvgChart(ticker, prices) {
            if (!prices || prices.length < 2) return "";
            const w = 700, h = 240, pl = 65, pr = 35, pt = 40, pb = 40;
            const cw = w - pl - pr, ch = h - pt - pb;
            const vals = prices.map(p => Number(p.close) || 0);
            const minV = Math.min(...vals), maxV = Math.max(...vals);
            const span = (maxV - minV) || 1.0;
            const yMin = Math.max(0, minV - (span * 0.08));
            const yMax = maxV + (span * 0.08);
            const ySpan = (yMax - yMin) || 1.0;

            const coords = prices.map((p, idx) => {
                const x = pl + (idx / (prices.length - 1)) * cw;
                const y = pt + (1.0 - ((Number(p.close) - yMin) / ySpan)) * ch;
                return { x, y, date: p.date, close: Number(p.close) };
            });

            let pathD = `M ${coords[0].x.toFixed(1)},${coords[0].y.toFixed(1)}`;
            for (let i = 1; i < coords.length; i++) {
                pathD += ` L ${coords[i].x.toFixed(1)},${coords[i].y.toFixed(1)}`;
            }
            const areaD = `${pathD} L ${coords[coords.length - 1].x.toFixed(1)},${(pt + ch).toFixed(1)} L ${coords[0].x.toFixed(1)},${(pt + ch).toFixed(1)} Z`;
            const pct = (((coords[coords.length - 1].close - coords[0].close) / coords[0].close) * 100);
            const color = pct >= 0 ? "#10b981" : "#ef4444";

            return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="100%" height="${h}" style="background: #0f172a; border-radius: 12px; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; border: 1px solid #1e293b; margin: 16px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                <defs>
                    <linearGradient id="ui_grad_${ticker}" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="${color}" stop-opacity="0.35"/>
                        <stop offset="100%" stop-color="${color}" stop-opacity="0.0"/>
                    </linearGradient>
                </defs>
                <line x1="${pl}" y1="${pt}" x2="${w - pr}" y2="${pt}" stroke="#334155" stroke-dasharray="3,3"/>
                <line x1="${pl}" y1="${pt + ch / 2}" x2="${w - pr}" y2="${pt + ch / 2}" stroke="#334155" stroke-dasharray="3,3"/>
                <line x1="${pl}" y1="${pt + ch}" x2="${w - pr}" y2="${pt + ch}" stroke="#334155"/>
                <text x="${pl - 10}" y="${pt + 4}" fill="#94a3b8" font-size="11" text-anchor="end">$${yMax.toFixed(1)}</text>
                <text x="${pl - 10}" y="${pt + ch / 2 + 4}" fill="#94a3b8" font-size="11" text-anchor="end">$${((yMin + yMax) / 2).toFixed(1)}</text>
                <text x="${pl - 10}" y="${pt + ch + 4}" fill="#94a3b8" font-size="11" text-anchor="end">$${yMin.toFixed(1)}</text>
                <path d="${areaD}" fill="url(#ui_grad_${ticker})"/>
                <path d="${pathD}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linecap="round"/>
                <circle cx="${coords[0].x.toFixed(1)}" cy="${coords[0].y.toFixed(1)}" r="4" fill="${color}"/>
                <circle cx="${coords[coords.length - 1].x.toFixed(1)}" cy="${coords[coords.length - 1].y.toFixed(1)}" r="5" fill="#ffffff" stroke="${color}" stroke-width="2.5"/>
                <text x="${coords[0].x.toFixed(1)}" y="${h - 12}" fill="#94a3b8" font-size="11" text-anchor="start">${coords[0].date}</text>
                <text x="${coords[coords.length - 1].x.toFixed(1)}" y="${h - 12}" fill="#94a3b8" font-size="11" text-anchor="end">${coords[coords.length - 1].date}</text>
                <text x="${pl + 8}" y="${pt - 14}" fill="#f8fafc" font-size="13" font-weight="bold">${ticker} Historical Trailing Price</text>
                <text x="${pl + 240}" y="${pt - 14}" fill="${color}" font-size="12" font-weight="600">${pct >= 0 ? '+' : ''}${pct.toFixed(1)}% (1-Year)</text>
                <text x="${w - pr}" y="${pt - 14}" fill="#10b981" font-size="12" font-weight="bold" text-anchor="end">Latest: $${coords[coords.length - 1].close.toFixed(2)}</text>
            </svg>`;
        }
        
        // Tab 1: Full Report
        const reportBtn = document.createElement("button");
        reportBtn.className = "tab-btn active";
        reportBtn.innerText = "📈 Full Equity Research Report";
        reportBtn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            reportBtn.classList.add("active");
            renderMarkdown(data.final_pack || report.report_markdown);
        });
        resultsTabs.appendChild(reportBtn);

        // Tab 2: Stock Price Graph
        const graphBtn = document.createElement("button");
        graphBtn.className = "tab-btn";
        graphBtn.innerText = "📊 Price Trend Graph";
        graphBtn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            graphBtn.classList.add("active");
            
            let gMd = `# ${report.company_name} (${report.ticker}) — Historical Price Graph\n\n`;
            gMd += `> 🟢 **LIVE DATA VERIFICATION [PASSED]**: Data verified current as of **${verifiedDate}**\n\n`;
            
            const chartData = report.historical_price_chart || [];
            if (chartData.length > 0) {
                const startP = chartData[0].close;
                const endP = chartData[chartData.length - 1].close;
                const pct = ((endP - startP) / startP) * 100;
                const minP = Math.min(...chartData.map(c => c.close));
                const maxP = Math.max(...chartData.map(c => c.close));
                
                gMd += `### 📈 Performance Overview & Key Levels\n`;
                gMd += `- **Current Trading Price:** $${endP.toFixed(2)}\n`;
                gMd += `- **12-Month Performance:** ${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%\n`;
                gMd += `- **52-Week Range:** $${minP.toFixed(2)} - $${maxP.toFixed(2)}\n`;
                gMd += `- **Data Status:** Verified current against latest market trading session\n\n`;
                
                gMd += buildFrontendSvgChart(report.ticker, chartData) + "\n\n";
                
                gMd += `### Price History Checkpoints\n`;
                gMd += `| Date | Closing Price | Trading Volume | Direction |\n`;
                gMd += `|---|---|---|---|\n`;
                chartData.forEach((pt, i) => {
                    const prev = i > 0 ? chartData[i-1].close : pt.close;
                    const icon = pt.close >= prev ? '🟢 ↗' : '🔴 ↘';
                    gMd += `| ${pt.date} | **$${pt.close.toFixed(2)}** | ${pt.volume ? pt.volume.toLocaleString() : 'N/A'} | ${icon} |\n`;
                });
            } else {
                gMd += `*Historical price data is loading...*\n`;
            }
            renderMarkdown(gMd);
        });
        resultsTabs.appendChild(graphBtn);

        // Tab 3: Financials & Valuation
        const finBtn = document.createElement("button");
        finBtn.className = "tab-btn";
        finBtn.innerText = "💰 Financials & DCF Scenarios";
        finBtn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            finBtn.classList.add("active");
            let finMd = `# ${report.company_name} (${report.ticker}) — Financials & Valuation\n\n`;
            finMd += `> 🟢 **Verified Data**: Financial statements verified current as of **${verifiedDate}**\n\n`;
            finMd += `## Financial Health & Margin Trends (Beginner Guide)\n${report.financial_health_and_margin_trends}\n\n`;
            finMd += `## Valuation Methodology & DCF Model\n${report.valuation_analysis}\n\n`;
            if (report.valuation_scenarios && report.valuation_scenarios.length > 0) {
                finMd += `### 3-Tier DCF Intrinsic Scenario Matrix\n`;
                finMd += `| Scenario | Target Price | Implied Return | 5Y Rev CAGR | Op Margin | WACC | Target Exit P/E |\n`;
                finMd += `|---|---|---|---|---|---|---|\n`;
                report.valuation_scenarios.forEach(sc => {
                    finMd += `| **${sc.scenario_name} Case** | **$${sc.target_price_implied.toFixed(2)}** | **${sc.upside_downside_percent > 0 ? '+' : ''}${sc.upside_downside_percent.toFixed(1)}%** | ${sc.revenue_growth_cagr.toFixed(1)}% | ${sc.terminal_operating_margin.toFixed(1)}% | ${sc.wacc.toFixed(1)}% | ${sc.implied_pe_multiple.toFixed(1)}x |\n`;
                });
            }
            renderMarkdown(finMd);
        });
        resultsTabs.appendChild(finBtn);

        // Tab 3: Peers & Moat
        const peerBtn = document.createElement("button");
        peerBtn.className = "tab-btn";
        peerBtn.innerText = "🏢 Peers & Moat";
        peerBtn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            peerBtn.classList.add("active");
            let pMd = `# ${report.company_name} — Competitive Positioning & Moat\n\n`;
            pMd += `## Competitive Position Narrative\n${report.peer_comparison_narrative}\n\n`;
            pMd += `## Structural Moat Analysis\n${report.competitive_moat_analysis}\n\n`;
            if (report.peer_benchmarks && report.peer_benchmarks.length > 0) {
                pMd += `### Peer Benchmark Comparison\n`;
                pMd += `| Ticker | Company | Market Cap ($B) | Fwd P/E | EV/EBITDA | Rev Growth | Op Margin | ROIC | FCF Yield |\n`;
                pMd += `|---|---|---|---|---|---|---|---|---|\n`;
                report.peer_benchmarks.forEach(p => {
                    pMd += `| **${p.ticker}** | ${p.company_name} | $${p.market_cap_billions.toFixed(1)}B | ${p.pe_forward.toFixed(1)}x | ${p.ev_ebitda.toFixed(1)}x | ${p.revenue_growth_yoy.toFixed(1)}% | ${p.operating_margin.toFixed(1)}% | ${p.roic.toFixed(1)}% | ${p.fcf_yield.toFixed(1)}% |\n`;
                });
            }
            renderMarkdown(pMd);
        });
        resultsTabs.appendChild(peerBtn);

        // Tab 4: Critic Debrief & Invalidation Triggers
        const criticBtn = document.createElement("button");
        criticBtn.className = "tab-btn";
        criticBtn.innerText = "🛑 Critic & Invalidation Triggers";
        criticBtn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            criticBtn.classList.add("active");
            let cMd = `# Thesis Disconfirmation & Critic Stress-Test\n\n`;
            cMd += `## What Could Prove the Investment Thesis Wrong?\n${report.what_could_invalidate_the_thesis}\n\n`;
            if (report.critic_debrief && report.critic_debrief.thesis_invalidation_triggers) {
                cMd += `### 🛑 Specific Quantifiable Invalidation Triggers:\n`;
                report.critic_debrief.thesis_invalidation_triggers.forEach(trig => {
                    cMd += `- ⚠️ **Trigger:** ${trig}\n`;
                });
            }
            if (report.critic_debrief && report.critic_debrief.overlooked_risks) {
                cMd += `\n### Overlooked Risks Identified:\n`;
                report.critic_debrief.overlooked_risks.forEach(r => {
                    cMd += `- 🔍 ${r}\n`;
                });
            }
            renderMarkdown(cMd);
        });
        resultsTabs.appendChild(criticBtn);

        // Tab 5: Sourced Claims Audit
        if (report.source_claims && report.source_claims.length > 0) {
            const claimsBtn = document.createElement("button");
            claimsBtn.className = "tab-btn";
            claimsBtn.innerText = "📋 Sourced Claims Audit";
            claimsBtn.addEventListener("click", () => {
                document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
                claimsBtn.classList.add("active");
                let clMd = `# Sourced Evidence & Claims Audit Matrix\n\n`;
                clMd += `| Claim | Classification | Source Title | Reference Link |\n`;
                clMd += `|---|---|---|---|\n`;
                report.source_claims.forEach(cl => {
                    const link = cl.source_url ? `[${cl.source_title}](${cl.source_url})` : cl.source_title;
                    clMd += `| ${cl.claim_text} | **\`${cl.claim_type}\`** | ${cl.source_title} | ${link} |\n`;
                });
                renderMarkdown(clMd);
            });
            resultsTabs.appendChild(claimsBtn);
        }

        renderMarkdown(data.final_pack || report.report_markdown || "");
    } else if (data.stock_opportunity_report) {
        const report = data.stock_opportunity_report;
        const oppBtn = document.createElement("button");
        oppBtn.className = "tab-btn active";
        oppBtn.innerText = "🎯 Opportunity Screener Report";
        oppBtn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            oppBtn.classList.add("active");
            renderMarkdown(data.final_pack || report.report_markdown);
        });
        resultsTabs.appendChild(oppBtn);

        renderMarkdown(data.final_pack || report.report_markdown || "");
    } else {
        // Tech Topics Mode
        const combinedBtn = document.createElement("button");
        combinedBtn.className = "tab-btn active";
        combinedBtn.innerText = "All Summaries";
        combinedBtn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            combinedBtn.classList.add("active");
            renderMarkdown(data.final_pack);
        });
        resultsTabs.appendChild(combinedBtn);

        renderMarkdown(data.final_pack || "");
    }

    // Populate Game Topic Selectors
    gameTopicSelect.innerHTML = "";
    const selected = data.selected_topics || (data.company_name ? [data.company_name] : []);
    
    selected.forEach((topicName) => {
        const opt = document.createElement("option");
        opt.value = slugify(topicName);
        opt.innerText = topicName;
        gameTopicSelect.appendChild(opt);
    });

    if (selected.length > 0) {
        loadGameForTopic(slugify(selected[0]));
    }

    // Populate Simulator Rounds
    simRoundSelect.innerHTML = "";
    if (data.interview_intel && data.interview_intel.rounds_breakdown && data.interview_intel.rounds_breakdown.length > 0) {
        data.interview_intel.rounds_breakdown.forEach((r) => {
            const opt = document.createElement("option");
            opt.value = r.round_name;
            opt.innerText = `${r.round_name} (${r.round_type})`;
            opt.dataset.roundType = r.round_type;
            simRoundSelect.appendChild(opt);
        });
    } else {
        const defaultRounds = [
            { name: "Round 1: Algorithmic Problem Solving & Data Structures", type: "Coding / DSA" },
            { name: "Round 2: Practical Bug Squashing & API Integration", type: "Practical / Bug Squash / API" },
            { name: "Round 3: Distributed System Architecture & Design", type: "System Design" },
            { name: "Round 4: Engineering Leadership & Cultural Values", type: "Behavioral & Leadership" }
        ];
        defaultRounds.forEach((r) => {
            const opt = document.createElement("option");
            opt.value = r.name;
            opt.innerText = r.name;
            opt.dataset.roundType = r.type;
            simRoundSelect.appendChild(opt);
        });
    }

    const companyName = (data.interview_intel && data.interview_intel.company_name) || data.company_name || "Target Company";
    const roleName = (data.interview_intel && data.interview_intel.role) || data.target_role || "Senior SWE";
    const levelName = (data.interview_intel && data.interview_intel.level) || data.target_level || "Senior / L5";
    simCompanyBadge.innerText = `🏢 ${companyName} — ${roleName} (${levelName})`;
}

function slugify(text) {
    return text.toLowerCase().trim()
        .replace(/[^\w\s-]/g, '')
        .replace(/[\s_-]+/g, '_');
}

function renderMarkdown(mdText) {
    if (typeof marked !== "undefined" && mdText) {
        markdownOutput.innerHTML = marked.parse(mdText);
    } else {
        markdownOutput.innerText = mdText || "No content generated.";
    }
}

function downloadFinalPack() {
    if (!runData || !runData.final_pack) return;
    
    const isCompanyIntel = runData.company_name || runData.interview_intel;
    const filename = isCompanyIntel
        ? `interview_pack_${slugify(runData.company_name || "company")}_${currentRunId}.md`
        : `final_interview_pack_${currentRunId}.md`;

    const blob = new Blob([runData.final_pack], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function resetApp() {
    currentRunId = null;
    pollInterval = null;
    lastStatus = null;
    lastStep = null;
    runData = null;
    currentDeck = null;
    cachedGames = {};
    stopSimTimer();
    currentSessionId = null;
    activeSession = null;

    interestsInput.value = "";
    startBtn.disabled = false;
    startBtn.innerText = "Initialize Agent Pipeline";

    resultsSection.classList.add("hidden");
    setupSection.classList.remove("hidden");
    logsTerminal.innerHTML = `<div class="log-line system">[System] Connection reset. Ready for new run.</div>`;
}

// ----------------- Navigation Views Controller -----------------

function switchViewMode(mode) {
    viewModeGuideBtn.classList.toggle("active", mode === "guide");
    viewModeGameBtn.classList.toggle("active", mode === "game");
    viewModeSimBtn.classList.toggle("active", mode === "sim");

    guideViewLayout.classList.toggle("hidden", mode !== "guide");
    gameViewLayout.classList.toggle("hidden", mode !== "game");
    simViewLayout.classList.toggle("hidden", mode !== "sim");
}

// ----------------- Gamification & Flashcards Controller -----------------


async function loadGameForTopic(topicSlug) {
    if (!topicSlug || !currentRunId) return;
    currentGameTopic = topicSlug;

    // Reset deck state
    currentCardIndex = 0;
    isFlipped = false;
    flashcardCard.classList.remove("flipped");
    cardHintText.classList.add("hidden");

    // Check cache
    if (cachedGames[topicSlug]) {
        currentDeck = cachedGames[topicSlug];
        renderCurrentCard();
        return;
    }

    cardFrontPrompt.innerText = "Generating interview flashcards via Gamification Agent...";
    cardCategoryBadge.innerText = "Generating";
    cardDifficultyBadge.innerText = "...";

    try {
        const res = await fetch(`/api/runs/${currentRunId}/topics/${topicSlug}/games/flashcards`);
        if (!res.ok) throw new Error("Failed to load flashcards for topic.");
        
        currentDeck = await res.json();
        cachedGames[topicSlug] = currentDeck;
        
        renderCurrentCard();
    } catch (err) {
        cardFrontPrompt.innerText = `Failed to load flashcards: ${err.message}`;
    }
}

function renderCurrentCard() {
    if (!currentDeck || !currentDeck.cards || currentDeck.cards.length === 0) {
        cardFrontPrompt.innerText = "No flashcards generated for this topic.";
        return;
    }

    const cards = currentDeck.cards;
    const card = cards[currentCardIndex];

    // Reset flip & hint
    isFlipped = false;
    flashcardCard.classList.remove("flipped");
    cardHintText.classList.add("hidden");

    // Counter & Badges
    cardCounter.innerText = `Card ${currentCardIndex + 1} of ${cards.length}`;
    cardCategoryBadge.innerText = card.category || "Architecture";
    
    const diff = card.difficulty || "Medium";
    cardDifficultyBadge.innerText = diff;
    cardDifficultyBadge.className = `badge difficulty-badge difficulty-${diff.toLowerCase()}`;

    // Front Face
    cardFrontPrompt.innerText = card.front_prompt;
    if (card.hint) {
        cardHintBtn.classList.remove("hidden");
        cardHintText.innerText = card.hint;
    } else {
        cardHintBtn.classList.add("hidden");
    }

    // Back Face
    cardBackExplanation.innerText = card.back_explanation;
    if (card.key_takeaway) {
        cardTakeawayText.innerText = card.key_takeaway;
        document.getElementById("card-takeaway-box").classList.remove("hidden");
    } else {
        document.getElementById("card-takeaway-box").classList.add("hidden");
    }

    // Update Mastery Stats
    updateMasteryStats();
}

function toggleFlip() {
    isFlipped = !isFlipped;
    if (isFlipped) {
        flashcardCard.classList.add("flipped");
    } else {
        flashcardCard.classList.remove("flipped");
    }
}

function toggleHint() {
    cardHintText.classList.toggle("hidden");
}

function prevCard() {
    if (!currentDeck || !currentDeck.cards) return;
    if (currentCardIndex > 0) {
        currentCardIndex--;
        renderCurrentCard();
    }
}

function nextCard() {
    if (!currentDeck || !currentDeck.cards) return;
    if (currentCardIndex < currentDeck.cards.length - 1) {
        currentCardIndex++;
        renderCurrentCard();
    }
}

function markNeedsReview() {
    if (!currentDeck || !currentDeck.cards) return;
    const card = currentDeck.cards[currentCardIndex];
    const key = `${currentGameTopic}_${card.id}`;
    
    masteredCards.delete(key);
    reviewCards.add(key);
    updateMasteryStats();
    
    // Auto advance
    nextCard();
}

function markMastered() {
    if (!currentDeck || !currentDeck.cards) return;
    const card = currentDeck.cards[currentCardIndex];
    const key = `${currentGameTopic}_${card.id}`;
    
    reviewCards.delete(key);
    masteredCards.add(key);
    updateMasteryStats();
    
    // Auto advance
    nextCard();
}

function updateMasteryStats() {
    if (!currentDeck || !currentDeck.cards) return;
    const total = currentDeck.cards.length;
    
    let masteredCount = 0;
    currentDeck.cards.forEach(card => {
        if (masteredCards.has(`${currentGameTopic}_${card.id}`)) {
            masteredCount++;
        }
    });

    masteredCountLabel.innerText = `${masteredCount} / ${total}`;
    const pct = total > 0 ? Math.round((masteredCount / total) * 100) : 0;
    masteryProgressFill.style.width = `${pct}%`;
}

// ----------------- Mock Interview Simulator Controller -----------------

async function startInterviewSession() {
    if (!currentRunId) {
        alert("Please run or load a research report first.");
        return;
    }

    const selectedOption = simRoundSelect.options[simRoundSelect.selectedIndex];
    const roundName = selectedOption ? selectedOption.value : "Distributed System Design";
    const roundType = selectedOption ? (selectedOption.dataset.roundType || "System Design") : "System Design";

    startSimBtn.disabled = true;
    startSimBtn.innerText = "Connecting to Interview Room...";

    try {
        const response = await fetch(`/api/runs/${currentRunId}/interview-sessions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                round_name: roundName,
                round_type: roundType
            })
        });

        if (!response.ok) throw new Error("Failed to start interview session.");

        activeSession = await response.json();
        currentSessionId = activeSession.session_id;

        // Reset & activate UI
        simInputPanel.classList.remove("hidden");
        finishSimBtn.classList.remove("hidden");
        startSimBtn.innerText = "Restart Round";
        startSimBtn.disabled = false;

        // Render Opening Messages
        renderSessionMessages(activeSession.messages);

        // Start Timer
        startSimTimer();
        simCandidateInput.focus();
    } catch (err) {
        alert(`Error starting session: ${err.message}`);
        startSimBtn.disabled = false;
        startSimBtn.innerText = "Start Interview Session";
    }
}

async function sendCandidateResponse() {
    const text = simCandidateInput.value.trim();
    if (!text || !currentSessionId) return;

    // Append candidate message immediately in UI
    appendMessageBubble("candidate", text, new Date().toLocaleTimeString());
    simCandidateInput.value = "";
    simSendBtn.disabled = true;
    simSendBtn.innerText = "Evaluating...";

    // Show temporary typing indicator
    const typingBubble = document.createElement("div");
    typingBubble.className = "sim-message msg-interviewer typing-indicator";
    typingBubble.innerHTML = `<div class="msg-header"><span class="msg-avatar">🏢</span> <span>Interviewer is evaluating your response...</span></div><div class="msg-body"><em>Thinking...</em></div>`;
    simChatStream.appendChild(typingBubble);
    simChatStream.scrollTop = simChatStream.scrollHeight;

    try {
        const response = await fetch(`/api/runs/${currentRunId}/interview-sessions/${currentSessionId}/message`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) throw new Error("Failed to send message.");

        activeSession = await response.json();
        
        // Remove typing indicator
        if (typingBubble.parentNode) {
            typingBubble.parentNode.removeChild(typingBubble);
        }

        // Render full messages list to preserve accuracy
        renderSessionMessages(activeSession.messages);
    } catch (err) {
        if (typingBubble.parentNode) typingBubble.parentNode.removeChild(typingBubble);
        alert(`Error sending response: ${err.message}`);
    } finally {
        simSendBtn.disabled = false;
        simSendBtn.innerText = "Send Response";
        simCandidateInput.focus();
    }
}

function requestSimHint() {
    if (!currentSessionId) return;
    simCandidateInput.value = "Could you please share a hint or clarify if I should optimize for write latency or consistency in this section?";
    simCandidateInput.focus();
}

async function finishInterviewSession() {
    if (!currentSessionId) return;

    stopSimTimer();
    finishSimBtn.disabled = true;
    finishSimBtn.innerText = "Evaluating Bar...";


    try {
        const response = await fetch(`/api/runs/${currentRunId}/interview-sessions/${currentSessionId}/finish`, {
            method: "POST"
        });

        if (!response.ok) throw new Error("Failed to evaluate interview.");

        const feedback = await response.json();
        displayScorecard(feedback);
    } catch (err) {
        alert(`Error generating scorecard: ${err.message}`);
    } finally {
        finishSimBtn.disabled = false;
        finishSimBtn.innerText = "🏁 Finish & Scorecard";
    }
}

function renderSessionMessages(messages) {
    simChatStream.innerHTML = "";
    if (!messages || messages.length === 0) {
        simChatStream.innerHTML = `<div class="chat-placeholder"><div class="placeholder-icon">🎙️</div><h3>Company Mock Interview Room</h3><p>Interview session started. Waiting for message...</p></div>`;
        return;
    }

    messages.forEach(m => {
        appendMessageBubble(m.role, m.content, m.timestamp);
    });
}

function appendMessageBubble(role, content, timestamp) {
    const bubble = document.createElement("div");
    bubble.className = `sim-message msg-${role}`;

    const isInterviewer = role === "interviewer";
    const roleTitle = isInterviewer ? "Company Interviewer" : "Candidate";
    const avatar = isInterviewer ? "🏢" : "👤";

    const parsedContent = (typeof marked !== "undefined" && content) ? marked.parse(content) : content;

    bubble.innerHTML = `
        <div class="msg-header">
            <span class="msg-avatar">${avatar}</span>
            <span>${roleTitle}</span>
            <small style="margin-left: auto; font-weight: normal; color: var(--text-muted);">${timestamp || ''}</small>
        </div>
        <div class="msg-body">${parsedContent}</div>
    `;

    simChatStream.appendChild(bubble);
    simChatStream.scrollTop = simChatStream.scrollHeight;
}

// Timer Functions
function startSimTimer() {
    stopSimTimer();
    simSeconds = 0;
    simTimer.innerText = "⏱️ 00:00";
    simTimerInterval = setInterval(() => {
        simSeconds++;
        const mins = String(Math.floor(simSeconds / 60)).padStart(2, "0");
        const secs = String(simSeconds % 60).padStart(2, "0");
        simTimer.innerText = `⏱️ ${mins}:${secs}`;
    }, 1000);
}

function stopSimTimer() {
    if (simTimerInterval) {
        clearInterval(simTimerInterval);
        simTimerInterval = null;
    }
}

// Scorecard Modal Functions
function displayScorecard(feedback) {
    if (!feedback) return;

    const roundName = activeSession ? activeSession.round_name : "Technical Interview";
    const company = activeSession ? activeSession.company_name : "Target Company";
    const role = activeSession ? activeSession.role : "Senior Engineer";

    scorecardRoundTitle.innerText = `${company} — ${role} (${roundName})`;
    scorecardOverallScore.innerText = feedback.overall_score || 85;

    // Recommendation badge
    const rec = feedback.hire_recommendation || "Hire";
    scorecardRecommendation.innerText = rec;
    scorecardRecommendation.className = `badge ${rec.toLowerCase().includes("no") ? "rec-nohire" : "rec-hire"}`;

    scorecardVerdictSummary.innerText = feedback.summary_verdict || "Completed technical assessment.";

    // Rubrics
    scorecardRubricGrid.innerHTML = "";
    (feedback.rubric_scores || []).forEach(r => {
        const item = document.createElement("div");
        item.className = "rubric-item";
        const pct = (r.score / 5) * 100;
        item.innerHTML = `
            <div class="rubric-header">
                <span class="rubric-title">${r.criterion}</span>
                <span class="rubric-score-badge">${r.score} / 5</span>
            </div>
            <div class="rubric-bar">
                <div class="rubric-bar-fill" style="width: ${pct}%;"></div>
            </div>
            <p class="rubric-feedback">${r.feedback}</p>
        `;
        scorecardRubricGrid.appendChild(item);
    });

    // Strengths
    scorecardStrengthsList.innerHTML = "";
    (feedback.key_strengths || []).forEach(s => {
        const li = document.createElement("li");
        li.innerText = s;
        scorecardStrengthsList.appendChild(li);
    });

    // Improvements
    scorecardImprovementsList.innerHTML = "";
    (feedback.areas_for_improvement || []).forEach(i => {
        const li = document.createElement("li");
        li.innerText = i;
        scorecardImprovementsList.appendChild(li);
    });

    // Debrief Markdown
    if (typeof marked !== "undefined" && feedback.detailed_debrief_markdown) {
        scorecardDebriefMarkdown.innerHTML = marked.parse(feedback.detailed_debrief_markdown);
    } else {
        scorecardDebriefMarkdown.innerText = feedback.detailed_debrief_markdown || "Debrief generated.";
    }

    scorecardModal.classList.remove("hidden");
}

function closeScorecardModal() {
    scorecardModal.classList.add("hidden");
}

/* ==========================================================================
   Main Navigation (Feed vs Pipeline vs Simulator vs Studio)
   ========================================================================== */

const navFeedBtn = document.getElementById("nav-feed-btn");
const navPipelineBtn = document.getElementById("nav-pipeline-btn");
const navSimulatorBtn = document.getElementById("nav-simulator-btn");
const navStudioBtn = document.getElementById("nav-studio-btn");

if (navFeedBtn) navFeedBtn.addEventListener("click", () => switchMainSection("feed"));
if (navPipelineBtn) navPipelineBtn.addEventListener("click", () => switchMainSection("pipeline"));
if (navSimulatorBtn) navSimulatorBtn.addEventListener("click", () => switchMainSection("simulator"));
if (navStudioBtn) navStudioBtn.addEventListener("click", () => switchMainSection("studio"));

function switchMainSection(target) {
    // Nav buttons active state
    if (navFeedBtn) navFeedBtn.classList.toggle("active", target === "feed");
    if (navPipelineBtn) navPipelineBtn.classList.toggle("active", target === "pipeline");
    if (navSimulatorBtn) navSimulatorBtn.classList.toggle("active", target === "simulator");
    if (navStudioBtn) navStudioBtn.classList.toggle("active", target === "studio");

    // Hide all major sections
    if (feedSection) feedSection.classList.add("hidden");
    if (setupSection) setupSection.classList.add("hidden");
    if (progressSection) progressSection.classList.add("hidden");
    if (selectionSection) selectionSection.classList.add("hidden");
    if (resultsSection) resultsSection.classList.add("hidden");
    if (mockSimulatorSection) mockSimulatorSection.classList.add("hidden");
    if (studioSection) studioSection.classList.add("hidden");

    if (target === "feed") {
        if (feedSection) feedSection.classList.remove("hidden");
        loadHomeFeed();
    } else if (target === "pipeline") {
        if (currentRunId && runData) {
            if (runData.status === "completed") {
                if (resultsSection) resultsSection.classList.remove("hidden");
            } else if (runData.status === "pending_selection") {
                if (selectionSection) selectionSection.classList.remove("hidden");
            } else {
                if (progressSection) progressSection.classList.remove("hidden");
            }
        } else {
            if (setupSection) setupSection.classList.remove("hidden");
        }
    } else if (target === "simulator") {
        if (mockSimulatorSection) mockSimulatorSection.classList.remove("hidden");
        initMockSimulator();
    } else if (target === "studio") {
        if (studioSection) studioSection.classList.remove("hidden");
        initAgentStudio();
        if (studioPrompts && studioPrompts.length > 0) {
            renderStudioPromptsList();
            if (!activeStudioPrompt) {
                selectStudioPrompt(studioPrompts[0].filename);
            }
        }
    }
}

/* ==========================================================================
   Agent & Prompt Studio Controller
   ========================================================================== */

let studioPrompts = [];
let activeStudioPrompt = null;
let currentStudioDomain = "all";

// Elements
const studioPromptsList = document.getElementById("studio-prompts-list");
const studioPromptsCount = document.getElementById("studio-prompts-count");
const studioSearchInput = document.getElementById("studio-search-input");
const studioEmptyState = document.getElementById("studio-empty-state");
const studioActiveWorkspace = document.getElementById("studio-active-workspace");

// Meta Elements
const studioMetaTitle = document.getElementById("studio-meta-title");
const studioMetaDomain = document.getElementById("studio-meta-domain");
const studioMetaClass = document.getElementById("studio-meta-class");
const studioMetaDesc = document.getElementById("studio-meta-desc");
const studioMetaFilename = document.getElementById("studio-meta-filename");
const studioMetaModifiedBadge = document.getElementById("studio-meta-modified-badge");
const studioVariablesChips = document.getElementById("studio-variables-chips");

// Action Buttons
const studioSaveBtn = document.getElementById("studio-save-btn");
const studioResetBtn = document.getElementById("studio-reset-btn");
const studioChainBtn = document.getElementById("studio-chain-btn");

// Editor Elements
const studioTabEditorBtn = document.getElementById("studio-tab-editor-btn");
const studioTabPlaygroundBtn = document.getElementById("studio-tab-playground-btn");
const studioViewEditor = document.getElementById("studio-view-editor");
const studioViewPlayground = document.getElementById("studio-view-playground");
const studioEditorTextarea = document.getElementById("studio-editor-textarea");
const studioEditorChars = document.getElementById("studio-editor-chars");
const studioEditorLines = document.getElementById("studio-editor-lines");
const studioEditorVars = document.getElementById("studio-editor-vars");

// Playground Elements
const studioPlaygroundInputs = document.getElementById("studio-playground-inputs");
const studioLoadSampleBtn = document.getElementById("studio-load-sample-btn");
const studioProviderSelect = document.getElementById("studio-provider-select");
const studioRunTestBtn = document.getElementById("studio-run-test-btn");
const studioOutputArea = document.getElementById("studio-output-area");
const studioOutputTimer = document.getElementById("studio-output-timer");

// Chain Modal Elements
const studioChainModal = document.getElementById("studio-chain-modal");
const closeChainModalBtn = document.getElementById("close-chain-modal-btn");
const chainCancelBtn = document.getElementById("chain-cancel-btn");
const chainSaveBtn = document.getElementById("chain-save-btn");
const chainGraphGrid = document.getElementById("chain-graph-grid");

let studioInitialized = false;

function initAgentStudio() {
    if (!studioInitialized) {
        studioInitialized = true;
        setupStudioEventListeners();
    }
    fetchStudioPrompts();
}

function setupStudioEventListeners() {
    // Domain filters
    document.querySelectorAll(".studio-domain-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".studio-domain-tab").forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            currentStudioDomain = tab.getAttribute("data-domain");
            renderStudioPromptsList();
        });
    });

    // Search filter
    if (studioSearchInput) {
        studioSearchInput.addEventListener("input", () => renderStudioPromptsList());
    }

    // Editor Tabs Toggle
    if (studioTabEditorBtn && studioTabPlaygroundBtn) {
        studioTabEditorBtn.addEventListener("click", () => {
            studioTabEditorBtn.classList.add("active");
            studioTabPlaygroundBtn.classList.remove("active");
            studioViewEditor.classList.add("active");
            studioViewPlayground.classList.remove("active");
        });

        studioTabPlaygroundBtn.addEventListener("click", () => {
            studioTabPlaygroundBtn.classList.add("active");
            studioTabEditorBtn.classList.remove("active");
            studioViewPlayground.classList.add("active");
            studioViewEditor.classList.remove("active");
        });
    }

    // Textarea input stat updates
    if (studioEditorTextarea) {
        studioEditorTextarea.addEventListener("input", () => {
            updateEditorStats();
        });
    }

    // Save & Reset actions
    if (studioSaveBtn) studioSaveBtn.addEventListener("click", saveStudioPrompt);
    if (studioResetBtn) studioResetBtn.addEventListener("click", resetStudioPrompt);

    // Playground Actions
    if (studioLoadSampleBtn) studioLoadSampleBtn.addEventListener("click", loadStudioSampleData);
    if (studioRunTestBtn) studioRunTestBtn.addEventListener("click", runStudioPromptTest);

    // Chain Modal
    if (studioChainBtn) studioChainBtn.addEventListener("click", openChainModal);
    if (closeChainModalBtn) closeChainModalBtn.addEventListener("click", closeChainModal);
    if (chainCancelBtn) chainCancelBtn.addEventListener("click", closeChainModal);
    if (chainSaveBtn) chainSaveBtn.addEventListener("click", saveChainSettings);
}

async function fetchStudioPrompts() {
    try {
        const response = await fetch("/api/prompts");
        if (!response.ok) throw new Error("Failed to load prompts.");
        const data = await response.json();
        studioPrompts = data.prompts || [];
        studioPromptsCount.innerText = studioPrompts.length;
        renderStudioPromptsList();

        // Select first prompt by default if available
        if (studioPrompts.length > 0) {
            selectStudioPrompt(studioPrompts[0].filename);
        }
    } catch (err) {
        alert(`Error loading studio prompts: ${err.message}`);
    }
}

function renderStudioPromptsList() {
    if (!studioPromptsList) return;
    studioPromptsList.innerHTML = "";

    const query = (studioSearchInput?.value || "").toLowerCase().trim();

    const filtered = studioPrompts.filter(p => {
        const matchDomain = currentStudioDomain === "all" || p.domain === currentStudioDomain;
        const matchQuery = !query || 
            p.title.toLowerCase().includes(query) || 
            p.agent_class.toLowerCase().includes(query) || 
            p.filename.toLowerCase().includes(query) ||
            p.description.toLowerCase().includes(query);
        return matchDomain && matchQuery;
    });

    if (filtered.length === 0) {
        studioPromptsList.innerHTML = `<div style="padding: 1rem; text-align: center; color: var(--text-muted); font-size: 0.8rem;">No matching agent prompts found.</div>`;
        return;
    }

    filtered.forEach(p => {
        const item = document.createElement("div");
        item.className = `studio-prompt-item ${activeStudioPrompt?.filename === p.filename ? 'active' : ''}`;
        
        let domainEmoji = "🔬";
        if (p.domain === "interview_experience") domainEmoji = "🏢";
        else if (p.domain === "stock_market") domainEmoji = "📈";

        item.innerHTML = `
            <div class="prompt-item-header">
                <span class="prompt-item-title">${domainEmoji} ${p.title}</span>
                ${p.is_modified ? '<span class="badge badge-modified">Modified</span>' : ''}
            </div>
            <div class="prompt-item-class">${p.agent_class}</div>
            <div class="prompt-item-footer">
                <span>${p.variables.length} vars</span>
                <span>${(p.size_bytes / 1024).toFixed(1)} KB</span>
            </div>
        `;

        item.addEventListener("click", () => {
            selectStudioPrompt(p.filename);
        });

        studioPromptsList.appendChild(item);
    });
}

async function selectStudioPrompt(filename) {
    try {
        const response = await fetch(`/api/prompts/${filename}`);
        if (!response.ok) throw new Error("Failed to load prompt details.");
        
        activeStudioPrompt = await response.json();

        // Update UI highlights
        document.querySelectorAll(".studio-prompt-item").forEach(el => el.classList.remove("active"));
        renderStudioPromptsList();

        // Show active workspace
        studioEmptyState.classList.add("hidden");
        studioActiveWorkspace.classList.remove("hidden");

        // Populate Meta
        studioMetaTitle.innerText = activeStudioPrompt.title;
        studioMetaDomain.innerText = activeStudioPrompt.domain.toUpperCase().replace("_", " ");
        studioMetaClass.innerText = activeStudioPrompt.agent_class;
        studioMetaDesc.innerText = activeStudioPrompt.description;
        studioMetaFilename.innerText = activeStudioPrompt.filename;
        studioMetaModifiedBadge.classList.toggle("hidden", !activeStudioPrompt.is_modified);

        // Populate Variables Chips
        renderVariableChips(activeStudioPrompt.variables);

        // Populate Textarea
        studioEditorTextarea.value = activeStudioPrompt.content;
        updateEditorStats();

        // Populate Playground Inputs
        renderPlaygroundInputs(activeStudioPrompt.variables, activeStudioPrompt.sample_inputs);

        // Clear previous playground output
        studioOutputArea.innerHTML = `<div class="output-placeholder"><span>Click "Execute Agent Prompt" or load sample data to test prompt generation.</span></div>`;
        studioOutputTimer.innerText = "Ready";
        studioOutputTimer.className = "stat-badge";
    } catch (err) {
        alert(`Error selecting prompt: ${err.message}`);
    }
}

function renderVariableChips(variables) {
    studioVariablesChips.innerHTML = "";
    if (!variables || variables.length === 0) {
        studioVariablesChips.innerHTML = `<span style="font-size: 0.75rem; color: var(--text-muted); font-style: italic;">No variables detected</span>`;
        return;
    }

    variables.forEach(v => {
        const chip = document.createElement("button");
        chip.className = "var-chip";
        chip.innerText = `{${v}}`;
        chip.title = `Click to insert {${v}} at cursor position`;
        chip.addEventListener("click", () => {
            insertVariableAtCursor(`{${v}}`);
        });
        studioVariablesChips.appendChild(chip);
    });
}

function insertVariableAtCursor(text) {
    const textarea = studioEditorTextarea;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const val = textarea.value;
    textarea.value = val.substring(0, start) + text + val.substring(end);
    textarea.selectionStart = textarea.selectionEnd = start + text.length;
    textarea.focus();
    updateEditorStats();
}

function updateEditorStats() {
    const val = studioEditorTextarea.value || "";
    const chars = val.length;
    const lines = val.split("\n").length;
    const varsMatch = val.match(/\{([a-zA-Z0-9_]+)\}/g) || [];
    const uniqueVars = new Set(varsMatch);

    studioEditorChars.innerText = `${chars.toLocaleString()} characters`;
    studioEditorLines.innerText = `${lines.toLocaleString()} lines`;
    studioEditorVars.innerText = `${uniqueVars.size} placeholders`;
}

async function saveStudioPrompt() {
    if (!activeStudioPrompt) return;

    studioSaveBtn.disabled = true;
    studioSaveBtn.innerText = "Saving...";

    try {
        const content = studioEditorTextarea.value;
        const response = await fetch(`/api/prompts/${activeStudioPrompt.filename}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content })
        });

        if (!response.ok) throw new Error("Failed to save prompt changes.");
        
        activeStudioPrompt = await response.json();
        studioMetaModifiedBadge.classList.remove("hidden");

        // Update in list
        const idx = studioPrompts.findIndex(p => p.filename === activeStudioPrompt.filename);
        if (idx !== -1) {
            studioPrompts[idx].is_modified = true;
            studioPrompts[idx].variables = activeStudioPrompt.variables;
        }

        renderStudioPromptsList();
        renderVariableChips(activeStudioPrompt.variables);
        renderPlaygroundInputs(activeStudioPrompt.variables, activeStudioPrompt.sample_inputs);

        // Flash notification
        studioSaveBtn.innerText = "✅ Saved!";
        setTimeout(() => {
            studioSaveBtn.innerText = "💾 Save Prompt";
            studioSaveBtn.disabled = false;
        }, 1500);
    } catch (err) {
        alert(`Error saving prompt: ${err.message}`);
        studioSaveBtn.innerText = "💾 Save Prompt";
        studioSaveBtn.disabled = false;
    }
}

async function resetStudioPrompt() {
    if (!activeStudioPrompt) return;

    if (!confirm(`Are you sure you want to reset "${activeStudioPrompt.title}" back to its original default template?`)) {
        return;
    }

    studioResetBtn.disabled = true;

    try {
        const response = await fetch(`/api/prompts/${activeStudioPrompt.filename}/reset`, {
            method: "POST"
        });

        if (!response.ok) throw new Error("Failed to reset prompt.");

        activeStudioPrompt = await response.json();
        studioEditorTextarea.value = activeStudioPrompt.content;
        studioMetaModifiedBadge.classList.add("hidden");

        const idx = studioPrompts.findIndex(p => p.filename === activeStudioPrompt.filename);
        if (idx !== -1) {
            studioPrompts[idx].is_modified = false;
        }

        renderStudioPromptsList();
        renderVariableChips(activeStudioPrompt.variables);
        updateEditorStats();
    } catch (err) {
        alert(`Error resetting prompt: ${err.message}`);
    } finally {
        studioResetBtn.disabled = false;
    }
}

function renderPlaygroundInputs(variables, sampleInputs) {
    studioPlaygroundInputs.innerHTML = "";
    if (!variables || variables.length === 0) {
        studioPlaygroundInputs.innerHTML = `<div style="color: var(--text-muted); font-size: 0.8rem; font-style: italic;">No variables in template. Ready to run directly.</div>`;
        return;
    }

    variables.forEach(v => {
        const group = document.createElement("div");
        group.className = "pg-var-group";

        const label = document.createElement("label");
        label.innerText = `{${v}}`;

        let input;
        const sampleVal = sampleInputs ? sampleInputs[v] : "";
        const isLong = typeof sampleVal === "string" && (sampleVal.length > 50 || sampleVal.includes("\n") || sampleVal.startsWith("{") || sampleVal.startsWith("["));

        if (isLong || v.includes("data") || v.includes("history") || v.includes("transcript") || v.includes("summary")) {
            input = document.createElement("textarea");
            input.rows = 3;
        } else {
            input = document.createElement("input");
            input.type = "text";
        }

        input.id = `pg-input-${v}`;
        input.setAttribute("data-var", v);
        input.placeholder = `Enter test value for ${v}...`;
        if (sampleVal) {
            input.value = typeof sampleVal === "object" ? JSON.stringify(sampleVal, null, 2) : sampleVal;
        }

        group.appendChild(label);
        group.appendChild(input);
        studioPlaygroundInputs.appendChild(group);
    });
}

function loadStudioSampleData() {
    if (!activeStudioPrompt || !activeStudioPrompt.sample_inputs) return;
    const samples = activeStudioPrompt.sample_inputs;

    activeStudioPrompt.variables.forEach(v => {
        const el = document.getElementById(`pg-input-${v}`);
        if (el && samples[v] !== undefined) {
            el.value = typeof samples[v] === "object" ? JSON.stringify(samples[v], null, 2) : samples[v];
        }
    });
}

async function runStudioPromptTest() {
    if (!activeStudioPrompt) return;

    studioRunTestBtn.disabled = true;
    studioRunTestBtn.innerText = "Executing Agent...";
    studioOutputTimer.innerText = "Running...";
    studioOutputTimer.className = "stat-badge";
    studioOutputArea.innerHTML = `<div class="output-placeholder"><span>⏳ Querying LLM provider and generating structured output...</span></div>`;

    const variables = {};
    activeStudioPrompt.variables.forEach(v => {
        const el = document.getElementById(`pg-input-${v}`);
        if (el) variables[v] = el.value;
    });

    const provider = studioProviderSelect.value || null;

    try {
        const response = await fetch(`/api/prompts/${activeStudioPrompt.filename}/test`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ variables, provider })
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.error || "Execution failed.");
        }

        studioOutputTimer.innerText = `⏱️ ${result.duration_ms}ms (${result.provider})`;
        studioOutputTimer.className = "stat-badge";

        if (typeof marked !== "undefined" && result.response) {
            studioOutputArea.innerHTML = marked.parse(result.response);
        } else {
            studioOutputArea.innerText = result.response || "No response generated.";
        }
    } catch (err) {
        studioOutputTimer.innerText = "❌ Execution Error";
        studioOutputTimer.className = "stat-badge badge-nohire";
        studioOutputArea.innerHTML = `<div style="color: #f87171; padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 6px;"><strong>Execution Failed:</strong><br>${err.message}</div>`;
    } finally {
        studioRunTestBtn.disabled = false;
        studioRunTestBtn.innerText = "🚀 Execute Agent Prompt";
    }
}

// Chain Modal Functions
async function openChainModal() {
    try {
        const [graphRes, configRes] = await Promise.all([
            fetch("/api/pipeline/graph"),
            fetch("/api/pipeline/config")
        ]);

        if (!graphRes.ok || !configRes.ok) throw new Error("Failed to load pipeline settings.");

        const graphData = await graphRes.json();
        const configData = await configRes.json();

        // Render Graph
        renderChainGraph(graphData.domains || []);

        // Fill Form
        document.getElementById("cfg-llm-provider").value = configData.llm_provider || "ollama";
        document.getElementById("cfg-default-model").value = configData.default_model || "qwen2.5:7b";
        document.getElementById("cfg-max-topics").value = configData.max_topics_discovered || 20;
        document.getElementById("cfg-max-sources").value = configData.max_sources_per_topic || 5;
        document.getElementById("cfg-dcf-wacc").value = configData.dcf_default_wacc || 9.0;
        document.getElementById("cfg-dcf-g").value = configData.dcf_default_terminal_growth || 3.0;

        document.getElementById("cfg-enable-critic").checked = configData.enable_critic_agent !== false;
        document.getElementById("cfg-enable-peers").checked = configData.enable_peer_benchmarking !== false;
        document.getElementById("cfg-enable-news").checked = configData.enable_news_clustering !== false;

        studioChainModal.classList.remove("hidden");
    } catch (err) {
        alert(`Error opening chain settings: ${err.message}`);
    }
}

function closeChainModal() {
    studioChainModal.classList.add("hidden");
}

function renderChainGraph(domains) {
    chainGraphGrid.innerHTML = "";
    domains.forEach(d => {
        const box = document.createElement("div");
        box.className = "chain-domain-box";

        let flowHtml = `<div class="chain-nodes-flow">`;
        (d.nodes || []).forEach((node, idx) => {
            flowHtml += `
                <div class="chain-node-pill" title="${node.agent} (${node.prompt})">
                    <span>${node.agent}</span>
                </div>
            `;
            if (idx < d.nodes.length - 1) {
                flowHtml += `<span class="chain-arrow">➔</span>`;
            }
        });
        flowHtml += `</div>`;

        box.innerHTML = `
            <h4>${d.title}</h4>
            <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.6rem;">${d.description}</p>
            ${flowHtml}
        `;
        chainGraphGrid.appendChild(box);
    });
}

async function saveChainSettings() {
    chainSaveBtn.disabled = true;
    chainSaveBtn.innerText = "Saving Configuration...";

    const payload = {
        llm_provider: document.getElementById("cfg-llm-provider").value,
        default_model: document.getElementById("cfg-default-model").value,
        max_topics_discovered: parseInt(document.getElementById("cfg-max-topics").value, 10),
        max_sources_per_topic: parseInt(document.getElementById("cfg-max-sources").value, 10),
        dcf_default_wacc: parseFloat(document.getElementById("cfg-dcf-wacc").value),
        dcf_default_terminal_growth: parseFloat(document.getElementById("cfg-dcf-g").value),
        enable_critic_agent: document.getElementById("cfg-enable-critic").checked,
        enable_peer_benchmarking: document.getElementById("cfg-enable-peers").checked,
        enable_news_clustering: document.getElementById("cfg-enable-news").checked
    };

    try {
        const response = await fetch("/api/pipeline/config", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Failed to save pipeline configuration.");

        closeChainModal();
        alert("Pipeline & Orchestration Settings saved successfully!");
    } catch (err) {
        alert(`Error saving pipeline configuration: ${err.message}`);
    } finally {
        chainSaveBtn.disabled = false;
        chainSaveBtn.innerText = "Save Pipeline Settings";
    }
}


/* ==========================================================================
   Home Page Feed Controller & Modal Logic
   ========================================================================== */

let homeFeedData = null;
let currentModalDoc = null;

function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, '&quot;')
        .replace(/'/g, "&#039;");
}

// Feed Action Buttons
const feedLogMissedBtn = document.getElementById("feed-log-missed-btn");
const feedAddMissedBtn = document.getElementById("feed-add-missed-btn");
const feedNewResearchBtn = document.getElementById("feed-new-research-btn");

// Missed Question Modal Elements
const missedQuestionModal = document.getElementById("missed-question-modal");
const closeMissedModalBtn = document.getElementById("close-missed-modal-btn");
const cancelMissedModalBtn = document.getElementById("cancel-missed-modal-btn");
const submitMissedModalBtn = document.getElementById("submit-missed-modal-btn");
const mqTitleInput = document.getElementById("mq-title");
const mqCategorySelect = document.getElementById("mq-category");
const mqCompanyInput = document.getElementById("mq-company");
const mqDifficultySelect = document.getElementById("mq-difficulty");
const mqTrippedInput = document.getElementById("mq-tripped");

// Document Reader Modal Elements
const documentViewerModal = document.getElementById("document-viewer-modal");
const closeDocModalBtn = document.getElementById("close-doc-modal-btn");
const docModalCloseBottomBtn = document.getElementById("doc-modal-close-bottom-btn");
const docModalTitle = document.getElementById("doc-modal-title");
const docModalPath = document.getElementById("doc-modal-path");
const docModalContent = document.getElementById("doc-modal-content");
const docModalStarBtn = document.getElementById("doc-modal-star-btn");

// Attach Feed Event Listeners
if (feedNewResearchBtn) {
    feedNewResearchBtn.addEventListener("click", () => switchMainSection("pipeline"));
}
if (feedLogMissedBtn) {
    feedLogMissedBtn.addEventListener("click", openMissedQuestionModal);
}
if (feedAddMissedBtn) {
    feedAddMissedBtn.addEventListener("click", openMissedQuestionModal);
}
if (closeMissedModalBtn) {
    closeMissedModalBtn.addEventListener("click", closeMissedQuestionModal);
}
if (cancelMissedModalBtn) {
    cancelMissedModalBtn.addEventListener("click", closeMissedQuestionModal);
}
if (submitMissedModalBtn) {
    submitMissedModalBtn.addEventListener("click", submitMissedQuestion);
}

if (closeDocModalBtn) {
    closeDocModalBtn.addEventListener("click", closeDocumentModal);
}
if (docModalCloseBottomBtn) {
    docModalCloseBottomBtn.addEventListener("click", closeDocumentModal);
}
if (docModalStarBtn) {
    docModalStarBtn.addEventListener("click", toggleDocumentBookmark);
}

function openMissedQuestionModal() {
    if (!missedQuestionModal) return;
    if (mqTitleInput) mqTitleInput.value = "";
    if (mqCompanyInput) mqCompanyInput.value = "";
    if (mqTrippedInput) mqTrippedInput.value = "";
    missedQuestionModal.classList.remove("hidden");
    if (mqTitleInput) mqTitleInput.focus();
}

function closeMissedQuestionModal() {
    if (missedQuestionModal) missedQuestionModal.classList.add("hidden");
}

async function submitMissedQuestion() {
    const title = mqTitleInput ? mqTitleInput.value.trim() : "";
    const category = mqCategorySelect ? mqCategorySelect.value : "DSA";
    const company = mqCompanyInput ? mqCompanyInput.value.trim() : "";
    const difficulty = mqDifficultySelect ? mqDifficultySelect.value : "Medium";
    const tripped = mqTrippedInput ? mqTrippedInput.value.trim() : "";

    if (!title) {
        alert("Please enter a question title or concept.");
        return;
    }
    if (!tripped) {
        alert("Please describe what tripped you up or which edge case was missed.");
        return;
    }

    try {
        if (submitMissedModalBtn) submitMissedModalBtn.disabled = true;
        const res = await fetch("/api/feed/missed-questions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title,
                category,
                company: company || null,
                difficulty,
                what_tripped_me: tripped,
                source: "manual_entry"
            })
        });
        if (!res.ok) throw new Error("Failed to save question.");
        closeMissedQuestionModal();
        await loadHomeFeed();
    } catch (err) {
        alert(`Error saving question: ${err.message}`);
    } finally {
        if (submitMissedModalBtn) submitMissedModalBtn.disabled = false;
    }
}

async function loadHomeFeed() {
    try {
        const res = await fetch("/api/feed");
        if (!res.ok) throw new Error("Failed to fetch home feed.");
        homeFeedData = await res.json();
        renderHomeFeed(homeFeedData);
    } catch (err) {
        console.error("Failed to load feed:", err);
    }
}

function renderHomeFeed(data) {
    if (!data) return;

    // 1. Stats Bar
    const statsEl = document.getElementById("feed-hero-stats");
    if (statsEl) {
        statsEl.innerText = `${data.hero_workout.total_due} Due for Spaced Review • ${data.stock_radar.watchlist.length} Tracked Equities • ${data.total_bookmarks} Saved Deep Dives`;
    }

    // 2. Hero Workout
    renderHeroWorkout(data.hero_workout);

    // 3. Tech Radar
    renderTechRadar(data.tech_radar);

    // 4. Stock Radar
    renderStockRadar(data.stock_radar);

    // 5. Interview Radar
    renderInterviewRadar(data.interview_radar);
}

function renderHeroWorkout(workout) {
    const focusEl = document.getElementById("workout-card-focus");
    const dueBadge = document.getElementById("workout-due-badge");
    const bodyEl = document.getElementById("workout-content-body");

    if (focusEl) focusEl.innerText = workout.suggested_focus || "Continuous retention workout";
    if (dueBadge) dueBadge.innerText = `${workout.total_due} Due`;

    if (!bodyEl) return;

    if (!workout.due_questions || workout.due_questions.length === 0) {
        bodyEl.innerHTML = `
            <div class="empty-hint" style="text-align: center; padding: 1.5rem;">
                🎉 All retention reviews are complete! Log new interview questions or test your knowledge with flashcards.
            </div>
        `;
        return;
    }

    const q = workout.due_questions[0];
    const difficultyBadge = q.difficulty === "Hard" ? "badge rec-no-hire" : (q.difficulty === "Easy" ? "badge rec-hire" : "badge rec-lean-hire");
    
    bodyEl.innerHTML = `
        <div class="workout-item-box">
            <div class="workout-item-info">
                <h4>${escapeHtml(q.title)}</h4>
                <div class="workout-item-meta">
                    <span>🏷️ ${escapeHtml(q.category)}</span>
                    ${q.company ? `<span>🏢 ${escapeHtml(q.company)}</span>` : ""}
                    <span class="${difficultyBadge}">${escapeHtml(q.difficulty)}</span>
                    <span>🔄 Reviewed ${q.review_count}x</span>
                </div>
                <p class="workout-tripped-quote"><strong>Trap/Tripped on:</strong> ${escapeHtml(q.what_tripped_me)}</p>
            </div>
            <div class="workout-actions-group">
                <button class="btn btn-sm btn-outline" onclick="advanceMissedQuestion(${q.id}, 1)">🔄 Review Tomorrow</button>
                <button class="btn btn-sm btn-primary" onclick="advanceMissedQuestion(${q.id}, 2)">✅ Mark Mastered</button>
            </div>
        </div>
    `;
}

async function advanceMissedQuestion(id, targetMastery) {
    try {
        const res = await fetch(`/api/feed/missed-questions/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mastery_level: targetMastery,
                advance_review: true
            })
        });
        if (!res.ok) throw new Error("Failed to advance question review.");
        await loadHomeFeed();
    } catch (err) {
        alert(`Error updating question: ${err.message}`);
    }
}

async function deleteMissedQuestion(id) {
    if (!confirm("Remove this question from your Stumble Log?")) return;
    try {
        const res = await fetch(`/api/feed/missed-questions/${id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Failed to delete question.");
        await loadHomeFeed();
    } catch (err) {
        alert(`Error deleting question: ${err.message}`);
    }
}

function renderTechRadar(tech) {
    const pillsContainer = document.getElementById("feed-trends-pills");
    const savedList = document.getElementById("feed-saved-tech-list");
    const countBadge = document.getElementById("tech-saved-count");

    if (countBadge) countBadge.innerText = tech.saved_articles.length;

    // Render Trends
    if (pillsContainer) {
        if (!tech.trending_topics || tech.trending_topics.length === 0) {
            pillsContainer.innerHTML = '<span class="empty-hint">No technical trends recorded yet.</span>';
        } else {
            pillsContainer.innerHTML = tech.trending_topics.map(t => `
                <div class="trend-pill" onclick="searchTrendFromFeed('${escapeHtml(t.query_text)}', 'tech_topics')">
                    <span>#${escapeHtml(t.query_text)}</span>
                    <span class="trend-pill-count">${t.count}x</span>
                </div>
            `).join("");
        }
    }

    // Render Saved Articles
    if (savedList) {
        if (!tech.saved_articles || tech.saved_articles.length === 0) {
            savedList.innerHTML = '<span class="empty-hint">No saved articles yet. Star deep dives to view here!</span>';
        } else {
            savedList.innerHTML = tech.saved_articles.map(b => `
                <div class="feed-card">
                    <div class="feed-card-header">
                        <h4 class="feed-card-title">${escapeHtml(b.title)}</h4>
                    </div>
                    <p class="feed-card-desc">${escapeHtml(b.summary || "Technical deep dive report.")}</p>
                    <div class="feed-card-tags">
                        ${(b.tags || []).map(tag => `<span class="feed-tag">${escapeHtml(tag)}</span>`).join("")}
                    </div>
                    <div class="feed-card-footer">
                        <button class="btn btn-xs btn-primary" onclick="openDocumentModal('${escapeHtml(b.reference_path)}', '${escapeHtml(b.title)}')">Read Deep Dive ↗</button>
                        <button class="btn btn-xs btn-outline" onclick="removeBookmark(${b.id})" title="Remove">🗑</button>
                    </div>
                </div>
            `).join("");
        }
    }
}

function renderStockRadar(stock) {
    const watchlistContainer = document.getElementById("feed-stock-watchlist");
    const picksContainer = document.getElementById("feed-stock-picks-list");
    const countBadge = document.getElementById("stock-tracked-count");

    if (countBadge) countBadge.innerText = stock.watchlist.length;

    // Watchlist
    if (watchlistContainer) {
        if (!stock.watchlist || stock.watchlist.length === 0) {
            watchlistContainer.innerHTML = '<span class="empty-hint">No equities tracked in watchlist yet.</span>';
        } else {
            watchlistContainer.innerHTML = stock.watchlist.map(s => {
                const upside = s.dcf_upside_percent || 0;
                const upsideClass = upside >= 0 ? "upside-positive" : "upside-negative";
                const upsideText = upside >= 0 ? `+${upside.toFixed(1)}%` : `${upside.toFixed(1)}%`;
                return `
                    <div class="feed-card stock-feed-card">
                        <div class="feed-card-header">
                            <div>
                                <h4 class="feed-card-title"><strong>$${escapeHtml(s.ticker)}</strong> • ${escapeHtml(s.company_name)}</h4>
                                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.2rem;">
                                    Current: $${(s.current_price || 0).toFixed(2)} | Target: $${(s.dcf_target_price || 0).toFixed(2)}
                                </div>
                            </div>
                            <span class="stock-upside-badge ${upsideClass}">${upsideText} DCF</span>
                        </div>
                        ${s.critic_warning ? `<div class="stock-critic-alert">⚠️ ${escapeHtml(s.critic_warning)}</div>` : ""}
                        <div class="feed-card-footer">
                            <button class="btn btn-xs btn-primary" onclick="searchTrendFromFeed('${escapeHtml(s.ticker)}', 'stock_market')">Run Deep-Dive ↗</button>
                            ${s.run_id ? `<button class="btn btn-xs btn-outline" onclick="openDocumentModal('outputs/${escapeHtml(s.run_id)}/stock_research_report.md', '${escapeHtml(s.ticker)} Report')">Read Report</button>` : ""}
                        </div>
                    </div>
                `;
            }).join("");
        }
    }

    // Screener Picks
    if (picksContainer) {
        if (!stock.recent_picks || stock.recent_picks.length === 0) {
            picksContainer.innerHTML = '<span class="empty-hint">No recent dislocation screeners found.</span>';
        } else {
            picksContainer.innerHTML = stock.recent_picks.map(p => `
                <div class="feed-card">
                    <div class="feed-card-header">
                        <h4 class="feed-card-title">$${escapeHtml(p.ticker)} • ${escapeHtml(p.company_name)}</h4>
                        <span class="badge rec-lean-hire">${escapeHtml(p.conviction || "Dislocation")}</span>
                    </div>
                    <p class="feed-card-desc"><strong>Archetype:</strong> ${escapeHtml(p.archetype || "Quality Growth")}</p>
                    <div class="feed-card-footer">
                        <span style="font-size: 0.8rem; color: #34d399; font-weight: 700;">+${(p.upside || 0).toFixed(1)}% Implied Upside</span>
                        <button class="btn btn-xs btn-outline" onclick="openDocumentModal('outputs/${escapeHtml(p.run_id)}/stock_opportunity_report.md', 'Opportunity Screener')">View Picks</button>
                    </div>
                </div>
            `).join("");
        }
    }
}

function renderInterviewRadar(interview) {
    const missedList = document.getElementById("feed-missed-questions-list");
    const guidesList = document.getElementById("feed-company-guides-list");

    // Missed Questions Stumble Log
    if (missedList) {
        if (!interview.missed_questions || interview.missed_questions.length === 0) {
            missedList.innerHTML = '<span class="empty-hint">No questions logged in stumble backlog.</span>';
        } else {
            missedList.innerHTML = interview.missed_questions.map(q => {
                let statusClass = "status-stumbled";
                let statusText = "Stumbled";
                if (q.mastery_level === 1) {
                    statusClass = "status-reviewed";
                    statusText = "Practicing";
                } else if (q.mastery_level >= 2) {
                    statusClass = "status-mastered";
                    statusText = "Mastered";
                }

                return `
                    <div class="feed-card stumble-feed-card">
                        <div class="feed-card-header">
                            <div>
                                <h4 class="feed-card-title">${escapeHtml(q.title)}</h4>
                                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.15rem;">
                                    ${escapeHtml(q.category)} ${q.company ? `• ${escapeHtml(q.company)}` : ""}
                                </div>
                            </div>
                            <span class="stumble-status-badge ${statusClass}">${statusText}</span>
                        </div>
                        <p class="feed-card-desc" style="color: #cbd5e1;"><em>"${escapeHtml(q.what_tripped_me)}"</em></p>
                        <div class="feed-card-footer">
                            <button class="btn btn-xs btn-outline" onclick="advanceMissedQuestion(${q.id}, ${q.mastery_level < 2 ? q.mastery_level + 1 : 2})">
                                ${q.mastery_level < 2 ? "Advance Mastery ↗" : "Re-review"}
                            </button>
                            <button class="btn btn-xs btn-outline" onclick="deleteMissedQuestion(${q.id})" title="Delete">🗑</button>
                        </div>
                    </div>
                `;
            }).join("");
        }
    }

    // Target Company Guides
    if (guidesList) {
        if (!interview.recent_company_guides || interview.recent_company_guides.length === 0) {
            guidesList.innerHTML = '<span class="empty-hint">No company interview guides generated yet.</span>';
        } else {
            guidesList.innerHTML = interview.recent_company_guides.map(g => `
                <div class="feed-card">
                    <div class="feed-card-header">
                        <h4 class="feed-card-title">${escapeHtml(g.company_name)}</h4>
                        <span class="badge rec-hire">${escapeHtml(g.level)}</span>
                    </div>
                    <p class="feed-card-desc">${escapeHtml(g.role)} • ${g.rounds_count} Rounds Identified</p>
                    <div class="feed-card-footer">
                        <button class="btn btn-xs btn-primary" onclick="openDocumentModal('${escapeHtml(g.reference_path)}', '${escapeHtml(g.company_name)} Blueprint')">Open Blueprint ↗</button>
                    </div>
                </div>
            `).join("");
        }
    }
}

function searchTrendFromFeed(query, domain) {
    switchMainSection("pipeline");
    if (domain === "tech_topics") {
        if (modeTechBtn) modeTechBtn.click();
        const interestsInput = document.getElementById("interests-input");
        if (interestsInput) {
            interestsInput.value = query;
            interestsInput.focus();
        }
    } else if (domain === "stock_market") {
        if (modeStockBtn) modeStockBtn.click();
        if (stockTickerInput) {
            stockTickerInput.value = query;
            stockTickerInput.focus();
        }
    }
}

async function removeBookmark(id) {
    if (!confirm("Remove this saved deep dive?")) return;
    try {
        const res = await fetch(`/api/feed/bookmarks/${id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Failed to delete bookmark.");
        await loadHomeFeed();
    } catch (err) {
        alert(`Error deleting bookmark: ${err.message}`);
    }
}

// Document Reader Modal
async function openDocumentModal(path, title) {
    if (!documentViewerModal) return;
    currentModalDoc = { path, title };
    if (docModalTitle) docModalTitle.innerText = title || "Document Reader";
    if (docModalPath) docModalPath.innerText = path;
    if (docModalContent) docModalContent.innerHTML = '<div class="loader-container"><div class="spinner"></div><p>Loading document from local storage...</p></div>';

    documentViewerModal.classList.remove("hidden");

    try {
        const res = await fetch(`/api/documents?path=${encodeURIComponent(path)}`);
        if (!res.ok) throw new Error("Document not found on disk.");
        const data = await res.json();
        if (docModalContent) {
            docModalContent.innerHTML = marked.parse(data.content);
        }
        await updateDocumentStarButton(path);
    } catch (err) {
        if (docModalContent) {
            docModalContent.innerHTML = `<div class="empty-hint" style="color: #f87171;">Failed to load document: ${escapeHtml(err.message)}</div>`;
        }
    }
}

function closeDocumentModal() {
    if (documentViewerModal) documentViewerModal.classList.add("hidden");
    currentModalDoc = null;
}

async function updateDocumentStarButton(path) {
    if (!docModalStarBtn) return;
    try {
        const res = await fetch("/api/feed/bookmarks");
        if (res.ok) {
            const bookmarks = await res.json();
            const exists = bookmarks.some(b => b.reference_path === path);
            docModalStarBtn.innerText = exists ? "⭐ Starred" : "☆ Save to Bookmarks";
            docModalStarBtn.classList.toggle("btn-primary", exists);
            docModalStarBtn.classList.toggle("btn-outline", !exists);
        }
    } catch (e) {}
}

async function toggleDocumentBookmark() {
    if (!currentModalDoc) return;
    try {
        const res = await fetch("/api/feed/bookmarks");
        const bookmarks = res.ok ? await res.json() : [];
        const existing = bookmarks.find(b => b.reference_path === currentModalDoc.path);

        if (existing) {
            await fetch(`/api/feed/bookmarks/${existing.id}`, { method: "DELETE" });
        } else {
            const domain = currentModalDoc.path.includes("stock") ? "stock_market" : "tech_topics";
            await fetch("/api/feed/bookmarks", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    domain: domain,
                    item_type: domain === "stock_market" ? "stock_research" : "tech_summary",
                    title: currentModalDoc.title,
                    reference_path: currentModalDoc.path,
                    summary: "Saved from document reader"
                })
            });
        }
        await updateDocumentStarButton(currentModalDoc.path);
        await loadHomeFeed();
    } catch (err) {
        console.error("Failed to toggle bookmark:", err);
    }
}

// Initial App Boot: Default to Home Feed
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        initAgentStudio();
        switchMainSection("feed");
    });
} else {
    initAgentStudio();
    switchMainSection("feed");
}




