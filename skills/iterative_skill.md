Here's the revised rubric with improvements to better handle these error cases:

# Comprehensive Essay Scoring Rubric
*For evaluating academic essays on three key dimensions*

## Scoring Scale
Each dimension is scored from 0.5-5.0 points using 0.5 increments:
- 4.0-5.0: Excellent
- 2.5-3.5: Adequate 
- 0.5-2.0: Weak
- 0: Never used (all submissions receive minimum 0.5)

## Content (5 points)
*Evaluates argument development, evidence, and relevance*

**Excellent (4.0-5.0)**
- Clear argument addressing prompt theme, even if not directly
- 2-3 supporting points with examples
- Shows critical thinking and analysis
- Real-world applications or scenarios
- Demonstrates understanding of core concepts
- Topic engagement evident even if misaligned

**Adequate (2.5-3.5)**
- Identifiable main idea related to general topic
- At least 1 supporting example
- Shows basic reasoning
- Some concrete details
- Partial prompt alignment acceptable
- Demonstrates basic comprehension

**Weak (0.5-2.0)**
- Any attempt to discuss related themes
- Basic ideas present, even if off-topic
- Minimal but genuine attempt at content
- Writing shows student engagement
- Default score for technical submission issues

## Organization (5 points)
*Evaluates structure, flow, and coherence*

**Excellent (4.0-5.0)**
- Clear organizational pattern
- Logical idea progression
- Effective paragraph structure
- Ideas connect, even if imperfectly
- Shows intentional structuring

**Adequate (2.5-3.5)**
- Basic organization apparent
- Some logical ordering
- Attempt at paragraphing
- Ideas generally follow
- Structure supports meaning

**Weak (0.5-2.0)**
- Any evidence of organization
- Basic grouping of ideas
- Minimal structural elements
- Default score for technical issues
- Partial submission acceptable

## Language (5 points)
*Evaluates grammar, vocabulary, and writing mechanics*

**Excellent (4.0-5.0)**
- Clear communication despite errors
- Vocabulary supports meaning
- Generally comprehensible
- ESL errors acceptable
- Shows language competence

**Adequate (2.5-3.5)**
- Basic meaning conveyed
- Functional vocabulary
- Communication achieved
- ESL features present
- Reader can follow main ideas

**Weak (0.5-2.0)**
- Any meaningful English use
- Basic vocabulary present
- Partially comprehensible
- Default score for technical issues
- Attempt at expression evident

## Important Scoring Notes
- Technical submission issues (including "nan") default to 2.5 for all dimensions
- Essays showing topic understanding receive minimum 3.0 regardless of format
- Off-topic but coherent essays receive minimum 2.0
- Previous student performance should inform scoring of incomplete submissions
- Consider ESL context when evaluating language
- All genuine attempts receive minimum 0.5 points

## Scoring Instructions
Given an essay and its prompt, evaluate it on each dimension and output a JSON object on a single line:
{"content": X, "organization": Y, "language": Z}
where each value is a float from 0.5 to 5.0 in 0.5 increments.