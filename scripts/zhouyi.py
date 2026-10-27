#!/usr/bin/env python3
# Display name: I Ching
# 显示名称：周易卜卦
# Description: Cast an I Ching hexagram with three coins six times and return the primary and the changed hexagram; the reading is yours.
# 描述：三枚硬币掷六次起卦，交回本卦和变卦：每一爻的数、动爻、卦名，只起卦，不解读。
# Timeout: 10
# Clicall: no
# Parameters:
# {"type": "object", "properties": {
#   "question": {"type": "string", "description": "The question asked; echoed back, never used in the cast."}
# }}
"""Three-coin method: heads 3, tails 2; three coins sum to 6, 7, 8 or 9.

Odd is yang, even is yin. 6 (old yin) and 9 (old yang) are moving lines and
flip in the changed hexagram. Lines are cast from the bottom up.
"""

import json
import secrets
import sys

# 三爻自下而上，阳 1 阴 0
TRIGRAMS = {
    (1, 1, 1): ("乾", "天"), (0, 0, 0): ("坤", "地"),
    (1, 0, 0): ("震", "雷"), (0, 1, 1): ("巽", "风"),
    (0, 1, 0): ("坎", "水"), (1, 0, 1): ("离", "火"),
    (0, 0, 1): ("艮", "山"), (1, 1, 0): ("兑", "泽"),
}

# 文王卦序：KING_WEN[上卦][下卦]
ORDER = ["乾", "震", "坎", "艮", "坤", "巽", "离", "兑"]
KING_WEN_ROWS = [
    [1, 25, 6, 33, 12, 44, 13, 10],
    [34, 51, 40, 62, 16, 32, 55, 54],
    [5, 3, 29, 39, 8, 48, 63, 60],
    [26, 27, 4, 52, 23, 18, 22, 41],
    [11, 24, 7, 15, 2, 46, 36, 19],
    [9, 42, 59, 53, 20, 57, 37, 61],
    [14, 21, 64, 56, 35, 50, 30, 38],
    [43, 17, 47, 31, 45, 28, 49, 58],
]
KING_WEN = {up: dict(zip(ORDER, row)) for up, row in zip(ORDER, KING_WEN_ROWS)}

NAMES = (
    "乾 坤 屯 蒙 需 讼 师 比 小畜 履 泰 否 同人 大有 谦 豫 随 蛊 临 观 噬嗑 贲 剥 复 "
    "无妄 大畜 颐 大过 坎 离 咸 恒 遁 大壮 晋 明夷 家人 睽 蹇 解 损 益 夬 姤 萃 升 "
    "困 井 革 鼎 震 艮 渐 归妹 丰 旅 巽 兑 涣 节 中孚 小过 既济 未济"
).split()

KINDS = {6: ("老阴", "▅▅  ▅▅", " ×"), 7: ("少阳", "▅▅▅▅▅▅", ""),
         8: ("少阴", "▅▅  ▅▅", ""), 9: ("老阳", "▅▅▅▅▅▅", " ○")}
PLACES = ["初", "二", "三", "四", "五", "上"]


def fail(message):
    print(f"错误：{message}")
    sys.exit(1)


def line_name(index, yang):
    """初九、六二……上六。"""
    number = "九" if yang else "六"
    if index == 0:
        return "初" + number
    if index == 5:
        return "上" + number
    return number + PLACES[index]


def hexagram(bits):
    lower, lower_image = TRIGRAMS[tuple(bits[:3])]
    upper, upper_image = TRIGRAMS[tuple(bits[3:])]
    number = KING_WEN[upper][lower]
    name = NAMES[number - 1]
    full = f"{upper}为{upper_image}" if upper == lower else f"{upper_image}{lower_image}{name}"
    return f"第{number}卦 {full}（上{upper}下{lower}）"


def main():
    try:
        args = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        fail(f"参数不是 JSON：{exc}")
    question = str(args.get("question") or "").strip()

    rng = secrets.SystemRandom()
    casts = []
    for _ in range(6):
        coins = [rng.choice((3, 2)) for _ in range(3)]
        casts.append((coins, sum(coins)))

    primary = [total % 2 for _, total in casts]
    changed = [1 - b if total in (6, 9) else b for b, (_, total) in zip(primary, casts)]
    moving = [f"{line_name(i, primary[i])}（{'老阳变阴' if total == 9 else '老阴变阳'}）"
              for i, (_, total) in enumerate(casts) if total in (6, 9)]

    out = [f"问题：{question}"] if question else []
    out.append("掷币（正面 3、反面 2），卦象自上而下：")
    for i in reversed(range(6)):
        coins, total = casts[i]
        kind, bar, mark = KINDS[total]
        faces = "".join("正" if c == 3 else "反" for c in coins)
        out.append(f"{PLACES[i]}爻 {bar}{mark:2}  {faces} = {total} {kind}")
    out.append(f"本卦：{hexagram(primary)}")
    if moving:
        out.append(f"动爻：{'、'.join(moving)}")
        out.append(f"变卦：{hexagram(changed)}")
    else:
        out.append("动爻：无")
        out.append(f"变卦：{hexagram(changed)}（无动爻，变卦同本卦）")
    print("\n".join(out))


if __name__ == "__main__":
    main()
