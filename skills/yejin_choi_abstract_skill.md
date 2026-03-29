# Yejin Choi Abstract Style Skill

You are writing a research paper abstract in the style of Yejin Choi.
Study the style fingerprint and examples below, then generate an abstract that sounds like it was written by Yejin Choi.
Do NOT copy content from the examples — reproduce the STYLE (structure, vocabulary, framing patterns), not the subject matter.

## Style Fingerprint

Certainly! Here's a structured style fingerprint for Yejin Choi's abstracts, based on the provided examples:

1. **Opening patterns**:
   - **Pattern**: Problem-first with a focus on introducing a novel dataset or challenge.
   - **Examples**:
     - "We introduce SOCIAL IQA, the first large-scale benchmark for commonsense reasoning about social situations."
     - "Recent work by Zellers et al. (2018) introduced a new task of commonsense natural language inference..."
     - "The Winograd Schema Challenge (WSC) (Levesque, Davis, and Morgenstern 2011), a benchmark for commonsense reasoning..."

2. **Problem framing**:
   - **Phrases/Templates**:
     - "This raises an important question whether..."
     - "Can AI systems learn to reliably answer..."
     - "While recent pretrained models have made progress on..., there remain questions about..."
     - "Our analysis leads to new insights into..."

3. **Methodology description**:
   - **Verbs and Phrases**:
     - "We introduce X, a Y that Z"
     - "We present the first study that investigates..."
     - "We propose a new evaluation framework for..."
     - "Through crowdsourcing, we collect..."

4. **Results and claims**:
   - **Quantitative vs. Qualitative**: Heavy emphasis on quantitative results, often with specific percentages and comparisons to human performance.
   - **Hedging Patterns**: Uses phrases like "demonstrates that," "achieves state-of-the-art performance," and "proves to be surprisingly robust."
   - **Benchmark Comparisons**: Often highlights the gap between model performance and human performance, using specific percentages to emphasize the challenge.

5. **MOST IMPORTANT — unique fingerprint mechanisms**:
   - **Mechanism 1: Emphasis on Human vs. Model Performance**:
     - Quotes: "state-of-the-art models struggle (ă48%)", "well below human performance of 91.4%."
     - Effect: Highlights the difficulty of the task and the gap that still exists between AI and human capabilities.
   
   - **Mechanism 2: Introduction of Novel Datasets/Benchmarks**:
     - Quotes: "We introduce SOCIAL IQA," "We present HellaSwag, a new challenge dataset."
     - Effect: Positions the work as pioneering and foundational in the field, providing new tools for further research.
   
   - **Mechanism 3: Use of Adversarial or Iterative Methods**:
     - Quotes: "Adversarial Filtering (AF)," "systematic bias reduction using a novel AFLITE algorithm."
     - Effect: Suggests a rigorous and innovative approach to dataset creation and evaluation, enhancing credibility.

6. **What this author avoids**:
   - **Avoids**:
     - Passive problem statements: Prefers active voice and direct framing.
     - Numbered contribution lists: Does not use bullet points or numbered lists to outline contributions.
     - Direct commercial framing: Focuses on academic and research implications rather than commercial applications.

By following these patterns, another writer could emulate Yejin Choi's distinctive style in writing academic paper abstracts.

## Positive Examples (abstracts by this author)

### Commonsense Reasoning about Social Interactions (2019)
We introduce SOCIAL IQA, the ﬁrst largescale benchmark for commonsense reasoning about social situations. SOCIAL IQA contains 38,000 multiple choice questions for probing emotional and social intelligence in a variety of everyday situations (e.g., Q: “Jordan wanted to tell Tracy a secret, so Jordan leaned towards Tracy. Why did Jordan do this?” A: “Make sure no one else could hear”). Through crowdsourcing, we collect commonsense questions along with correct and incorrect answers about social interactions, using a new framework that mitigates stylistic artifacts in incorrect answers by asking workers to provide the right answer to a different but related question. Empirical results show that our benchmark is challenging for existing question-answering models based on pretrained language models, compared to human performance (>20% gap). Notably, we further establish SOCIAL IQA as a resource for transfer learning of commonsense knowledge, achieving state-of-the-art performance on multiple commonsense reasoning tasks (Winograd Schemas, COPA).

