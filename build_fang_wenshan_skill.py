#!/usr/bin/env python3
"""
Track B: Style Induction for 方文山体 (Fang Wenshan Style)
Following SKILL_INDUCTION_PIPELINE.md Steps B2 → B4 → B5
"""
import os, json, re, textwrap
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    timeout=90
)
MODEL = "openai/gpt-4o"

# ─── Step B1: Gather Examples ───────────────────────────────────────────────

POSITIVES = [
    {
        "title": "青花瓷",
        "text": """素胚勾勒出青花笔锋浓转淡
瓶身描绘的牡丹一如你初妆
冉冉檀香透过窗心事我了然
宣纸上走笔至此搁一半

釉色渲染仕女图韵味被私藏
落款时却惦记着你
你隐藏在窑烧里千年的秘密
极细腻犹如绣花针落地

帘外芭蕉惹骤雨门环惹铜绿
而我路过那江南小镇惹了你
在泼墨山水画里你从墨色深处被隐去"""
    },
    {
        "title": "菊花台",
        "text": """你的泪光柔弱中带伤
惨白的月弯弯勾住过往
夜太漫长凝结成了霜
是谁在阁楼上冰冷地绝望

菊花残满地伤你的笑容已泛黄
花落人断肠我心事静静躺
北风乱夜未央你的影子剪不断
徒留我孤单在湖面成双

花已向晚飘落了灿烂
凋谢的世道上命运不堪
愁莫渡江秋心拆两半
怕你上不了岸一辈子摇晃"""
    },
    {
        "title": "东风破",
        "text": """一盏离愁孤单伫立在窗口
我在门后假装你人还没走
旧地如重游月圆更寂寞
夜半清醒的烛火不忍苛责我

一壶漂泊浪迹天涯难入喉
你走之后酒暖回忆思念瘦
水向东流时间怎么偷
花开就一次成熟我却错过

谁在用琵琶弹奏一曲东风破
岁月在墙上剥落看见小时候
犹记得那年我们都还小小的
你用背包装着所有我却背着你"""
    },
    {
        "title": "发如雪",
        "text": """狼牙月伊人憔悴
我举杯饮尽了风雪
是谁打翻前世柜
惹尘埃是非

缘字诀几番轮回
你锁眉哭红颜唤不回
纵然青史已经成灰
我爱不灭

繁华如三千东流水
我只取一瓢爱了解
只恋你化身的蝶

你发如雪纷飞了眼泪
我等待苍老了谁
红尘醉微醺的岁月
我用无悔刻永恒"""
    },
    {
        "title": "烟花易冷",
        "text": """雨纷纷旧故里草木深
我听闻你始终一个人
斑驳的城门盘踞着老树根
石板上回荡的是再等

伽蓝寺听雨声盼永恒
你在雨中我却在伽蓝觅不到你
繁华声遁入空门折煞了世人
梦偏冷辗转一生情债又牵

如你默认生死前
转山转水转佛前
等待着再见"""
    },
]

NEGATIVES = [
    {
        "title": "晴天（周杰伦自作词）",
        "text": """故事的小黄花从出生那年就飘着
童年的荡秋千随记忆一直晃到现在
所以那时候才说着要去哪里哪里
怎么人连做梦都那么拼

刮风这天我试过握着你手
但偏偏雨渐渐大到我看你不见
还要多久我才能在你身边
等到放晴的那天也许我会比较好一点

从前从前有个人爱你很久
但偏偏风渐渐把距离吹得好远
好不容易又能再多爱一天
但故事的最后你好像还是说了拜拜"""
    },
    {
        "title": "以父之名（周杰伦自作词）",
        "text": """微凉的晨露沾湿黑礼服
教堂的钟声响起了
我宣读誓言望着你嫩白的脸庄严

圣洁的气氛
我无法呼吸
恶魔的低语
不断侵蚀我心灵

闭上眼睛祈祷离别前夕
孤独的魂魄能否接受主的洗礼

以父之名判决我
世人啊你们听好
命运无法抗拒
说好的幸福呢"""
    },
]

# ─── Step B2: Extract Style Fingerprint ─────────────────────────────────────

def extract_fingerprint(positives, negatives):
    pos_block = "\n\n".join(
        f"【正例{i+1}：{p['title']}】\n{p['text']}" for i, p in enumerate(positives)
    )
    neg_block = "\n\n".join(
        f"【反例{i+1}：{n['title']}】\n{n['text']}" for i, n in enumerate(negatives)
    )
    prompt = f"""你是一位风格分析专家。你的任务是提炼下列正例的共同风格特征，并参考反例说明此风格刻意回避了什么。

{pos_block}

以下是明显不属于该风格的反例：

{neg_block}

请输出一份结构化的【风格指纹】，涵盖以下六个维度。每个维度必须具体到可以被另一位作者复现的操作层面——引用原文作为证据，命名具体句法模式，不接受"诗意""唯美""古典优雅"等空洞形容词：

1. 词汇与用语（哪些词汇类型高频出现？古汉语词汇如何与现代语法混搭？列出5个以上具体例词/例句）
2. 句法与结构（句式长短节奏规律、对仗/排比的具体形式、行内如何断句）
3. 意象体系（核心意象群是什么？意象之间如何转接？给出跨行意象链的具体例子）
4. 叙事视角与情感表达（情感通过什么被间接承载？举出3个"物象代替情感陈述"的具体例子）
5. 只有这位词人才会写的独特句法机制（这是最重要的部分）：
   列举3-5个在正例中反复出现、但反例中完全缺席的造句方式或修辞手法。
   每条必须：命名该机制 + 引用至少2处原文 + 说明它产生什么效果
6. 此风格刻意回避的东西（对照反例，指出具体缺席的句型、词汇类型、情感表达方式）"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return resp.choices[0].message.content.strip()


# ─── Step B4: Generate Style Annotations ────────────────────────────────────

def annotate_examples(fingerprint, positives, negatives):
    examples_block = "\n\n".join(
        f"【正例{i+1}：{p['title']}】\n{p['text']}" for i, p in enumerate(positives)
    )
    neg_block = "\n\n".join(
        f"【反例{i+1}：{n['title']}】\n{n['text']}" for i, n in enumerate(negatives)
    )
    prompt = f"""你正在为一个语言模型编写教学标注，目的是让模型通过观察这些例子学会生成特定风格的文字。

