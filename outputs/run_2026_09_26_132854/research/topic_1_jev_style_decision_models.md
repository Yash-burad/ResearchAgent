# Research Notes: Jev-Style Decision Models

## Definition
Jev-style decision models (also categorized as System One models developed by TypeSafe AI) are a class of transformer-based frontier AI models that eschew text generation/string output entirely, instead evaluating unstructured state against typed questions to produce probabilities, confidence scores, and calibrated structured decisions directly usable by software.

## Why It Matters
- Addresses the limitation that traditional LLMs optimize for human language rather than direct computer automation, which causes them to be slow, expensive, and prone to hallucinations.
- Makes AI integration significantly cheaper and faster (up to 40x-200x faster and 400x lower cost than comparable LLMs on classification tasks).
- Output tokens are effectively free, and input tokens are metered at a much lower cost per billion.
- Brings native epistemic honesty and calibrated probabilities to every output, enabling applications to safely branch logic based on concrete confidence scores.

## Technical Details
- Built with a new model architecture, a parallel sampler for maximum efficiency, and a training methodology known as Reinforcement Learning for Calibrated Decisions (RLCD).
- Unlike traditional autoregressive LLMs that generate one token sequentially, Jev uses parallel sampling to generate all requested outputs in a single query.
- Takes unstructured state (e.g., text, sequential messages) as input along with typed questions, evaluating every question in parallel and in isolation against the same state.
- Supports three core primitives: Choice (pick from a set of options with probabilities), Score (rate an input against ordered levels with a continuous score and distribution), and Noul (yes-or-no question returning the probability a statement is true).
- Output tokens are typed structured values rather than raw text strings, completely eliminating hallucinations in text generation since strings are not generated.

## Use Cases
- Reviewing and classifying commands or support tickets for safety, urgency, and categorization (e.g., Vercel's ticket classification and safety checks).
- Classifying business emails and filtering workflows automatically based on real probabilities and confidence scores.
- Monitoring LLM agent traces and preventing jailbreaks or acting as a smart safety check on LLM misbehavior.
- Real-time model routing to predict whether a given workload requires a specific model without incurring heavy LLM invocation costs.

## Code or Practical Examples
- API Request Example:
{
  "model": "jev-latest",
  "state": "Hi, I've been trying to connect my Stripe account for 3 days and it keeps failing. I'm losing sales. Please help ASAP.",
  "questions": {
    "is_urgent": {
      "type": "noul",
      "instructions": "The message conveys urgency or time-sensitivity"
    }
  }
}

Response Example:
{
  "is_urgent": {
    "type": "noul",
    "noul": 0.999
  }
}

## Limitations & Drawbacks
- Does not generate text, chat responses, or arbitrary strings; it is strictly optimized for structured outputs and typed decisions.
- Delegates the handling of uncertainty to the user application; developers must explicitly define thresholds (e.g., deciding whether a 50% vs 95% probability warrants action).
- Tasks requiring extended reasoning or weighing multiple independent factors must be decomposed into atomic questions in code rather than handled via a single open-ended prompt.

## Related Topics
- System One Models
- Reinforcement Learning for Calibrated Decisions (RLCD)
- TypeSafe AI
- Agentic Infrastructure
- Model Routing
- Structured Outputs

## Sources & References
1. [Jev-Style Decision Models](https://techcrunch.com/2026/09/18/a-new-kind-of-ai-model-from-a-chatgpt-inventor-is-thrilling-developers/) (TechCrunch)
   - **Retrieved at**: 2026-09-18
   - **Credibility Score**: 6/10
   - **Key Points**:
     - Created by Diogo Almeida, an ex-OpenAI researcher and co-inventor of RLHF, through his startup TypeSafe AI.
     - Model is named after 19th-century economist William Stanley Jevons.
     - Produces calibrated decisions and probabilities instead of outputting human language text.
     - Delivers results 5 to 18 times more quickly with greater accuracy than LLMs in classification tests (e.g., Vercel's use case).
     - Provides real probability confidence scores useful for automation and workflow routing.
2. [Introducing System One Models & Jev - TypeSafe AI Blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev) (TypeSafe AI)
   - **Retrieved at**: 2026-09-18
   - **Credibility Score**: 5/10
   - **Key Points**:
     - Introduces System One Models built to make fast, structured decisions for software.
     - Trained using Reinforcement Learning for Calibrated Decisions (RLCD).
     - Uses parallel sampling to generate all outputs in a single query.
     - Input tokens cost $0.042 / MTok, while output tokens are free.
     - End-to-end response time ranges from 70ms to 500ms.
3. [Introduction - TypeSafe AI](https://docs.typesafe.ai/introduction) (TypeSafe AI)
   - **Retrieved at**: 2026-09-18
   - **Credibility Score**: 5/10
   - **Key Points**:
     - Jev evaluates typed questions against a state and returns structured results directly without text generation or parsing.
     - Exposes three AI primitives: Choice, Score, and Noul.
     - Evaluates every question in parallel and in isolation against the same state in one go.
     - Complex goals require decomposing questions into atomic queries and combining results with code logic.
4. [What Is Jev? A Guide to TypeSafe AI’s System One Model](https://www.langchain.com/blog/building-a-harness-with-jev) (LangChain)
   - **Retrieved at**: 2026-09-18
   - **Credibility Score**: 5/10
   - **Key Points**:
     - Integrates into agent loops to replace costly and slow full chat LLM calls for intermediate decisions.
     - Reports up to 200x faster inference and 400x lower cost than comparable LLMs on classification tasks.
     - Provides concrete examples of request bodies featuring states and typed questions such as Noul for binary determinations.
