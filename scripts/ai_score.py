#!/usr/bin/env python3
"""
AI 味检测器(反 AI 检测自检工具)

对一篇 Markdown 文章做启发式扫描,从以下维度给出"AI 味"评分(0-100),
越高越像 AI 生成,越低越像真人写作。

维度(与权重):
  1. burstiness(句长方差)   30%  —— 真人句长抖动大,AI 平滑
  2. phrase_hits(AI 套话)   30%  —— 命中 AI 高频句式 / 套话的次数
  3. vocab_hits(AI 词汇)    20%  —— 命中 AI 高频名词的次数
  4. structural_perfection  10%  —— 首先/其次/最后 等教科书结构
  5. punctuation_flatness   10%  —— 标点单调(几乎只有句号逗号)

用法:
    python3 ai_score.py article.md
    python3 ai_score.py article.md --json         # 输出 JSON
    python3 ai_score.py article.md --threshold 40 # 阈值,高于阈值 exit 1

返回:
    exit 0 通过(分数 < 阈值)
    exit 1 失败(分数 >= 阈值,建议重写)

注意:这只是启发式检测,不替代真实的第三方检测器(GPTZero / 朱雀 /
腾讯 AI 检测),但可以作为发布前的快速 gate 拦住最明显的 AI 味。
"""

import re
import sys
import json
import argparse
import statistics
from pathlib import Path

# 默认失败阈值：总分 >= 该值视为"AI 味过重"。
# check_ai_score()、CLI --threshold 默认值和 publish.py 均应引用此常量，保持一致。
DEFAULT_THRESHOLD: float = 45.0


# ---------- 黑名单 ----------

# AI 高频套话句式(正则)
AI_PHRASES = [
    r"首先[,，].{0,8}其次[,，].{0,10}最后",
    r"首先[,，].{0,8}其次[,，].{0,10}再次",
    r"不仅.{0,10}而且",
    r"一方面.{1,15}另一方面",
    r"值得一提的是",
    r"值得注意的是",
    r"与此同时",
    r"无独有偶",
    r"不可否认",
    r"毋庸置疑",
    r"综上所述",
    r"总而言之",
    r"总的来说",
    r"由此可见",
    r"众所周知",
    r"不难发现",
    r"显而易见",
    r"在.{1,15}的背景下",
    r"随着.{1,20}的发展",
    r"随着.{1,20}的不断",
    r"让我们一起来",
    r"让我们共同",
    r"归根结底",
    r"无论如何",
    r"从某种意义上(说|讲)",
    r"在当今社会",
    r"进入新时代",
    r"在.{1,10}时代",
    r"站在.{1,10}的角度",
    r"为.{1,10}提供了.{1,10}可能",
    r"打开了.{1,10}的大门",
    r"开启了.{1,10}的篇章",
    r"翻开了.{1,10}新的一页",
    r"具有(重要|深远|里程碑)的意义",
    r"产生了(深远|重大|巨大)的影响",
    # --- 系动词回避: AI 用"堪称/充当/扮演"替代"是/就是" ---
    r"(堪称|充当|扮演)(.{2,10})的?(利器|桥梁|典范|标志|象征|证明|基石|核心|关键|驱动力|催化剂)",
    r"作为.{2,10}的?(有力|最佳|完美|重要|核心|关键|不可或缺)?(证明|象征|标志|体现|典范|代表)",
    # --- 预告式宣告 ---
    r"接下来.{0,6}(让我们|我们|将)(一起|深入|详细|共同)",
    r"下面.{0,4}(让我们|我们|将)(一起|深入|详细|共同)",
    r"接下来我们来(看看|聊聊|谈谈|分析|探讨)",
    r"下面我们就来(看看|聊聊|谈谈|分析|探讨)",
    # --- 虚假对比范围 / 假史诗排比 ---
    r"从.{2,8}到.{2,8}(，|,)从.{2,8}到.{2,8}",
    r"从小白到(大佬|大神|专家)",
    r"从入门到精通",
    r"从零到一",
    r"从.{2,6}走向.{2,6}",
    # --- 营销化 / 广告腔 ---
    r"令人叹为观止",
    r"拥有丰富.{0,6}(底蕴|文化|内涵|传承)",
    r"坐落在.{0,10}(中心|腹地|核心)",
    r"作为.{2,10}的焦点",
    r"无缝(衔接|连接|融合|对接)",
    r"直观且充满活力",
    r"丰富且(充满|极具|富有)",
    # --- 空洞正面结论 ---
    r"(总之|总的来说|总而言之).{0,10}(值得期待|前景广阔|未来可期|拭目以待|令人期待)",
    r"相信在不久的将来",
    r"让我们(拭目以待|共同期待)",
    r"在新时代的(浪潮|洪流|征程)中",
    r"开启.{2,10}(新(篇章|征程|纪元|时代)|下一个.{2,6})",
]

