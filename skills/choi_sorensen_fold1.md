# Yejin Choi and Taylor Sorensen Abstract Style Skill

You are writing a research paper abstract in the collaborative style of Yejin Choi and Taylor Sorensen.
Study the style fingerprint and examples carefully, then generate an abstract that sounds like it was co-authored by both of them.
Do NOT copy content from the examples — reproduce the STYLE (structure, vocabulary, framing, normative stance), not the subject matter.

## Style Fingerprint

1. **Opening patterns** — Yejin Choi and Taylor Sorensen often open with a broad contextual statement about the significance or urgency of the topic, followed by a specific problem statement. This pattern sets the stage by highlighting the importance of the issue before narrowing down to the specific research focus. 

   - Example 1: "With increased power and prevalence of AI systems, it is ever more critical that AI systems are designed to serve all, i.e., people with diverse values and perspectives."
   - Example 2: "Language model post-training has enhanced instruction-following and performance on many downstream tasks, but also comes with an often-overlooked cost on tasks with many possible valid answers."

   **Pattern Name:** Contextual Significance to Specific Problem.

2. **Problem framing** — They frame the AI alignment and personalization challenge by emphasizing diversity, pluralism, and the limitations of current methods. Specific phrases or templates they reuse include:

   - "Aligning models to serve pluralistic human values remains an open research question."
   - "Models must cover an entire distribution of outputs, rather than a single correct answer."
   - "Current alignment techniques may be fundamentally limited for pluralistic AI."

3. **Methodology description** — They describe their approach using specific verbs and sentence templates that emphasize formalization, evaluation, and improvement. Structural choices often include listing key components or steps in their methodology.

   - Verbs: "propose," "identify and formalize," "characterize," "introduce."
   - Sentence Templates: "We propose a roadmap to...", "We identify and formalize three possible ways...", "We introduce SPECTRUM SUITE, a large-scale resource..."

4. **Claims and hedging** — In position papers, they make assertive claims about the limitations of current methods and the necessity of their proposed frameworks. In empirical papers, they present results with a balance of confidence and acknowledgment of ongoing challenges.

   - Position Papers: "Current alignment techniques may be fundamentally limited for pluralistic AI."
   - Empirical Papers: "We find that while current post-training techniques elicit underlying capabilities and knowledge, they hurt models’ ability to flexibly steer in-context."

5. **MOST IMPORTANT — unique fingerprint mechanisms**

   - **Normative Language:** They frequently use normative language to emphasize the ethical and societal implications of AI alignment. 
     - Quotes: "It is ever more critical that AI systems are designed to serve all," "aligning models to serve pluralistic human values."
     - Effect: This language underscores the moral imperative of their research focus, distinguishing it from more technical or capability-focused work.

   - **Pluralism Vocabulary:** Their abstracts are rich with vocabulary related to pluralism and diversity, which is central to their research theme.
     - Quotes: "pluralistic alignment," "Overton pluralistic models," "distributional pluralism."
     - Effect: This vocabulary reinforces their focus on accommodating diverse human values and perspectives within AI systems.

   - **Rhetorical Strategies Specific to Alignment Position Papers:** They use rhetorical strategies that highlight the limitations of existing methods and the need for new frameworks.
     - Quotes: "highlight empirical evidence," "motivating the need for further research."
     - Effect: These strategies create a sense of urgency and necessity for their proposed solutions.

   - **Stance on AI Values:** They explicitly address the alignment of AI systems with human values, often critiquing current methods.
     - Quotes: "serve pluralistic human values," "reduce distributional pluralism in models."
     - Effect: This stance positions their work as a critical examination of how AI systems can better reflect human diversity.

6. **What this collaboration avoids** — Choi and Sorensen's style avoids overly technical jargon without context, purely capability-focused language, and neglecting the ethical implications of AI alignment. They do not use constructions that ignore the societal impact of AI, nor do they focus solely on technical performance without addressing broader value alignment issues.

## Positive Examples (co-authored by Yejin Choi + Taylor Sorensen)

### Position: A Roadmap to Pluralistic Alignment (2024)
With increased power and prevalence of AI systems, it is ever more critical that AI systems are designed to serve all, i.e., people with diverse values and perspectives. However, aligning models to serve pluralistic human values remains an open research question. In this piece, we propose a roadmap to pluralistic alignment, specifically using large language models as a test bed. We identify and formalize three possible ways to define and operationalize pluralism in AI systems: 1) Overton pluralistic models that present a spectrum of reasonable responses; 2) Steerably pluralistic models that can steer to reflect certain perspectives; and 3) Distributionally pluralistic models that are well-calibrated to a given population in distribution. We also formalize and discuss three possible classes of pluralistic benchmarks: 1) Multi-objective benchmarks, 2) Tradeoff steerable benchmarks that incentivize models to steer to arbitrary trade-offs, and 3) Jurypluralistic benchmarks that explicitly model diverse human ratings. We use this framework to argue that current alignment techniques may be fundamentally limited for pluralistic AI; indeed, we highlight empirical evidence, both from our own experiments and from other work, that standard alignment procedures might reduce distributional pluralism in models, motivating the need for further research on pluralistic alignment. 1Department of Computer Science, University of Washington, Seattle, Washington, USA 2Department of Computer Scienc

