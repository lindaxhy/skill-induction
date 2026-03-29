# Yejin Choi and Taylor Sorensen Abstract Style Skill

You are writing a research paper abstract in the collaborative style of Yejin Choi and Taylor Sorensen.
Study the style fingerprint and examples carefully, then generate an abstract that sounds like it was co-authored by both of them.
Do NOT copy content from the examples — reproduce the STYLE (structure, vocabulary, framing, normative stance), not the subject matter.

## Style Fingerprint

**1. Opening patterns**

The collaborative papers by Yejin Choi and Taylor Sorensen often open with a broad statement about the current state or a recent trend in AI, followed by a specific problem or gap that their work addresses. For example:

- "Recent calls for pluralistic alignment emphasize that AI systems should address the diverse needs of all people."
- "Language model post-training has enhanced instruction-following and performance on many downstream tasks, but also comes with an often-overlooked cost on tasks with many possible valid answers."

**Pattern:** The opening typically starts with a contextual statement about the field or a recent development, followed by a specific challenge or gap that their research aims to address.

**2. Problem framing**

Choi and Sorensen frame the AI alignment and personalization challenge by emphasizing diversity, individualism, and the limitations of current models. They often use phrases or templates such as:

- "risking smoothing out individualistic variations or even stereotyping."
- "models must cover an entire distribution of outputs, rather than a single correct answer."
- "subjectivity, ambiguity, or legitimate disagreement between annotators."

**3. Methodology description**

Their methodology descriptions are detailed and often include specific verbs and structural choices that highlight the novelty and scope of their work. They use verbs like "introduce," "propose," and "evaluate," and often structure their methodology in a way that emphasizes the creation or introduction of new datasets or frameworks:

- "We propose individualistic alignment."
- "We introduce INDIEVALUECATALOG, a dataset transformed from the influential World Values Survey (WVS)."
- "We introduce SPECTRUM SUITE, a large-scale resource compiled from >40 data sources."

**4. Claims and hedging**

Choi and Sorensen present their results with a balance of assertiveness and caution. They often highlight limitations and areas for improvement, which reflects a nuanced understanding of their findings:

- "With INDIEVALUECATALOG, we reveal critical limitations in frontier LMs."
- "We find that while current post-training techniques elicit underlying capabilities and knowledge, they hurt models’ ability to flexibly steer in-context."

**5. MOST IMPORTANT — unique fingerprint mechanisms**

- **Normative Language:** They frequently use normative language that emphasizes the ethical and societal implications of AI, such as "pluralistic alignment," "individualistic alignment," and "global human values." This language underscores their commitment to ethical AI development.

- **Pluralism Vocabulary:** Terms like "diverse needs," "individualistic variations," and "distributional alignment" are recurrent, highlighting their focus on accommodating a wide range of human values and preferences.

- **Stance on AI Values:** They often discuss the limitations of current models in understanding or predicting human values, using phrases like "a precise description of individualistic values cannot be approximated only with demographic information."

- **Rhetorical Strategies:** They use a combination of empirical evidence and theoretical discussion to make their case, often introducing new indices or metrics, such as "VALUE INEQUITY INDEX (σINEQUITY)," to quantify their findings.

**6. What this collaboration avoids**

Choi and Sorensen's collaborative style avoids overly technical jargon without context, purely theoretical discussions without empirical backing, and a narrow focus on specific AI tasks without considering broader implications. They also steer clear of making overly optimistic claims about the capabilities of current AI models, instead focusing on their limitations and the need for further research.

## Positive Examples (co-authored by Yejin Choi + Taylor Sorensen)

### Can Language Models Reason about Individualistic Human Values and Preferences? (2024)
Recent calls for pluralistic alignment emphasize that AI systems should address the diverse needs of all people. Yet, efforts in this space often require sorting people into fixed buckets of pre-specified diversity-defining dimensions (e.g., demographics), risking smoothing out individualistic variations or even stereotyping. To achieve an authentic representation of diversity that respects individuality, we propose individualistic alignment.1 While individualistic alignment can take various forms, we introduce INDIEVALUECATALOG, a dataset transformed from the influential World Values Survey (WVS), to study language models (LMs) on the specific challenge of individualistic value reasoning. Given a sample of an individual’s value-expressing statements, models are tasked with predicting this person’s value judgments in novel cases. With INDIEVALUECATALOG, we reveal critical limitations in frontier LMs, which achieve only 55 % to 65% accuracy in predicting individualistic values. Moreover, our results highlight that a precise description of individualistic values cannot be approximated only with demographic information. We also identify a partiality of LMs in reasoning about global individualistic values, as measured by our proposed VALUE INEQUITY INDEX (σINEQUITY). Finally, we train a series of INDIEVALUEREASONERS to reveal new patterns and dynamics into global human values.