# AI 高频名词 / 形容词(整篇密集出现即扣分)
AI_VOCAB = [
    "赋能", "打造", "聚焦", "深度融合", "生态", "闭环", "链路", "抓手",
    "价值链", "护城河", "方法论", "底层逻辑", "生态位", "结构化思维",
    "提升效率", "助力", "全链路", "一站式", "端到端", "量变到质变",
    "引领", "颠覆", "革命性", "前所未有", "核心竞争力", "范式", "新范式",
    "降本增效", "数字化转型", "智能化", "生态体系", "产业升级",
    "破局", "出圈", "破圈", "沉淀", "赋予", "深耕", "蓝图", "新篇章",
    # --- 从 humanizer-zh 合并的高频 AI 词 ---
    "玩法", "愿景", "重新定义", "开辟新赛道", "加速器", "原生",
    "新物种", "新格局", "新态势", "新起点", "新征程",
    "深度整合", "全面赋能", "精细化", "深度优化",
    "场景化", "多元化", "全方位", "立体化", "体系化", "系统化",
    "持续迭代",
]

# 中文长文中常见的模型化句法。这里按“提醒”处理，不做绝对禁用：
# 正常、有事实依据的对比句和行业术语仍可保留。
PIVOT_PATTERNS = [
    r"(?:并)?不是[^。！？\n]{1,90}而是",
    r"并非[^。！？\n]{1,90}而是",
    r"不在于[^。！？\n]{1,90}而在于",
    r"与其说[^。！？\n]{1,90}(?:不如|毋宁|倒不如)",
    r"你以为[^。！？\n]{1,70}(?:其实|实际|结果)",
    r"看似[^。！？\n]{1,70}(?:其实|实际|实则)",
    r"[^，。！？\n]{1,16}不重要，(?:重要|要紧)的是",
]

NOMINALIZATION_PATTERNS = [
    r"进行(?:了|一次|一场|着)?[^。，！？\n]{0,12}(?:调整|优化|升级|分析|讨论|沟通|梳理|复盘|迭代|探索|尝试|思考|规划|布局)",
    r"实现了?[^。，！？\n]{0,16}的?[^。，！？\n]{0,8}(?:提升|增长|突破|转变|跃升|落地)",
    r"完成了?对[^。，！？\n]{0,18}的",
    r"起到了?[^。，！？\n]{0,14}的?作用",
]

CONJUNCTIONS = (
    "因为", "所以", "但是", "然而", "同时", "此外", "而且", "并且", "因此", "不仅",
)

REPEATED_OPENERS = (
    "其实", "不过", "当然", "所以", "但是", "后来", "当时", "很多人", "问题是", "更重要的是", "说到这里",
)