**Style note:** Positive: The phrase 'our benchmark is challenging for existing question-answering models based on pretrained language models, compared to human performance (>20% gap)' demonstrates Mechanism 1: Emphasis on Human vs. Model Performance. Negative: The abstract uses a numbered list format in 'achieving state-of-the-art performance on multiple commonsense reasoning tasks (Winograd Schemas, COPA),' which violates the avoidance of numbered contribution lists.

### HellaSwag Can a Machine Really Finish Your Sentence? (2019)
Recent work by Zellers et al. (2018) introduced a new task of commonsense natural language inference: given an event description such as “A woman sits at a piano,” a machine must select the most likely followup: “She sets her ﬁngers on the keys.” With the introduction of BERT (Devlin et al., 2018), near human-level performance was reached. Does this mean that machines can perform human level commonsense inference? In this paper, we show that commonsense inference still proves diﬃcult for even stateof-the-art models, by presenting HellaSwag, a new challenge dataset. Though its questions are trivial for humans (ą95% accuracy), state-of-the-art models struggle (ă48%). We achieve this via Adversarial Filtering (AF), a data collection paradigm wherein a series of discriminators iteratively select an adversarial set of machine-generated wrong answers. AF proves to be surprisingly robust. The key insight is to scale up the length and complexity of the dataset examples towards a critical ‘Goldilocks’ zone wherein generated text is ridiculous to humans, yet often misclassiﬁed by state-of-the-art models. Our construction of HellaSwag, and its resulting diﬃculty, sheds light on the inner workings of deep pretrained models. More broadly, it suggests a new path forward for NLP research, in which benchmarks co-evolve with the evolving state-of-the-art in an adversarial way, so as to present ever-harder challenges.

**Style note:** Positive: The phrase 'state-of-the-art models struggle (ă48%)' highlights Mechanism 1: Emphasis on Human vs. Model Performance. Negative: The abstract uses a more narrative style in 'The key insight is to scale up the length and complexity of the dataset examples,' which deviates from the more structured and direct problem framing typical of Yejin Choi's style.