**Style note:** Positive: The phrase 'aligning models to serve pluralistic human values remains an open research question' demonstrates the use of Normative Language, emphasizing the ethical implications of AI alignment. Negative: The abstract could be improved by avoiding overly technical jargon such as 'Overton pluralistic models' without providing sufficient context for readers unfamiliar with the term.

### Spectrum Tuning: Post-Training for Distributional Coverage and In-Context Steerability (2025)
Language model post-training has enhanced instruction-following and performance on many downstream tasks, but also comes with an often-overlooked cost on tasks with many possible valid answers. On many tasks such as creative writing, synthetic data generation, or steering to diverse preferences, models must cover an entire distribution of outputs, rather than a single correct answer. We characterize three desiderata for conditional distributional modeling: in-context steerability, valid output space coverage, and distributional alignment, and document across three model families how current post-training can reduce these properties. In particular, we disambiguate between two kinds of in-context learning: ICL for eliciting existing underlying knowledge or capabilities, and in-context steerability, where a model must use in-context information to override its priors and steer to a novel data generating distribution. To better evaluate and improve these desiderata, we introduce SPECTRUM SUITE, a large-scale resource compiled from >40 data sources and spanning >90 tasks requiring models to steer to and match diverse distributions ranging from varied human preferences to numerical distributions and more. We find that while current post-training techniques elicit underlying capabilities and knowledge, they hurt models’ ability to flexibly steer in-context. To mitigate these issues, we propose SPECTRUM TUNING, a posttraining method using SPECTRUM SUITE to improve steerability and di

**Style note:** Positive: The phrase 'models must cover an entire distribution of outputs, rather than a single correct answer' highlights the Pluralism Vocabulary mechanism, focusing on diversity in AI outputs. Negative: The abstract could better align with Choi and Sorensen's style by more explicitly addressing the societal impact of the proposed methods, rather than focusing predominantly on technical performance.

### Opt-ICL at LeWiDi-2025: Maximizing In-Context Signal from Rater Examples via Meta-Learning (2025)
Many natural language processing (NLP) tasks involve subjectivity, ambiguity, or legitimate disagreement between annotators. In this paper, we outline our system for modeling human variation. Our system leverages language models’ (LLMs) in-context learning abilities, along with a two-step meta-learning training procedure for 1) post-training on many datasets requiring in-context learning and 2) specializing the model via in-context meta-learning to the particular data distribution of interest. We also evaluate the performance of our system submission to the Learning With Disagreements (LeWiDi) competition, where it was the overall winner on both tasks. Additionally, we perform an ablation study to measure the importance of each system component. We find that including rater examples in-context is crucial for our system’s performance, dataset-specific fine-tuning is helpful on the larger datasets, post-training on other in-context datasets is helpful on one of the competition datasets, and that performance improves with model scale.

**Style note:** Positive: The phrase 'modeling human variation' reflects the Pluralism Vocabulary mechanism, emphasizing the importance of accommodating diverse human perspectives. Negative: The abstract lacks a strong opening pattern that sets the broader contextual significance before narrowing down to the specific research focus, which is a key element of Choi and Sorensen's style.

## Negative Examples

### RankAlign: A Ranking View of the Generator-Validator Gap in Large Language Models (2025)
Although large language models (LLMs) have become more capable and accurate across many tasks, some fundamental sources of unreliability remain in their behavior. One key limitation is their inconsistency at reporting the same information when prompts are changed. In this paper, we consider the discrepancy between a model’s generated answer and their own verification of that answer, the generator-validator gap. We define this gap in a more stringent way than prior work: we expect correlation of scores from a generator and a validator over the entire set of candidate answers, i.e., candidate completions that could possibly arise during ordinary language use without breaking Gricean norms. We show that according to this measure, a large gap exists in various settings, including question answering, lexical semantics tasks, and next-word prediction. We then propose RankAlign, a ranking-based training method, and show that it significantly closes the gap, surpassing all baseline methods. Moreover, this approach generalizes well to out-of-domain tasks and lexical items.1

**What's missing:** Negative: The abstract focuses heavily on technical aspects such as 'generator-validator gap' and 'ranking-based training method' without addressing the ethical or societal implications, which is contrary to Choi and Sorensen's emphasis on Normative Language and Pluralism Vocabulary.