def _strip_markdown(md_text: str) -> str:
    """去掉 markdown 语法,只保留正文文字,用于句子级分析。"""
    text = md_text
    # 代码块
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    # 行内代码
    text = re.sub(r"`[^`]+`", " ", text)
    # 图片 / 链接
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # 自定义行内标记(保留文字内容)
    text = re.sub(r"==([^=\n]+)==", r"\1", text)
    text = re.sub(r"\+\+([^+\n]+)\+\+", r"\1", text)
    text = re.sub(r"%%([^%\n]+)%%", r"\1", text)
    text = re.sub(r"&&([^&\n]+)&&", r"\1", text)
    text = re.sub(r"!!([^!\n]+)!!", r"\1", text)
    text = re.sub(r"@@([^@\n]+)@@", r"\1", text)
    text = re.sub(r"\^\^([^\^\n]+)\^\^", r"\1", text)
    # 加粗 / 斜体
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*\n]+)\*", r"\1", text)
    # 标题符号 / 引用符号 / 列表符号
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    # 表格
    text = re.sub(r"^\|.*\|$", " ", text, flags=re.MULTILINE)
    return text.strip()


def _split_sentences(text: str) -> list:
    """按中文/英文标点切句。"""
    parts = re.split(r"(?<=[。!?!?;;])", text)
    return [p.strip() for p in parts if p.strip()]


# ---------- 各维度打分 ----------

def score_burstiness(sentences: list) -> tuple:
    """
    真人写作句长分布有"突发性"(burstiness)。
    计算句长的变异系数(CV = stdev / mean),CV 越大越像真人。
    转换为 0-100 的 AI 味分数(CV 越小分越高)。
    """
    if len(sentences) < 5:
        return 50.0, {"cv": None, "reason": "too_few_sentences"}
    lengths = [len(s) for s in sentences]
    mean = statistics.mean(lengths)
    stdev = statistics.stdev(lengths) if len(lengths) > 1 else 0
    cv = stdev / mean if mean else 0
    # CV 0.3 以下 = 非常平滑(AI 味 90),CV 0.8 以上 = 抖动大(AI 味 10)
    if cv <= 0.3:
        ai = 90
    elif cv >= 0.8:
        ai = 10
    else:
        ai = 90 - (cv - 0.3) * (80 / 0.5)
    return round(ai, 1), {
        "sentence_count": len(sentences),
        "mean_length": round(mean, 1),
        "stdev": round(stdev, 1),
        "cv": round(cv, 3),
    }


def score_phrases(text: str) -> tuple:
    """AI 套话命中率(按 span 去重,避免同一段文本被多个重叠模式重复计数)。"""
    seen_spans = {}  # (start, end) -> matched text
    for pat in AI_PHRASES:
        for m in re.finditer(pat, text):
            span = (m.start(), m.end())
            # 只保留首次命中(不同 pattern 命中同一 span 算一次)
            if span not in seen_spans:
                seen_spans[span] = m.group(0)
    # 再做一轮重叠消除:若 span A 完全被 span B 包含,则丢弃 A
    spans = sorted(seen_spans.keys(), key=lambda s: (s[0], -s[1]))
    kept = []
    for span in spans:
        contained = any(
            other != span and other[0] <= span[0] and other[1] >= span[1]
            for other in seen_spans.keys()
        )
        if not contained:
            kept.append(span)
    hits = [seen_spans[s] for s in kept]
    # 每命中一次扣 15 分(从 0 起累加,上限 100)
    ai = min(100, len(hits) * 15)
    return round(float(ai), 1), {"hit_count": len(hits), "samples": hits[:8]}


def score_vocab(text: str) -> tuple:
    """AI 高频词密度。"""
    hits = {}
    for w in AI_VOCAB:
        c = text.count(w)
        if c > 0:
            hits[w] = c
    total = sum(hits.values())
    # 每 1000 字允许最多 2 个,再多按比例扣分
    char_count = max(1, len(text))
    density = total / (char_count / 1000)
    if density <= 2:
        ai = density * 15  # 0-30
    elif density <= 5:
        ai = 30 + (density - 2) * 15  # 30-75
    else:
        ai = min(100, 75 + (density - 5) * 5)
    return round(float(ai), 1), {
        "total_hits": total,
        "density_per_1k": round(density, 2),
        "top": sorted(hits.items(), key=lambda x: -x[1])[:10],
    }


