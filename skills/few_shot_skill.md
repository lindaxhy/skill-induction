# Essay Scoring Rubric

## Content (Development & Support)

### Excellent (4.0-5.0)
- Presents a clear, sophisticated argument directly addressing all aspects of the prompt
- Supports claims with specific, relevant examples and detailed explanations
- Demonstrates thorough understanding of the topic with insightful analysis
- Develops ideas fully with rich supporting details and compelling reasoning
- Shows original thinking and depth of analysis (e.g., Essays #26, #28)

### Adequate (2.5-3.5)
- Addresses the prompt with a basic argument or position
- Includes some examples but may lack detail or specificity
- Shows basic understanding but limited depth of analysis
- Support may be general or partially developed
- Ideas are relevant but may be repetitive or superficial (e.g., Essays #1, #6)

### Weak (0.5-2.0)
- Minimal or unclear response to the prompt
- Few or no specific examples to support claims
- Underdeveloped ideas with little explanation
- May drift off-topic or show misunderstanding
- Relies on assertion rather than reasoning (e.g., Essays #2, #7)

## Organization (Structure & Coherence)

### Excellent (4.0-5.0)
- Clear introduction with strong thesis statement
- Logical progression of ideas with effective transitions
- Well-structured paragraphs with clear topic sentences
- Strong conclusion that reinforces main arguments
- Coherent overall structure that enhances argument (e.g., Essays #21, #28)

### Adequate (2.5-3.5)
- Basic organizational structure present
- Some transitions between ideas, though may be mechanical
- Paragraphs show basic focus but may lack strong organization
- Conclusion present but may be simple restatement
- Generally logical but may have some disconnected ideas (e.g., Essays #5, #17)

### Weak (0.5-2.0)
- Unclear or missing organizational structure
- Abrupt transitions or lacking connections between ideas
- Paragraphs poorly focused or organized
- Missing or ineffective conclusion
- Ideas presented randomly or illogically (e.g., Essays #2, #4)

## Language (Grammar, Vocabulary & Mechanics)

### Excellent (4.0-5.0)
- Sophisticated vocabulary used accurately and effectively
- Complex sentence structures handled well
- Minimal grammar/spelling errors
- Strong command of academic writing conventions
- Clear, fluid expression throughout (e.g., Essays #26, #28)

### Adequate (2.5-3.5)
- Basic but clear vocabulary
- Simple but generally correct sentence structures
- Some grammar/spelling errors but meaning remains clear
- Basic grasp of writing conventions
- Expression is understandable though may be awkward (e.g., Essays #3, #10)

### Weak (0.5-2.0)
- Limited vocabulary with frequent word choice errors
- Major grammar/syntax problems that impede understanding
- Numerous spelling/punctuation errors
- Poor grasp of writing conventions
- Expression frequently unclear or confusing (e.g., Essays #2, #4)

## Scoring Instructions
Given an essay and its prompt, evaluate it on each dimension and output a JSON object on a single line:
{"content": X, "organization": Y, "language": Z}
where each value is a float from 0.5 to 5.0 in 0.5 increments.