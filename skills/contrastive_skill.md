# Essay Scoring Rubric

## Content Dimension

### High Score (4.0-5.0)
- Presents clear, specific main arguments with multiple supporting points
- Provides concrete, relevant examples and evidence
- Demonstrates deeper analytical thinking beyond surface observations
- Explores cause-effect relationships
- Considers multiple perspectives and broader implications

### Mid Score (2.5-3.5)
- Contains some specific supporting details but inconsistent development
- Shows partial analysis but may not fully explore implications
- Demonstrates basic organization of ideas but lacks sophisticated connections
- Mixes concrete and general statements

### Low Score (0.5-2.0)
- Relies on overly simple or obvious statements
- Lacks specific supporting evidence
- Shows limited development of ideas
- Uses vague language and general claims
- Demonstrates circular or superficial reasoning

## Organization Dimension

### High Score (4.0-5.0)
- Clear structural framework (introduction, body, conclusion)
- Strong topic sentences for each paragraph
- Explicit organizational markers and transitions
- Focused paragraphs developing one main idea
- Clear thesis statement previewing structure
- Logical progression between ideas

### Mid Score (2.5-3.5)
- Basic organizational structure with less consistent execution
- Some paragraph breaks but less clear focus
- Weaker transitions between ideas
- Less explicit signposting
- May drift from main topic within paragraphs

### Low Score (0.5-2.0)
- Unclear or absent overall structure
- Abrupt topic shifts without transitions
- Paragraphs mixing multiple ideas without focus
- Missing or unclear thesis statement
- Random presentation of ideas
- Incomplete development

## Language Dimension

### High Score (4.0-5.0)
- Generally correct grammar with only minor errors
- Appropriate academic vocabulary
- Complex sentence structures used effectively
- Proper use of transitional phrases
- Mostly correct spelling and punctuation
- Consistent formal academic tone

### Mid Score (2.5-3.5)
- Some grammar errors but meaning remains clear
- Mix of basic and academic vocabulary
- Simpler sentence structures with occasional complexity
- Basic transitions present but may be repetitive
- Some spelling and punctuation errors
- Inconsistent formal tone

### Low Score (0.5-2.0)
- Frequent grammar errors that impede meaning
- Simple, repetitive vocabulary
- Basic or fragmented sentence structures
- Minimal or incorrect transitions
- Multiple spelling/punctuation errors
- Informal tone and colloquial expressions
- Choppy, disconnected writing style

## Scoring Instructions
Given an essay and its prompt, evaluate it on each dimension and output a JSON object on a single line:
{"content": X, "organization": Y, "language": Z}
where each value is a float from 0.5 to 5.0 in 0.5 increments.