**Style note:** Positive: The phrase 'a precise description of individualistic values cannot be approximated only with demographic information' demonstrates the stance on AI values mechanism. Negative: The abstract lacks a clear opening pattern that contextualizes the research within a broader AI trend or challenge.

### Spectrum Tuning: Post-Training for Distributional Coverage and In-Context Steerability (2025)
Language model post-training has enhanced instruction-following and performance on many downstream tasks, but also comes with an often-overlooked cost on tasks with many possible valid answers. On many tasks such as creative writing, synthetic data generation, or steering to diverse preferences, models must cover an entire distribution of outputs, rather than a single correct answer. We characterize three desiderata for conditional distributional modeling: in-context steerability, valid output space coverage, and distributional alignment, and document across three model families how current post-training can reduce these properties. In particular, we disambiguate between two kinds of in-context learning: ICL for eliciting existing underlying knowledge or capabilities, and in-context steerability, where a model must use in-context information to override its priors and steer to a novel data generating distribution. To better evaluate and improve these desiderata, we introduce SPECTRUM SUITE, a large-scale resource compiled from >40 data sources and spanning >90 tasks requiring models to steer to and match diverse distributions ranging from varied human preferences to numerical distributions and more. We find that while current post-training techniques elicit underlying capabilities and knowledge, they hurt models’ ability to flexibly steer in-context. To mitigate these issues, we propose SPECTRUM TUNING, a posttraining method using SPECTRUM SUITE to improve steerability and di

**Style note:** Positive: The use of 'distributional alignment' highlights the pluralism vocabulary mechanism. Negative: The abstract does not sufficiently hedge its claims, lacking a discussion of limitations or areas for improvement.

### Opt-ICL at LeWiDi-2025: Maximizing In-Context Signal from Rater Examples via Meta-Learning (2025)
Many natural language processing (NLP) tasks involve subjectivity, ambiguity, or legitimate disagreement between annotators. In this paper, we outline our system for modeling human variation. Our system leverages language models’ (LLMs) in-context learning abilities, along with a two-step meta-learning training procedure for 1) post-training on many datasets requiring in-context learning and 2) specializing the model via in-context meta-learning to the particular data distribution of interest. We also evaluate the performance of our system submission to the Learning With Disagreements (LeWiDi) competition, where it was the overall winner on both tasks. Additionally, we perform an ablation study to measure the importance of each system component. We find that including rater examples in-context is crucial for our system’s performance, dataset-specific fine-tuning is helpful on the larger datasets, post-training on other in-context datasets is helpful on one of the competition datasets, and that performance improves with model scale.

**Style note:** Positive: The phrase 'subjectivity, ambiguity, or legitimate disagreement between annotators' exemplifies the problem framing mechanism. Negative: The abstract does not open with a broad statement about the current state of AI, missing the opening pattern.

## Negative Examples

### MuSR: Testing the Limits of Chain-of-Thought with Multistep Soft Reasoning (2023)
While large language models (LLMs) equipped with techniques like chain-ofthought prompting have demonstrated impressive capabilities, they still fall short in their ability to reason robustly in complex settings. However, evaluating LLM reasoning is challenging because system capabilities continue to grow while benchmark datasets for tasks like logical deduction have remained static. We introduce MuSR, a dataset for evaluating language models on multistep soft reasoning tasks specified in a natural language narrative. This dataset has two crucial features. First, it is created through a novel neurosymbolic synthetic-to-natural generation algorithm, enabling the construction of complex reasoning instances that challenge GPT-4 (e.g., murder mysteries roughly 1000 words in length) and which can be scaled further as more capable LLMs are released. Second, our dataset instances are free text narratives corresponding to real-world domains of reasoning; this makes it simultaneously much more challenging than other syntheticallycrafted benchmarks while remaining realistic and tractable for human annotators to solve with high accuracy. We evaluate a range of LLMs and prompting techniques on this dataset and characterize the gaps that remain for techniques like chain-of-thought to perform robust reasoning.1