def score_structural_perfection(text: str) -> tuple:
    """检测教科书式枚举结构。"""
    bad = [
        r"第一[,，、].{0,80}第二[,，、].{0,80}第三",
        r"一[是、][^。]{0,60}二[是、][^。]{0,60}三[是、]",
    ]
    hits = 0
    for pat in bad:
        hits += len(re.findall(pat, text))
    ai = min(100, hits * 35)
    return round(float(ai), 1), {"hit_count": hits}


def score_punctuation_flatness(text: str) -> tuple:
    """检测标点单调度。只做低权重提醒，不鼓励为了得分硬加标点。"""
    chars = len(text)
    flavor = 0
    flavor += text.count("——")
    flavor += min(3, text.count("…"))
    flavor += text.count("?") + text.count("？")
    flavor += min(3, text.count("!") + text.count("！"))
    flavor += min(4, text.count("(") + text.count("（"))
    # 每 1000 字只期望少量自然变化；达到后不继续奖励堆标点。
    expected = max(chars, 400) / 1000 * 2
    ratio = flavor / expected if expected else 0
    if ratio >= 1:
        ai = 10
    elif ratio >= 0.5:
        ai = 35
    elif ratio >= 0.2:
        ai = 60
    else:
        ai = 80
    return round(float(ai), 1), {
        "flavor_points": flavor,
        "expected": round(expected, 1),
        "ratio": round(ratio, 2),
        "note": "仅作提醒，不要为降分硬加标点",
    }


def score_prose_patterns(text: str) -> tuple:
    """检测中文长文的翻案腔、名词化、连词过密和段落模板化。"""
    pivot_hits = []
    for pattern in PIVOT_PATTERNS:
        pivot_hits.extend(m.group(0) for m in re.finditer(pattern, text))

    nominal_hits = []
    for pattern in NOMINALIZATION_PATTERNS:
        nominal_hits.extend(m.group(0) for m in re.finditer(pattern, text))

    char_count = max(1, len(text))
    conjunction_count = sum(text.count(word) for word in CONJUNCTIONS)
    conjunction_density = conjunction_count / (char_count / 1000)

    paragraphs = [
        re.sub(r"\s+", " ", block).strip()
        for block in re.split(r"\n\s*\n", text)
        if len(re.findall(r"[\u4e00-\u9fff]", block)) >= 4
    ]

    opener_counts = {}
    for paragraph in paragraphs:
        value = paragraph.lstrip("“‘\"（(")
        for opener in REPEATED_OPENERS:
            if value.startswith(opener):
                opener_counts[opener] = opener_counts.get(opener, 0) + 1
                break
    repeated_openers = {k: v for k, v in opener_counts.items() if v >= 4}

    short_streaks = 0
    streak = 0
    for paragraph in paragraphs:
        han = len(re.findall(r"[\u4e00-\u9fff]", paragraph))
        sentences = len(re.findall(r"[。！？!?]", paragraph))
        if han <= 24 and sentences <= 1:
            streak += 1
            if streak == 4:
                short_streaks += 1
        else:
            streak = 0

    score = min(30, len(pivot_hits) * 8)
    score += min(20, len(nominal_hits) * 5)
    if conjunction_density > 8:
        score += min(25, (conjunction_density - 8) * 4)
    score += min(15, sum(v - 3 for v in repeated_openers.values()) * 5)
    score += min(10, short_streaks * 10)

    return round(min(100.0, float(score)), 1), {
        "pivot_count": len(pivot_hits),
        "pivot_samples": pivot_hits[:6],
        "nominalization_count": len(nominal_hits),
        "nominalization_samples": nominal_hits[:6],
        "conjunction_density_per_1k": round(conjunction_density, 2),
        "repeated_openers": repeated_openers,
        "short_paragraph_streaks": short_streaks,
        "note": "这些是语境提醒，不是绝对禁用项",
    }


# ---------- 总评 ----------