### WinoGrande: An Adversarial Winograd Schema Challenge at Scale (2019)
The Winograd Schema Challenge (WSC) (Levesque, Davis, and Morgenstern 2011), a benchmark for commonsense reasoning, is a set of 273 expert-crafted pronoun resolution problems originally designed to be unsolvable for statistical models that rely on selectional preferences or word associations. However, recent advances in neural language models have already reached around 90% accuracy on variants of WSC. This raises an important question whether these models have truly acquired robust commonsense capabilities or whether they rely on spurious biases in the datasets that lead to an overestimation of the true capabilities of machine commonsense. To investigate this question, we introduce WINOGRANDE, a large-scale dataset of 44k problems, inspired by the original WSC design, but adjusted to improve both the scale and the hardness of the dataset. The key steps of the dataset construction consist of (1) a carefully designed crowdsourcing procedure, followed by (2) systematic bias reduction using a novel AFLITE algorithm that generalizes human-detectable word associations to machine-detectable embedding associations. The best state-of-the-art methods on WINOGRANDE achieve 59.4 – 79.1%, which are ∼15-35% (absolute) below human performance of 94.0%, depending on the amount of the training data allowed (2% – 100% respectively). Furthermore, we establish new state-of-the-art results on ﬁve related benchmarks — WSC (→90.1%), DPR (→93.1%), COPA(→90.6%), KnowRef (→85.6%), and Winogender (→97

**Style note:** Positive: The phrase 'systematic bias reduction using a novel AFLITE algorithm' exemplifies Mechanism 3: Use of Adversarial or Iterative Methods. Negative: The abstract includes a numbered list format in 'The key steps of the dataset construction consist of (1) a carefully designed crowdsourcing procedure, followed by (2) systematic bias reduction,' which is not typical of Yejin Choi's style.

### Abductive Commonsense Reasoning (2019)
Abductive reasoning is inference to the most plausible explanation. For example, if Jenny ﬁnds her house in a mess when she returns from work, and remembers that she left a window open, she can hypothesize that a thief broke into her house and caused the mess, as the most plausible explanation. While abduction has long been considered to be at the core of how people interpret and read between the lines in natural language (Hobbs et al., 1988), there has been relatively little research in support of abductive natural language inference and generation. We present the ﬁrst study that investigates the viability of language-based abductive reasoning. We introduce a challenge dataset, ART, that consists of over 20k commonsense narrative contexts and 200k explanations. Based on this dataset, we conceptualize two new tasks – (i) Abductive NLI: a multiple-choice question answering task for choosing the more likely explanation, and (ii) Abductive NLG: a conditional generation task for explaining given observations in natural language. On Abductive NLI, the best model achieves 68.9% accuracy, well below human performance of 91.4%. On Abductive NLG, the current best language generators struggle even more, as they lack reasoning capabilities that are trivial for humans. Our analysis leads to new insights into the types of reasoning that deep pre-trained language models fail to perform—despite their strong performance on the related but more narrowly deﬁned task of entailment NLI—pointing 

**Style note:** Positive: The phrase 'On Abductive NLI, the best model achieves 68.9% accuracy, well below human performance of 91.4%' demonstrates Mechanism 1: Emphasis on Human vs. Model Performance. Negative: The abstract uses a more descriptive narrative in 'For example, if Jenny finds her house in a mess when she returns from work,' which is less direct than Yejin Choi's typical style.

### PIQA: Reasoning about Physical Commonsense in Natural Language ??? (2019)
To apply eyeshadow without a brush, should I use a cotton swab or a toothpick? Questions requiring this kind of physical commonsense pose a challenge to today’s natural language understanding systems. While recent pretrained models (such as BERT) have made progress on question answering over more abstract domains – such as news articles and encyclopedia entries, where text is plentiful – in more physical domains, text is inherently limited due to reporting bias. Can AI systems learn to reliably answer physical commonsense questions without experiencing the physical world? In this paper, we introduce the task of physical commonsense reasoning and a corresponding benchmark dataset Physical Interaction: Question Answering or PIQA . Though humans ﬁnd the dataset easy (95% accuracy), large pretrained models struggle (∼77%). We provide analysis about the dimensions of knowledge that existing models lack, which offers signiﬁcant opportunities for future research.

### A On Symbolic and Neural Commonsense Knowledge Graphs (2020)
Recent years have brought about a renewed interest in commonsense representation and reasoning in the ﬁeld of natural language understanding. The development of new commonsense knowledge graphs (CSKG) has been central to these advances as their diverse facts can be used and referenced by machine learning models for tackling new and challenging tasks. At the same time, there remain questions about the quality and coverage of these resources due to the massive scale required to comprehensively encompass general commonsense knowledge. In this work, we posit that manually constructed CSKGs will never achieve the coverage necessary to be applicable in all situations encountered by NLP agents. Therefore, we propose a new evaluation framework for testing the utility of KGs based on how effectively implicit knowledge representations can be learned from them. With this new goal, we propose ATOMIC20 20, a new CSKG of general-purpose commonsense knowledge containing knowledge that is not readily available in pretrained language models. We evaluate its properties in comparison with other leading CSKGs, performing the ﬁrst large-scale pairwise study of commonsense knowledge resources. Next, we show that ATOMIC20 20 is better suited for training knowledge models that can generate accurate, representative knowledge for new, unseen entities and events. Finally, through human evaluation, we show that the few-shot performance of GPT-3 (175B parameters), while impressive, remains ∼12 absolute p

### Knowledge Neurons in Pretrained Transformers (2021)
Large-scale pretrained language models are surprisingly good at recalling factual knowledge presented in the training corpus (Petroni et al., 2019; Jiang et al., 2020b). In this paper, we present preliminary studies on how factual knowledge is stored in pretrained Transformers by introducing the concept of knowledge neurons. Speciﬁcally, we examine the ﬁll-in-the-blank cloze task for BERT. Given a relational fact, we propose a knowledge attribution method to identify the neurons that express the fact. We ﬁnd that the activation of such knowledge neurons is positively correlated to the expression of their corresponding facts. In our case studies, we attempt to leverage knowledge neurons to edit (such as update, and erase) speciﬁc factual knowledge without ﬁne-tuning. Our results shed light on understanding the storage of knowledge within pretrained Transformers. The code is available at https://github.com/ Hunter-DDM/knowledge-neurons.

**Style note:** Positive: The phrase 'Our results shed light on understanding the storage of knowledge within pretrained Transformers' demonstrates Mechanism 3: Use of Adversarial or Iterative Methods. Negative: The abstract includes a more exploratory narrative in 'In our case studies, we attempt to leverage knowledge neurons,' which is less structured than Yejin Choi's typical style.

### Symbolic Knowledge Distillation: from General Language Models to Commonsense Models (2021)
The common practice for training commonsense models has gone from–human–to– corpus–to–machine: humans author commonsense knowledge graphs in order to train commonsense models. In this work, we investigate an alternative, from–machine–to–corpus– to–machine: general language models author these commonsense knowledge graphs to train commonsense models. Our study leads to a new framework, Symbolic Knowledge Distillation. As with prior art in Knowledge Distillation (Hinton et al., 2015), our approach uses larger models to teach smaller models. A key difference is that we distill knowledge symbolically–as text–in addition to the resulting neural model. We distill only one aspect–the commonsense of a general language model teacher, allowing the student to be a different type of model, a commonsense model. Altogether, we show that careful prompt engineering and a separately trained critic model allow us to selectively distill highquality causal commonsense from GPT-3, a general language model. Empirical results demonstrate that, for the ﬁrst time, a human-authored commonsense knowledge graph is surpassed by our automatically distilled variant in all three criteria: quantity, quality, and diversity. In addition, it results in a neural commonsense model that surpasses the teacher model’s commonsense capabilities despite its 100x smaller size. We apply this to the ATOMIC resource, and will share our new symbolic knowledge graph and commonsense models1.

**Style note:** Positive: The phrase 'Empirical results demonstrate that, for the first time, a human-authored commonsense knowledge graph is surpassed by our automatically distilled variant' highlights Mechanism 2: Introduction of Novel Datasets/Benchmarks. Negative: The abstract uses a more narrative style in 'Our study leads to a new framework, Symbolic Knowledge Distillation,' which is less direct than Yejin Choi's typical style.

## Negative Examples (different author, same field)

### MuSR: Testing the Limits of Chain-of-Thought with Multistep Soft Reasoning (2023)
While large language models (LLMs) equipped with techniques like chain-ofthought prompting have demonstrated impressive capabilities, they still fall short in their ability to reason robustly in complex settings. However, evaluating LLM reasoning is challenging because system capabilities continue to grow while benchmark datasets for tasks like logical deduction have remained static. We introduce MuSR, a dataset for evaluating language models on multistep soft reasoning tasks specified in a natural language narrative. This dataset has two crucial features. First, it is created through a novel neurosymbolic synthetic-to-natural generation algorithm, enabling the construction of complex reasoning instances that challenge GPT-4 (e.g., murder mysteries roughly 1000 words in length) and which can be scaled further as more capable LLMs are released. Second, our dataset instances are free text narratives corresponding to real-world domains of reasoning; this makes it simultaneously much more challenging than other syntheticallycrafted benchmarks while remaining realistic and tractable for human annotators to solve with high accuracy. We evaluate a range of LLMs and prompting techniques on this dataset and characterize the gaps that remain for techniques like chain-of-thought to perform robust reasoning.1

**What's missing:** Positive: The phrase 'we introduce MuSR, a dataset for evaluating language models on multistep soft reasoning tasks' demonstrates Mechanism 2: Introduction of Novel Datasets/Benchmarks. Negative: The abstract uses a more descriptive narrative in 'This dataset has two crucial features,' which is less direct and structured than Yejin Choi's typical style.

### RankAlign: A Ranking View of the Generator-Validator Gap in Large Language Models (2025)
Although large language models (LLMs) have become more capable and accurate across many tasks, some fundamental sources of unreliability remain in their behavior. One key limitation is their inconsistency at reporting the same information when prompts are changed. In this paper, we consider the discrepancy between a model’s generated answer and their own verification of that answer, the generator-validator gap. We define this gap in a more stringent way than prior work: we expect correlation of scores from a generator and a validator over the entire set of candidate answers, i.e., candidate completions that could possibly arise during ordinary language use without breaking Gricean norms. We show that according to this measure, a large gap exists in various settings, including question answering, lexical semantics tasks, and next-word prediction. We then propose RankAlign, a ranking-based training method, and show that it significantly closes the gap, surpassing all baseline methods. Moreover, this approach generalizes well to out-of-domain tasks and lexical items.1

**What's missing:** Positive: The phrase 'we propose RankAlign, a ranking-based training method, and show that it significantly closes the gap' exemplifies Mechanism 3: Use of Adversarial or Iterative Methods. Negative: The abstract uses a more speculative tone in 'we expect correlation of scores from a generator and a validator,' which is less definitive than Yejin Choi's typical style.

### ChartMuseum: Testing Visual Reasoning Capabilities of Large Vision-Language Models (2025)
Chart understanding presents a unique challenge for large vision-language models (LVLMs), as it requires the integration of sophisticated textual and visual reasoning capabilities. However, current LVLMs exhibit a notable imbalance between these skills, falling short on visual reasoning that is difficult to perform in text. We conduct a case study using a synthetic dataset solvable only through visual reasoning and show that model performance degrades significantly with increasing visual complexity, while human performance remains robust. We then introduce CHARTMUSEUM, a new Chart Question Answering (QA) benchmark containing 1,162 expert-annotated questions spanning multiple reasoning types, curated from realworld charts across 184 sources, specifically built to evaluate complex visual and textual reasoning. Unlike prior chart understanding benchmarks—where frontier models perform similarly and near saturation—our benchmark exposes a substantial gap between model and human performance, while effectively differentiating model capabilities: although humans achieve 93% accuracy, the best-performing model Gemini-2.5-Pro attains only 63.0%, and the leading open-source LVLM Qwen2.5-VL-72B-Instruct achieves only 38.5%. Moreover, on questions requiring primarily visual reasoning, all models experience a 35%-55% performance drop from text-reasoning-heavy question performance. Lastly, our qualitative error analysis reveals specific categories of visual reasoning that are challenging fo

**What's missing:** Positive: The phrase 'we then introduce CHARTMUSEUM, a new Chart Question Answering (QA) benchmark' highlights Mechanism 2: Introduction of Novel Datasets/Benchmarks. Negative: The abstract includes a more descriptive narrative in 'Chart understanding presents a unique challenge for large vision-language models,' which is less direct and structured than Yejin Choi's typical style.

## Generation Instructions

1. Read section 5 of the style fingerprint (unique mechanisms) — this is what makes Yejin Choi's writing distinctive.
2. Before writing, decide which mechanism(s) you will use as the structural backbone.
3. Open the abstract with the pattern identified in section 1 of the fingerprint.
4. Use the vocabulary and framing from sections 2–4.
5. Do NOT use numbered contribution lists or bullet points unless the fingerprint says this author uses them.
6. Output only the abstract text — no meta-commentary.