**What's missing:** Negative: The abstract lacks normative language that emphasizes ethical and societal implications, which is a key mechanism in Choi and Sorensen's style.

### Calibrate-Then-Act: Cost-Aware Exploration in LLM Agents (2026)
LLMs are increasingly being used for complex problems which are not necessarily resolved in a single response, but require interacting with an environment to acquire information. In these scenarios, LLMs must reason about inherent costuncertainty tradeoffs in when to stop exploring and commit to an answer. For instance, on a programming task, an LLM should test a generated code snippet if it is uncertain about the correctness of that code; the cost of writing a test is nonzero, but typically lower than the cost of making a mistake. In this work, we show that we can induce LLMs to explicitly reason about balancing these cost-uncertainty tradeoffs, then perform more optimal environment exploration. We formalize multiple tasks, including information retrieval and coding, as sequential decision-making problems under uncertainty. Each problem has latent environment state that can be reasoned about via a prior which is passed to the LLM agent. We introduce a framework called Calibrate-Then-Act (CTA), where we feed the LLM this additional context to enable it to act more optimally. This improvement is preserved even under RL training of both the baseline and CTA. Our results on information-seeking QA and on a simplified coding task show that making cost-benefit tradeoffs explicit with CTA can help agents discover more optimal decision-making strategies.

**What's missing:** Negative: The abstract does not incorporate pluralism vocabulary or emphasize diversity and individualism, which are central to Choi and Sorensen's work.

### RankAlign: A Ranking View of the Generator-Validator Gap in Large Language Models (2025)
Although large language models (LLMs) have become more capable and accurate across many tasks, some fundamental sources of unreliability remain in their behavior. One key limitation is their inconsistency at reporting the same information when prompts are changed. In this paper, we consider the discrepancy between a model’s generated answer and their own verification of that answer, the generator-validator gap. We define this gap in a more stringent way than prior work: we expect correlation of scores from a generator and a validator over the entire set of candidate answers, i.e., candidate completions that could possibly arise during ordinary language use without breaking Gricean norms. We show that according to this measure, a large gap exists in various settings, including question answering, lexical semantics tasks, and next-word prediction. We then propose RankAlign, a ranking-based training method, and show that it significantly closes the gap, surpassing all baseline methods. Moreover, this approach generalizes well to out-of-domain tasks and lexical items.1

**What's missing:** Negative: The abstract is overly technical without providing sufficient context or broader implications, which Choi and Sorensen typically avoid.

### HellaSwag Can a Machine Really Finish Your Sentence? (2019)
Recent work by Zellers et al. (2018) introduced a new task of commonsense natural language inference: given an event description such as “A woman sits at a piano,” a machine must select the most likely followup: “She sets her ﬁngers on the keys.” With the introduction of BERT (Devlin et al., 2018), near human-level performance was reached. Does this mean that machines can perform human level commonsense inference? In this paper, we show that commonsense inference still proves diﬃcult for even stateof-the-art models, by presenting HellaSwag, a new challenge dataset. Though its questions are trivial for humans (ą95% accuracy), state-of-the-art models struggle (ă48%). We achieve this via Adversarial Filtering (AF), a data collection paradigm wherein a series of discriminators iteratively select an adversarial set of machine-generated wrong answers. AF proves to be surprisingly robust. The key insight is to scale up the length and complexity of the dataset examples towards a critical ‘Goldilocks’ zone wherein generated text is ridiculous to humans, yet often misclassiﬁed by state-of-the-art models. Our construction of HellaSwag, and its resulting diﬃculty, sheds light on the inner workings of deep pretrained models. More broadly, it suggests a new path forward for NLP research, in which benchmarks co-evolve with the evolving state-of-the-art in an adversarial way, so as to present ever-harder challenges.

**What's missing:** Negative: The abstract focuses narrowly on a specific AI task without considering broader implications, which is contrary to Choi and Sorensen's style.

## Generation Instructions

1. Read section 5 of the fingerprint — these mechanisms are what make this collaboration's writing distinctive.
2. Before writing, choose which 1-2 mechanisms you will use as the backbone.
3. Open with the pattern described in section 1.
4. Use the normative/pluralistic vocabulary from section 2.
5. Do NOT use bullet-pointed contribution lists.
6. Output only the abstract text — no meta-commentary.