# 长文(news)权重：把标点降为低权重提醒，新增中文句法与段落模式。
WEIGHTS_NEWS = {
    "burstiness": 0.25,
    "phrases": 0.25,
    "vocab": 0.15,
    "structural": 0.10,
    "punctuation": 0.05,
    "prose_patterns": 0.20,
}

# 短文(newspic 贴图)用的精简权重。
WEIGHTS_NEWSPIC = {
    "burstiness": 0.0,
    "phrases": 0.50,
    "vocab": 0.30,
    "structural": 0.0,
    "punctuation": 0.10,
    "prose_patterns": 0.10,
}

# 向后兼容:现有代码从本模块 `from ai_score import WEIGHTS` 的地方仍然能读到长文权重
WEIGHTS = WEIGHTS_NEWS


def _weights_for(mode: str) -> dict:
    if mode == "newspic":
        return WEIGHTS_NEWSPIC
    return WEIGHTS_NEWS


def analyze(md_text: str, mode: str = "news") -> dict:
    """
    对一段 Markdown(或纯文本)做 AI 味打分。

    Args:
        md_text: 原文
        mode:  "news"(默认,长文 5 维)或 "newspic"(贴图短文本,phrases + vocab + punctuation)
    """
    plain = _strip_markdown(md_text)
    sentences = _split_sentences(plain)

    b_score, b_det = score_burstiness(sentences)
    p_score, p_det = score_phrases(plain)
    v_score, v_det = score_vocab(plain)
    s_score, s_det = score_structural_perfection(plain)
    pu_score, pu_det = score_punctuation_flatness(plain)
    pr_score, pr_det = score_prose_patterns(plain)

    weights = _weights_for(mode)
    total = (
        b_score * weights["burstiness"]
        + p_score * weights["phrases"]
        + v_score * weights["vocab"]
        + s_score * weights["structural"]
        + pu_score * weights["punctuation"]
        + pr_score * weights["prose_patterns"]
    )

    verdict = (
        "🟢 PASS (真人味)"
        if total < 35
        else ("🟡 WARN (有 AI 味,建议改)" if total < 55 else "🔴 FAIL (AI 味太重,必须重写)")
    )

    return {
        "total_ai_score": round(total, 1),
        "verdict": verdict,
        "mode": mode,
        "char_count": len(plain),
        "sentence_count": len(sentences),
        "dimensions": {
            "burstiness":   {"score": b_score,  "detail": b_det},
            "phrases":      {"score": p_score,  "detail": p_det},
            "vocab":        {"score": v_score,  "detail": v_det},
            "structural":   {"score": s_score,  "detail": s_det},
            "punctuation":  {"score": pu_score, "detail": pu_det},
            "prose_patterns": {"score": pr_score, "detail": pr_det},
        },
        "weights": weights,
    }


def check_ai_score(
    md_content: str,
    threshold: float = DEFAULT_THRESHOLD,
    mode: str = "news",
) -> tuple:
    """
    库入口:对 md 内容做 AI 味检测。

    Args:
        md_content: Markdown 原文
        threshold: 失败阈值(total_score >= threshold 视为失败)
        mode: "news"(长文)或 "newspic"(贴图短文本,只看 phrases/vocab/punctuation)

    Returns:
        (passed, report)
          passed: bool,total_score < threshold 时为 True
          report: dict,包含:
            - total_score: float  总分 0-100
            - mode: str
            - dimensions: dict    各维度原始分(未加权)
                - burstiness / phrases / vocab / structural / punctuation / prose_patterns
            - hit_phrases: list[str]  命中的 AI 套话样本
            - hit_vocab:   list[str]  命中的 AI 词汇样本
            - threshold:   float
    """
    full = analyze(md_content, mode=mode)
    dims = full["dimensions"]
    hit_phrases = list(dims["phrases"]["detail"].get("samples", []))
    hit_vocab = [w for w, _ in dims["vocab"]["detail"].get("top", [])]

    report = {
        "total_score": full["total_ai_score"],
        "mode": full.get("mode", mode),
        "dimensions": {
            "burstiness":  dims["burstiness"]["score"],
            "phrases":     dims["phrases"]["score"],
            "vocab":       dims["vocab"]["score"],
            "structural":  dims["structural"]["score"],
            "punctuation": dims["punctuation"]["score"],
            "prose_patterns": dims["prose_patterns"]["score"],
        },
        "hit_phrases": hit_phrases,
        "hit_vocab":   hit_vocab,
        "prose_detail": dims["prose_patterns"]["detail"],
        "threshold":   float(threshold),
    }
    passed = report["total_score"] < threshold
    return passed, report


