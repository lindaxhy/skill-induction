# Yejin Choi and Taylor Sorensen Abstract Style Skill

You are writing a research paper abstract in the collaborative style of Yejin Choi and Taylor Sorensen.
Study the style fingerprint and examples carefully, then generate an abstract that sounds like it was co-authored by both of them.
Do NOT copy content from the examples — reproduce the STYLE (structure, vocabulary, framing, normative stance), not the subject matter.

## Style Fingerprint

### 1. Opening Patterns

**Pattern:** Contextualization with a focus on AI's societal role.

**Quoted Openings:**
- "With increased power and prevalence of AI systems, it is ever more critical that AI systems are designed to serve all, i.e., people with diverse values and perspectives."
- "Recent calls for pluralistic alignment emphasize that AI systems should address the diverse needs of all people."

**Explanation:** Choi and Sorensen consistently open with a broad contextual statement about the societal importance of AI, emphasizing diversity and pluralism. This sets the stage for their focus on alignment and personalization.

### 2. Problem Framing

**Specific Phrases/Templates:**
- "aligning models to serve pluralistic human values remains an open research question."
- "efforts in this space often require sorting people into fixed buckets of pre-specified diversity-defining dimensions."
- "achieve an authentic representation of diversity that respects individuality."

**Explanation:** They frame the challenge as one of inclusivity and representation, often highlighting the limitations of current approaches and the need for more nuanced solutions.

### 3. Methodology Description

**Specific Verbs/Sentence Templates:**
- "We propose a roadmap to..."
- "We identify and formalize..."
- "We introduce INDIEVALUECATALOG, a dataset transformed from..."
- "Our system leverages language models’ (LLMs) in-context learning abilities..."

**Explanation:** Their methodology descriptions often involve proposing frameworks, identifying key components, and introducing new datasets or systems. They use active verbs to convey a sense of innovation and contribution.

### 4. Claims and Hedging

**Position Papers:** 
- Use of normative language and broad claims, e.g., "current alignment techniques may be fundamentally limited for pluralistic AI."

**Empirical Papers:**
- Present empirical evidence with specific metrics, e.g., "models achieve only 55 % to 65% accuracy."

**Explanation:** They use strong normative language in position papers to advocate for new directions, while empirical papers are more data-driven, presenting specific findings and limitations.

### 5. Most Important — Unique Fingerprint Mechanisms

**Mechanism 1: Normative Language on Pluralism**
- Quotes: "serve pluralistic human values," "authentic representation of diversity."
- Effect: Establishes a moral imperative for AI alignment, emphasizing ethical considerations.

**Mechanism 2: Pluralism Vocabulary**
- Quotes: "Overton pluralistic models," "Steerably pluralistic models," "Distributionally pluralistic models."
- Effect: Introduces specialized terminology to categorize and discuss pluralism in AI, creating a nuanced framework.

**Mechanism 3: Stance on AI Values**
- Quotes: "AI systems should address the diverse needs of all people," "respect individuality."
- Effect: Positions their work as fundamentally concerned with ethical AI, distinguishing it from more technical or performance-focused research.

**Mechanism 4: Rhetorical Strategies in Position Papers**
- Quotes: "motivating the need for further research," "highlight empirical evidence."
- Effect: Uses rhetorical strategies to build a case for the importance and urgency of their research agenda.

### 6. What This Collaboration Avoids

**Constructions Absent:**
- **Technical Jargon Overload:** Unlike some technical papers, they avoid excessive jargon, focusing instead on clarity and accessibility.
- **Overemphasis on Model Performance:** They do not focus solely on performance metrics or technical improvements, instead emphasizing ethical and societal implications.
- **Static Problem Definitions:** They avoid framing problems as static or purely technical, instead highlighting the dynamic and evolving nature of AI alignment challenges.

## Positive Examples (co-authored by Yejin Choi + Taylor Sorensen)

### Position: A Roadmap to Pluralistic Alignment (2024)
With increased power and prevalence of AI systems, it is ever more critical that AI systems are designed to serve all, i.e., people with diverse values and perspectives. However, aligning models to serve pluralistic human values remains an open research question. In this piece, we propose a roadmap to pluralistic alignment, specifically using large language models as a test bed. We identify and formalize three possible ways to define and operationalize pluralism in AI systems: 1) Overton pluralistic models that present a spectrum of reasonable responses; 2) Steerably pluralistic models that can steer to reflect certain perspectives; and 3) Distributionally pluralistic models that are well-calibrated to a given population in distribution. We also formalize and discuss three possible classes of pluralistic benchmarks: 1) Multi-objective benchmarks, 2) Tradeoff steerable benchmarks that incentivize models to steer to arbitrary trade-offs, and 3) Jurypluralistic benchmarks that explicitly model diverse human ratings. We use this framework to argue that current alignment techniques may be fundamentally limited for pluralistic AI; indeed, we highlight empirical evidence, both from our own experiments and from other work, that standard alignment procedures might reduce distributional pluralism in models, motivating the need for further research on pluralistic alignment. 1Department of Computer Science, University of Washington, Seattle, Washington, USA 2Department of Computer Scienc

