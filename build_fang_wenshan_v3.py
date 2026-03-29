#!/usr/bin/env python3
"""
Iteration 3: hand-curated fingerprint section 5 + regenerate skill + compare
"""
import os, json, re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    timeout=90
)
MODEL = "openai/gpt-4o"

# ─── Read v2 skill to reuse its fingerprint base and annotations ─────────────

V2_PATH = os.path.join(os.path.dirname(__file__), "skills", "fang_wenshan_skill_v2.md")
with open(V2_PATH) as f:
    v2_text = f.read()

# ─── Hand-curated section 5: three specific mechanisms ──────────────────────

HAND_CURATED_MECHANISMS = """
5. **独特句法机制（手工整理，三个核心机制）**

   **机制A：「惹」字连接法**
   用"惹"让无生命的物体主动牵连出情感链条，制造物-物-人的三重转接：
   - 「帘外芭蕉**惹**骤雨 / 门环**惹**铜绿 / 而我路过那江南小镇**惹**了你」（青花瓷）
   - 「是谁打翻前世柜 / **惹**尘埃是非」（发如雪）
   效果：情感显得不是主动选择，而是身不由己地被周遭事物"招惹"而来，距离感与宿命感并存。

   **机制B：具象量词包裹不可量的情感**
   不说"很多离愁"，而是把情感装进具体的容器/量词：
   - 「**一盏**离愁孤单伫立在窗口」（东风破）—— 离愁被装进一盏灯
   - 「**一壶**漂泊浪迹天涯难入喉」（东风破）—— 漂泊被装进一壶酒
   - 「我举杯饮尽了**风雪**」（发如雪）—— 风雪/痛苦可以被饮尽
   - 「**繁华如三千**东流水 / 我只取**一瓢**爱了解」（发如雪）—— 爱情用"一瓢"来量
   效果：情感被赋予了物理重量和体积，可以被拿起、饮下、放置，极度具体。

   **机制C：今古叠层（时间折叠）**
   在同一句/同一段里让现代视角与远古时间并置，造成时间的折叠感：
   - 「你隐藏在窑烧里**千年**的秘密」（青花瓷）—— 千年的物件承载当下的情感
   - 「**几番轮回** / 你锁眉哭红颜唤不回」（发如雪）—— 轮回（无限时间）与当下的锁眉
   - 「岁月在墙上剥落 / **看见小时候**」（东风破）—— 古旧痕迹直接通向个人童年
   - 「**伽蓝寺**听雨声盼永恒」（烟花易冷）—— 寺庙（历史空间）承载个人的等待
   效果：个人情感被嵌入历史尺度，显得沉甸甸，不是一时的感受而是永恒的宿命。
"""

# Replace section 5 in v2 fingerprint
# The v2 fingerprint is inside the skill file between "## 风格指纹" and "## 正例"
import re as _re

def replace_section5(skill_text, new_section5):
    # Find and replace the "5. 独特句法机制" block in the fingerprint
    pattern = r'(5\. \*\*独特句法机制.*?)(?=\n6\.|\n\n##)'
    replacement = new_section5.strip()
    new_text = _re.sub(pattern, replacement, skill_text, flags=_re.DOTALL)
    # Also update filename reference
    return new_text

v3_text = replace_section5(v2_text, HAND_CURATED_MECHANISMS)
# Update identity line
v3_text = v3_text.replace("# 方文山体 Generation Skill\n", "# 方文山体 Generation Skill (v3)\n")

# Update creation instructions to highlight mechanisms
OLD_INSTRUCTIONS = """## 创作指引

1. 阅读风格指纹，理解每一个维度的具体要求。
2. 研究正例中的具体句子：注意哪些词汇、哪种句法节奏、哪类意象的组合方式。
3. 用正例中出现的意象逻辑（而非正例的具体内容）来构建新作品。
4. 始终通过物象传递情感，不直白陈述「我很思念」「我很难过」。
5. 检查反例：确认你的输出中没有出现反例中被指出的那些写法。
6. 直接输出歌词/诗句，不需要解释你的创作思路。"""

NEW_INSTRUCTIONS = """## 创作指引

1. 仔细阅读风格指纹第5条的三个具体机制（A/B/C），这是与普通古风词最大的区别所在。
2. 在开始写之前，先选定你要使用哪种机制作为主骨架：
   - 想用「惹」字串联？先构建 物→物→人 的招惹链。
   - 想用具象量词？先决定把什么情感装进什么容器（"一盏XX"、"一壶XX"）。
   - 想用时间折叠？先锚定一个古旧物件/场所，再让现代情感从中涌现。
3. 研究正例中的意象：优先发明新的意象组合，不要复用正例中的具体词语（不要再写"夜未央""帘外"）。
4. 情感永远通过物象承载，不写「我很思念」「我很孤独」等直白陈述。
5. 直接输出歌词/诗句，不需要解释创作思路。"""

v3_text = v3_text.replace(OLD_INSTRUCTIONS, NEW_INSTRUCTIONS)

V3_PATH = os.path.join(os.path.dirname(__file__), "skills", "fang_wenshan_skill_v3.md")
with open(V3_PATH, "w") as f:
    f.write(v3_text)
print(f"v3 skill saved: {V3_PATH} ({len(v3_text.splitlines())} lines)")

# ─── Generation comparison: same prompts as before ──────────────────────────

test_prompts = [
    "用方文山体写一段关于「等待」的歌词，意象请用「茶」和「雨」，四行到八行即可，直接输出歌词。",
    "用方文山体写一段关于「离别」的歌词，以「船」和「桥」为核心意象，六行左右，直接输出歌词。",
    "用方文山体写一段关于「重逢」的歌词，以「旧宅」和「梅花」为意象，六行左右，直接输出歌词。",
]

V1_PATH = os.path.join(os.path.dirname(__file__), "skills", "fang_wenshan_skill.md")

for prompt_text in test_prompts:
    print(f"\n\n{'='*60}")
    print(f"PROMPT: {prompt_text}")
    print('='*60)

    # v1
    if os.path.exists(V1_PATH):
        with open(V1_PATH) as f:
            v1_content = f.read()
        r1 = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": v1_content},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7
        )
        print(f"\n[v1]:\n{r1.choices[0].message.content.strip()}")

    # v3
    with open(V3_PATH) as f:
        v3_content = f.read()
    r3 = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": v3_content},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.7
    )
    print(f"\n[v3]:\n{r3.choices[0].message.content.strip()}")