def _pretty_print(report: dict):
    print("=" * 60)
    print(f" AI 味检测报告  —— {report['verdict']}")
    print("=" * 60)
    mode = report.get("mode", "news")
    print(f"模式: {mode}  (news=长文, newspic=贴图短文)")
    print(f"总分: {report['total_ai_score']} / 100  (0 = 纯真人, 100 = 纯 AI)")
    print(f"字数: {report['char_count']}  句数: {report['sentence_count']}")
    print("-" * 60)
    weights = report.get("weights", WEIGHTS)
    for name, d in report["dimensions"].items():
        w = weights.get(name, 0)
        suffix = "  [跳过]" if w == 0 else ""
        print(f"  [{name:13s}] 分数={d['score']:>5}  权重={int(w*100)}%{suffix}")
        det = d["detail"]
        if name == "phrases" and det.get("hit_count"):
            print(f"      命中 {det['hit_count']} 次 AI 套话:")
            for s in det.get("samples", []):
                print(f"        · {s}")
        elif name == "vocab" and det.get("total_hits"):
            top = det.get("top", [])
            if top:
                top_str = ", ".join(f"{w}×{c}" for w, c in top)
                print(f"      AI 词密度 {det['density_per_1k']}/千字: {top_str}")
        elif name == "burstiness" and det.get("cv") is not None:
            print(f"      句长均值 {det['mean_length']} 字,CV={det['cv']}")
        elif name == "punctuation":
            print(f"      人味标点 {det.get('flavor_points', 0)} 次,期望 {det.get('expected', 0)}（仅提醒，不要硬加）")
        elif name == "prose_patterns":
            print(
                "      中文句法提醒: "
                f"翻案腔 {det.get('pivot_count', 0)}，"
                f"名词化 {det.get('nominalization_count', 0)}，"
                f"连词密度 {det.get('conjunction_density_per_1k', 0)}/千字，"
                f"短句段连排 {det.get('short_paragraph_streaks', 0)}"
            )
            for s in det.get("pivot_samples", [])[:4]:
                print(f"        · 疑似翻案腔: {s}")
            for s in det.get("nominalization_samples", [])[:3]:
                print(f"        · 疑似名词化: {s}")
            if det.get("repeated_openers"):
                print(f"        · 段首重复: {det['repeated_openers']}")
        elif name == "structural" and det.get("hit_count"):
            print(f"      教科书枚举命中 {det['hit_count']} 次")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="AI 味检测器")
    parser.add_argument("input", help="Markdown 文件路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"失败阈值(默认 {DEFAULT_THRESHOLD})。总分 >= 阈值则 exit 1",
    )
    parser.add_argument(
        "--mode",
        choices=["news", "newspic"],
        default="news",
        help="检测模式: news(长文,默认)/ newspic(贴图短文本,只看 phrases+vocab+punctuation)",
    )
    args = parser.parse_args()

    md = Path(args.input).read_text(encoding="utf-8")
    # 走和库 API 相同的 check_ai_score 路径,保证 CLI/库行为一致。
    passed, _ = check_ai_score(md, threshold=args.threshold, mode=args.mode)
    full = analyze(md, mode=args.mode)  # 用于详细打印(库 API 只返回简表)

    if args.json:
        print(json.dumps(full, ensure_ascii=False, indent=2))
    else:
        _pretty_print(full)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