**Style note:** Positive: The phrase 'current alignment techniques may be fundamentally limited for pluralistic AI' demonstrates Mechanism 1: Normative Language on Pluralism, emphasizing the ethical imperative for AI alignment. Negative: The abstract lacks a clear empirical evidence section, which is a key component in Choi and Sorensen's empirical papers.

### Can Language Models Reason about Individualistic Human Values and Preferences? (2024)
Recent calls for pluralistic alignment emphasize that AI systems should address the diverse needs of all people. Yet, efforts in this space often require sorting people into fixed buckets of pre-specified diversity-defining dimensions (e.g., demographics), risking smoothing out individualistic variations or even stereotyping. To achieve an authentic representation of diversity that respects individuality, we propose individualistic alignment.1 While individualistic alignment can take various forms, we introduce INDIEVALUECATALOG, a dataset transformed from the influential World Values Survey (WVS), to study language models (LMs) on the specific challenge of individualistic value reasoning. Given a sample of an individual’s value-expressing statements, models are tasked with predicting this person’s value judgments in novel cases. With INDIEVALUECATALOG, we reveal critical limitations in frontier LMs, which achieve only 55 % to 65% accuracy in predicting individualistic values. Moreover, our results highlight that a precise description of individualistic values cannot be approximated only with demographic information. We also identify a partiality of LMs in reasoning about global individualistic values, as measured by our proposed VALUE INEQUITY INDEX (σINEQUITY). Finally, we train a series of INDIEVALUEREASONERS to reveal new patterns and dynamics into global human values.

**Style note:** Positive: The phrase 'achieve an authentic representation of diversity that respects individuality' exemplifies Mechanism 1: Normative Language on Pluralism, highlighting the moral imperative for respecting individual diversity. Negative: The abstract could benefit from a more explicit discussion of the societal role of AI, which is a common opening pattern in Choi and Sorensen's work.

### Opt-ICL at LeWiDi-2025: Maximizing In-Context Signal from Rater Examples via Meta-Learning (2025)
Many natural language processing (NLP) tasks involve subjectivity, ambiguity, or legitimate disagreement between annotators. In this paper, we outline our system for modeling human variation. Our system leverages language models’ (LLMs) in-context learning abilities, along with a two-step meta-learning training procedure for 1) post-training on many datasets requiring in-context learning and 2) specializing the model via in-context meta-learning to the particular data distribution of interest. We also evaluate the performance of our system submission to the Learning With Disagreements (LeWiDi) competition, where it was the overall winner on both tasks. Additionally, we perform an ablation study to measure the importance of each system component. We find that including rater examples in-context is crucial for our system’s performance, dataset-specific fine-tuning is helpful on the larger datasets, post-training on other in-context datasets is helpful on one of the competition datasets, and that performance improves with model scale.

**Style note:** Positive: The phrase 'Our system leverages language models’ (LLMs) in-context learning abilities' aligns with Mechanism 3: Stance on AI Values, showcasing the innovative use of AI capabilities. Negative: The abstract lacks a broader contextualization of AI's societal role, which is a typical opening pattern in Choi and Sorensen's style.

## Negative Examples

### RankAlign: A Ranking View of the Generator-Validator Gap in Large Language Models (2025)
Although large language models (LLMs) have become more capable and accurate across many tasks, some fundamental sources of unreliability remain in their behavior. One key limitation is their inconsistency at reporting the same information when prompts are changed. In this paper, we consider the discrepancy between a model’s generated answer and their own verification of that answer, the generator-validator gap. We define this gap in a more stringent way than prior work: we expect correlation of scores from a generator and a validator over the entire set of candidate answers, i.e., candidate completions that could possibly arise during ordinary language use without breaking Gricean norms. We show that according to this measure, a large gap exists in various settings, including question answering, lexical semantics tasks, and next-word prediction. We then propose RankAlign, a ranking-based training method, and show that it significantly closes the gap, surpassing all baseline methods. Moreover, this approach generalizes well to out-of-domain tasks and lexical items.1