下面是已提炼的风格指纹（特别注意第5条"独特句法机制"）：
{fingerprint}

请为以下每首作品写标注：
- 正例：重点指出该作品中体现了风格指纹第5条"独特句法机制"的具体句子，引用原文，说明它用的是哪种机制以及产生了什么效果。2-3句。
- 反例：指出它最明显地违反了哪条机制，以及用了什么替代写法。1-2句。

{examples_block}

---
反例：
{neg_block}

请按以下格式输出（JSON）：
{{
  "positives": [
    {{"title": "...", "annotation": "..."}},
    ...
  ],
  "negatives": [
    {{"title": "...", "annotation": "..."}},
    ...
  ]
}}"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    raw = resp.choices[0].message.content.strip()
    # extract JSON
    m = re.search(r'\{[\s\S]+\}', raw)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return {"positives": [], "negatives": [], "raw": raw}


# ─── Step B5: Assemble Skill File ────────────────────────────────────────────

def assemble_skill(fingerprint, positives, negatives, annotations):
    pos_ann = {a['title']: a['annotation'] for a in annotations.get('positives', [])}
    neg_ann = {a['title']: a['annotation'] for a in annotations.get('negatives', [])}

    lines = []
    lines.append("# 方文山体 Generation Skill\n")
    lines.append("你正在以方文山的词风创作歌词或诗句。")
    lines.append("方文山体最核心的特质：用古典意象和器物作为情感的载体，从不直接说出情感本身。\n")

    lines.append("## 风格指纹\n")
    lines.append(fingerprint)
    lines.append("")

    lines.append("## 正例\n")
    for p in positives:
        lines.append(f"### 正例：{p['title']}")
        lines.append(p['text'])
        ann = pos_ann.get(p['title'], '')
        if ann:
            lines.append(f"\n**风格特征：** {ann}")
        lines.append("")

    lines.append("## 反例（此风格刻意回避的写法）\n")
    for n in negatives:
        lines.append(f"### 反例：{n['title']}")
        lines.append(n['text'])
        ann = neg_ann.get(n['title'], '')
        if ann:
            lines.append(f"\n**缺失了什么：** {ann}")
        lines.append("")

    lines.append("## 创作指引\n")
    lines.append("1. 阅读风格指纹，理解每一个维度的具体要求。")
    lines.append("2. 研究正例中的具体句子：注意哪些词汇、哪种句法节奏、哪类意象的组合方式。")
    lines.append("3. 用正例中出现的意象逻辑（而非正例的具体内容）来构建新作品。")
    lines.append("4. 始终通过物象传递情感，不直白陈述「我很思念」「我很难过」。")
    lines.append("5. 检查反例：确认你的输出中没有出现反例中被指出的那些写法。")
    lines.append("6. 直接输出歌词/诗句，不需要解释你的创作思路。")

    return "\n".join(lines)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("Step B2: Extracting style fingerprint...")
    fingerprint = extract_fingerprint(POSITIVES, NEGATIVES)
    print("\n=== STYLE FINGERPRINT ===")
    print(fingerprint)

    print("\n\nStep B4: Generating style annotations...")
    annotations = annotate_examples(fingerprint, POSITIVES, NEGATIVES)
    if 'raw' in annotations:
        print("[Warning] JSON parse failed, raw output:")
        print(annotations['raw'][:500])
    else:
        print(f"  Got {len(annotations.get('positives',[]))} positive annotations, "
              f"{len(annotations.get('negatives',[]))} negative annotations")

    print("\nStep B5: Assembling skill file...")
    skill_text = assemble_skill(fingerprint, POSITIVES, NEGATIVES, annotations)

    out_path = os.path.join(os.path.dirname(__file__), "skills", "fang_wenshan_skill_v2.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(skill_text)
    print(f"\nSkill saved to: {out_path}")
    print(f"Lines: {len(skill_text.splitlines())}")

    # Load v1 for comparison
    v1_path = os.path.join(os.path.dirname(__file__), "skills", "fang_wenshan_skill.md")

    test_prompts = [
        "用方文山体写一段关于「等待」的歌词，意象请用「茶」和「雨」，四行到八行即可，直接输出歌词。",
        "用方文山体写一段关于「离别」的歌词，以「船」和「桥」为核心意象，六行左右，直接输出歌词。",
    ]

    for prompt_text in test_prompts:
        print(f"\n\n=== 测试：{prompt_text[:20]}... ===")

        # Zero-shot baseline
        zero = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.7
        )
        print(f"\n[Zero-shot]:\n{zero.choices[0].message.content.strip()}")

        # v1 skill
        if os.path.exists(v1_path):
            with open(v1_path) as f:
                v1_content = f.read()
            r1 = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": v1_content},
                    {"role": "user", "content": prompt_text}
                ],
                temperature=0.7
            )
            print(f"\n[Skill v1]:\n{r1.choices[0].message.content.strip()}")

        # v2 skill
        with open(out_path) as f:
            v2_content = f.read()
        r2 = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": v2_content},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7
        )
        print(f"\n[Skill v2]:\n{r2.choices[0].message.content.strip()}")


if __name__ == "__main__":
    main()