### MuSR: Testing the Limits of Chain-of-Thought with Multistep Soft Reasoning (2023)
While large language models (LLMs) equipped with techniques like chain-ofthought prompting have demonstrated impressive capabilities, they still fall short in their ability to reason robustly in complex settings. However, evaluating LLM reasoning is challenging because system capabilities continue to grow while benchmark datasets for tasks like logical deduction have remained static. We introduce MuSR, a dataset for evaluating language models on multistep soft reasoning tasks specified in a natural language narrative. This dataset has two crucial features. First, it is created through a novel neurosymbolic synthetic-to-natural generation algorithm, enabling the construction of complex reasoning instances that challenge GPT-4 (e.g., murder mysteries roughly 1000 words in length) and which can be scaled further as more capable LLMs are released. Second, our dataset instances are free text narratives corresponding to real-world domains of reasoning; this makes it simultaneously much more challenging than other syntheticallycrafted benchmarks while remaining realistic and tractable for human annotators to solve with high accuracy. We evaluate a range of LLMs and prompting techniques on this dataset and characterize the gaps that remain for techniques like chain-of-thought to perform robust reasoning.1

**What's missing:** Negative: The abstract is centered on technical performance and dataset creation, lacking the Normative Language and focus on pluralism that characterize Choi and Sorensen's work, thus missing the broader societal context and implications.

### Calibrate-Then-Act: Cost-Aware Exploration in LLM Agents (2026)
LLMs are increasingly being used for complex problems which are not necessarily resolved in a single response, but require interacting with an environment to acquire information. In these scenarios, LLMs must reason about inherent costuncertainty tradeoffs in when to stop exploring and commit to an answer. For instance, on a programming task, an LLM should test a generated code snippet if it is uncertain about the correctness of that code; the cost of writing a test is nonzero, but typically lower than the cost of making a mistake. In this work, we show that we can induce LLMs to explicitly reason about balancing these cost-uncertainty tradeoffs, then perform more optimal environment exploration. We formalize multiple tasks, including information retrieval and coding, as sequential decision-making problems under uncertainty. Each problem has latent environment state that can be reasoned about via a prior which is passed to the LLM agent. We introduce a framework called Calibrate-Then-Act (CTA), where we feed the LLM this additional context to enable it to act more optimally. This improvement is preserved even under RL training of both the baseline and CTA. Our results on information-seeking QA and on a simplified coding task show that making cost-benefit tradeoffs explicit with CTA can help agents discover more optimal decision-making strategies.

**What's missing:** Negative: The abstract primarily discusses technical strategies and improvements in decision-making without incorporating the Normative Language or Pluralism Vocabulary that highlight the ethical and societal dimensions of AI alignment, which are central to Choi and Sorensen's style.

### HellaSwag Can a Machine Really Finish Your Sentence? (2019)
Recent work by Zellers et al. (2018) introduced a new task of commonsense natural language inference: given an event description such as “A woman sits at a piano,” a machine must select the most likely followup: “She sets her ﬁngers on the keys.” With the introduction of BERT (Devlin et al., 2018), near human-level performance was reached. Does this mean that machines can perform human level commonsense inference? In this paper, we show that commonsense inference still proves diﬃcult for even stateof-the-art models, by presenting HellaSwag, a new challenge dataset. Though its questions are trivial for humans (ą95% accuracy), state-of-the-art models struggle (ă48%). We achieve this via Adversarial Filtering (AF), a data collection paradigm wherein a series of discriminators iteratively select an adversarial set of machine-generated wrong answers. AF proves to be surprisingly robust. The key insight is to scale up the length and complexity of the dataset examples towards a critical ‘Goldilocks’ zone wherein generated text is ridiculous to humans, yet often misclassiﬁed by state-of-the-art models. Our construction of HellaSwag, and its resulting diﬃculty, sheds light on the inner workings of deep pretrained models. More broadly, it suggests a new path forward for NLP research, in which benchmarks co-evolve with the evolving state-of-the-art in an adversarial way, so as to present ever-harder challenges.

**What's missing:** Negative: The abstract focuses on technical challenges and adversarial dataset creation without addressing the societal implications or ethical considerations, which are key elements of Choi and Sorensen's style, particularly their use of Normative Language.

## Generation Instructions

1. Read section 5 of the fingerprint — these mechanisms are what make this collaboration's writing distinctive.
2. Before writing, choose which 1-2 mechanisms you will use as the backbone.
3. Open with the pattern described in section 1.
4. Use the normative/pluralistic vocabulary from section 2.
5. Do NOT use bullet-pointed contribution lists.
6. Output only the abstract text — no meta-commentary.