**What's missing:** Negative: The abstract is heavily focused on technical jargon and model performance, which violates the Choi and Sorensen style that avoids overemphasis on technical details and instead focuses on ethical and societal implications.

### MuSR: Testing the Limits of Chain-of-Thought with Multistep Soft Reasoning (2023)
While large language models (LLMs) equipped with techniques like chain-ofthought prompting have demonstrated impressive capabilities, they still fall short in their ability to reason robustly in complex settings. However, evaluating LLM reasoning is challenging because system capabilities continue to grow while benchmark datasets for tasks like logical deduction have remained static. We introduce MuSR, a dataset for evaluating language models on multistep soft reasoning tasks specified in a natural language narrative. This dataset has two crucial features. First, it is created through a novel neurosymbolic synthetic-to-natural generation algorithm, enabling the construction of complex reasoning instances that challenge GPT-4 (e.g., murder mysteries roughly 1000 words in length) and which can be scaled further as more capable LLMs are released. Second, our dataset instances are free text narratives corresponding to real-world domains of reasoning; this makes it simultaneously much more challenging than other syntheticallycrafted benchmarks while remaining realistic and tractable for human annotators to solve with high accuracy. We evaluate a range of LLMs and prompting techniques on this dataset and characterize the gaps that remain for techniques like chain-of-thought to perform robust reasoning.1

**What's missing:** Negative: The abstract emphasizes static problem definitions and technical improvements, which contrasts with Choi and Sorensen's dynamic framing of AI alignment challenges and their focus on ethical considerations.

### Calibrate-Then-Act: Cost-Aware Exploration in LLM Agents (2026)
LLMs are increasingly being used for complex problems which are not necessarily resolved in a single response, but require interacting with an environment to acquire information. In these scenarios, LLMs must reason about inherent costuncertainty tradeoffs in when to stop exploring and commit to an answer. For instance, on a programming task, an LLM should test a generated code snippet if it is uncertain about the correctness of that code; the cost of writing a test is nonzero, but typically lower than the cost of making a mistake. In this work, we show that we can induce LLMs to explicitly reason about balancing these cost-uncertainty tradeoffs, then perform more optimal environment exploration. We formalize multiple tasks, including information retrieval and coding, as sequential decision-making problems under uncertainty. Each problem has latent environment state that can be reasoned about via a prior which is passed to the LLM agent. We introduce a framework called Calibrate-Then-Act (CTA), where we feed the LLM this additional context to enable it to act more optimally. This improvement is preserved even under RL training of both the baseline and CTA. Our results on information-seeking QA and on a simplified coding task show that making cost-benefit tradeoffs explicit with CTA can help agents discover more optimal decision-making strategies.

**What's missing:** Negative: The abstract focuses on technical jargon and performance metrics, lacking the normative language and pluralism vocabulary that are central to Choi and Sorensen's style.

### HellaSwag Can a Machine Really Finish Your Sentence? (2019)
Recent work by Zellers et al. (2018) introduced a new task of commonsense natural language inference: given an event description such as “A woman sits at a piano,” a machine must select the most likely followup: “She sets her ﬁngers on the keys.” With the introduction of BERT (Devlin et al., 2018), near human-level performance was reached. Does this mean that machines can perform human level commonsense inference? In this paper, we show that commonsense inference still proves diﬃcult for even stateof-the-art models, by presenting HellaSwag, a new challenge dataset. Though its questions are trivial for humans (ą95% accuracy), state-of-the-art models struggle (ă48%). We achieve this via Adversarial Filtering (AF), a data collection paradigm wherein a series of discriminators iteratively select an adversarial set of machine-generated wrong answers. AF proves to be surprisingly robust. The key insight is to scale up the length and complexity of the dataset examples towards a critical ‘Goldilocks’ zone wherein generated text is ridiculous to humans, yet often misclassiﬁed by state-of-the-art models. Our construction of HellaSwag, and its resulting diﬃculty, sheds light on the inner workings of deep pretrained models. More broadly, it suggests a new path forward for NLP research, in which benchmarks co-evolve with the evolving state-of-the-art in an adversarial way, so as to present ever-harder challenges.

**What's missing:** Negative: The abstract is centered on model performance and technical challenges, missing the broader societal context and ethical considerations that are characteristic of Choi and Sorensen's work.

## Generation Instructions

1. Read section 5 of the fingerprint — these mechanisms are what make this collaboration's writing distinctive.
2. Before writing, choose which 1-2 mechanisms you will use as the backbone.
3. Open with the pattern described in section 1.
4. Use the normative/pluralistic vocabulary from section 2.
5. Do NOT use bullet-pointed contribution lists.
6. Output only the abstract text — no meta-commentary.