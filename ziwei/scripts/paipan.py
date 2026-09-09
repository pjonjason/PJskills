#!/usr/bin/env python3
"""紫微斗数排盘脚本 — 基于 py-iztro 精确排盘引擎。

严禁凭记忆推算星曜位置！必须运行本脚本获得准确命盘后再解读。

用法:
    python paipan.py --date 2000-8-16 --hour 3 --gender 女
    python paipan.py --date 1990-1-1 --hour 14 --gender 男 --horoscope 2026-9-9
    python paipan.py --lunar --date 2000-7-17 --hour 3 --gender 女

参数:
    --date       出生日期 YYYY-M-D（默认阳历；加 --lunar 则为农历）
    --hour       出生时刻（0-23 的钟点数，如 14 表示下午2点；23 为晚子时）
    --gender     男 / 女
    --horoscope  可选：查看某日期所在的大限与流年四化（如 2026-9-9）
    --leap       农历闰月时加此参数
依赖: pip install py-iztro
"""
import argparse
import sys

try:
    from py_iztro import Astro
except ImportError:
    print("缺少依赖，请先运行: pip install py-iztro --break-system-packages")
    sys.exit(1)

BRANCH_ORDER = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
MUTAGEN_MARK = {"禄": "化禄", "权": "化权", "科": "化科", "忌": "化忌"}


def hour_to_index(hour: int) -> int:
    """钟点(0-23) → iztro 时辰索引(0-12)。0点=早子时(0)，23点=晚子时(12)。"""
    if hour == 23:
        return 12
    return (hour + 1) // 2


HOUR_NAMES = ["早子时(0点)", "丑时(1-3点)", "寅时(3-5点)", "卯时(5-7点)", "辰时(7-9点)",
              "巳时(9-11点)", "午时(11-13点)", "未时(13-15点)", "申时(15-17点)",
              "酉时(17-19点)", "戌时(19-21点)", "亥时(21-23点)", "晚子时(23点)"]


def fmt_star(s):
    parts = [s.name]
    if s.brightness:
        parts.append(f"({s.brightness})")
    if s.mutagen:
        parts.append(f"[{MUTAGEN_MARK.get(s.mutagen, s.mutagen)}]")
    return "".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--hour", type=int, required=True)
    ap.add_argument("--gender", required=True, choices=["男", "女"])
    ap.add_argument("--lunar", action="store_true")
    ap.add_argument("--leap", action="store_true")
    ap.add_argument("--horoscope", default=None)
    args = ap.parse_args()

    astro = Astro()
    tidx = hour_to_index(args.hour)
    if args.lunar:
        chart = astro.by_lunar(args.date, tidx, args.gender, args.leap, True)
    else:
        chart = astro.by_solar(args.date, tidx, args.gender, True)

    print("=" * 62)
    print("【基本信息】")
    print(f"  阳历: {chart.solar_date}   农历: {chart.lunar_date}")
    print(f"  干支: {chart.chinese_date}")
    print(f"  性别: {chart.gender}   时辰: {HOUR_NAMES[tidx]}")
    print(f"  五行局: {chart.five_elements_class}   命主: {chart.soul}   身主: {chart.body}")
    print(f"  命宫地支: {chart.earthly_branch_of_soul_palace}   身宫地支: {chart.earthly_branch_of_body_palace}")
    print("=" * 62)
    print("【十二宫】(亮度: 庙>旺>得>利>平>不>陷; [化X]为生年四化)")

    for p in chart.palaces:
        body_mark = " ★身宫" if p.is_body_palace else ""
        majors = "、".join(fmt_star(s) for s in p.major_stars) or "（无主星，借对宫）"
        minors = "、".join(fmt_star(s) for s in p.minor_stars)
        adj = "、".join(s.name for s in p.adjective_stars)
        lo, hi = p.decadal.range
        pname = p.name if p.name.endswith("宫") else p.name + "宫"
        print(f"\n  ◆ {pname} [{p.heavenly_stem}{p.earthly_branch}]{body_mark}  大限:{lo}-{hi}岁")
        print(f"    主星: {majors}")
        if minors:
            print(f"    辅星: {minors}")
        if adj:
            print(f"    杂曜: {adj}")
        print(f"    长生十二神: {p.changsheng12}  博士十二神: {p.boshi12}")

    if args.horoscope:
        h = chart.horoscope(args.horoscope)
        print("\n" + "=" * 62)
        print(f"【运限】查询日期: {args.horoscope}  虚岁: {h.age.nominal_age}")
        d = h.decadal
        print(f"  大限: {d.heavenly_stem}{d.earthly_branch}大限  "
              f"四化(禄权科忌): {'、'.join(d.mutagen)}")
        y = h.yearly
        print(f"  流年: {y.heavenly_stem}{y.earthly_branch}年  "
              f"四化(禄权科忌): {'、'.join(y.mutagen)}")
        m = h.monthly
        print(f"  流月: {m.heavenly_stem}{m.earthly_branch}月  "
              f"四化(禄权科忌): {'、'.join(m.mutagen)}")
    print("=" * 62)


if __name__ == "__main__":
    main()
