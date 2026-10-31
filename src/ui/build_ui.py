# -*- coding: utf-8 -*-
"""生成校园二手交易系统 UI 设计稿（HTML）"""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------- 图标 ----------------
IC = {
    "search": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>',
    "back": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16202B" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 19l-7-7 7-7"/></svg>',
    "filter": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h16M7 12h10M10 18h4"/></svg>',
    "bell": '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><path d="M18 16v-4a6 6 0 10-12 0v4l-2 2h16l-2-2z"/><path d="M10 21h4"/></svg>',
    "home": '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"><path d="M4 10.5L12 4l8 6.5V20H4z"/></svg>',
    "grid": '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/></svg>',
    "chat": '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"><path d="M20 12a7 7 0 01-7 7H8l-4 3v-5.5A7 7 0 0111 5h2a7 7 0 017 7z"/></svg>',
    "user": '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="12" cy="8.5" r="3.6"/><path d="M5 20c0-3.6 3.1-5.6 7-5.6s7 2 7 5.6"/></svg>',
    "plus": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round"><path d="M12 6v12M6 12h12"/></svg>',
    "more": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.7"/><circle cx="12" cy="12" r="1.7"/><circle cx="19" cy="12" r="1.7"/></svg>',
    "share": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#16202B" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4M8 8l4-4 4 4"/><path d="M5 14v5h14v-5"/></svg>',
    "flag": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 21V4h11l-2 4 2 4H6"/></svg>',
    "camera": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#9AA8B8" stroke-width="1.8"><path d="M3 8h3l1.5-2h9L18 8h3v11H3z"/><circle cx="12" cy="13" r="3.2"/></svg>',
    "check": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
    "clock": '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></svg>',
    "right": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#B6C1CD" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg>',
}

def sb():
    return ('<div class="statusbar"><span>9:41</span><span class="right">'
            '<svg width="17" height="11" viewBox="0 0 17 11" fill="#16202B"><rect x="0" y="7" width="3" height="4" rx="1"/>'
            '<rect x="4.5" y="5" width="3" height="6" rx="1"/><rect x="9" y="2.5" width="3" height="8.5" rx="1"/>'
            '<rect x="13.5" y="0" width="3" height="11" rx="1"/></svg>'
            '<svg width="16" height="11" viewBox="0 0 16 12" fill="#16202B"><path d="M8 10.2l1.8-2A2.6 2.6 0 008 7.4a2.6 2.6 0 00-1.8.8L8 10.2z"/>'
            '<path d="M3.4 5.6A6.7 6.7 0 018 3.9c1.7 0 3.4.6 4.6 1.7l1.3-1.4A8.6 8.6 0 008 1.7 8.6 8.6 0 002.1 4.2L3.4 5.6z"/></svg>'
            '<svg width="24" height="11" viewBox="0 0 24 12" fill="none"><rect x="0.5" y="0.5" width="20" height="11" rx="3" stroke="#16202B" stroke-opacity=".4"/>'
            '<rect x="2" y="2" width="15" height="8" rx="2" fill="#16202B"/><path d="M22 4v4a2.4 2.4 0 000-4z" fill="#16202B" fill-opacity=".5"/></svg>'
            '</span></div>')

def tabbar(active="home"):
    t = lambda k, ic, name: ('<div class="tab on">' if k == active else '<div class="tab">') + IC[ic] + f'<span>{name}</span></div>'
    return ('<div class="tabbar">' + t("home", "home", "首页") + t("cate", "grid", "分类") +
            '<div class="fab"><div class="circle">' + IC["plus"] + '</div></div>' +
            t("msg", "chat", "消息") + t("me", "user", "我的") + '</div>')

def page(name, body, title="", extra_css=""):
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<link rel="stylesheet" href="app.css">
<style>
body{{width:390px;height:844px;margin:0;}}
.phone{{width:390px;height:844px;}}
{extra_css}
</style></head><body><div class="phone"><div class="screen">{body}</div></div></body></html>"""
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", name)

# 商品缩略图
def thumb(w, h, c1, c2, label=""):
    return (f'<div style="width:{w}px;height:{h}px;border-radius:10px;position:relative;overflow:hidden;'
            f'background:linear-gradient(135deg,{c1},{c2});">'
            f'<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;'
            f'color:rgba(255,255,255,.92);font-size:11px;letter-spacing:2px;font-weight:700">{label}</div></div>')

# =====================================================================
# 界面 1  首页 · 商品查询
# =====================================================================
GOODS = [
    ("高等数学 第七版 上下册", "¥28", "九成新", "教材书籍", "#9FC6B3", "#6FAF92", "教材"),
    ("iPad 9代 64G WiFi 版", "¥1480", "九五新", "数码电子", "#9FB3CE", "#6B87AC", "数码"),
    ("宿舍静音小风扇 可摇头", "¥35", "八成新", "生活用品", "#F0CBA0", "#D6A26B", "生活"),
    ("捷安特山地车 21速", "¥460", "八成新", "运动户外", "#B9C79C", "#8FA36B", "运动"),
    ("罗技机械键盘 青轴", "¥180", "九成新", "数码电子", "#C6B4CE", "#9A85A6", "数码"),
    ("考研英语真题 全新未拆", "¥22", "全新", "教材书籍", "#E6C3A6", "#CE9C77", "教材"),
]

def goods_card(g):
    t, p, c, cat, c1, c2, lab = g
    return f"""<div class="card" style="overflow:hidden;">
  {thumb(171,132,c1,c2,lab)}
  <div style="padding:9px 10px 11px;">
    <div style="font-size:13px;line-height:1.35;height:36px;overflow:hidden;">{t}</div>
    <div style="display:flex;align-items:flex-end;margin-top:6px;">
      <span class="price"><small>¥</small>{p[1:]}</span>
      <span class="tag green" style="margin-left:auto;">{c}</span>
    </div>
    <div style="display:flex;align-items:center;gap:5px;margin-top:7px;font-size:10.5px;color:#96A3B2;">
      <span style="width:14px;height:14px;border-radius:7px;background:#DCE5EE;display:inline-block;"></span>
      <span>李同学</span><span style="margin-left:auto;">3 小时前</span>
    </div>
  </div>
</div>"""

s1 = sb() + f"""
<div style="padding:8px 16px 4px;background:#fff;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="display:flex;align-items:center;gap:4px;font-size:13.5px;font-weight:700;">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0E9F6E" stroke-width="2.2"><path d="M12 21s7-5.4 7-11a7 7 0 10-14 0c0 5.6 7 11 7 11z"/><circle cx="12" cy="10" r="2.4"/></svg>
      东校区
    </div>
    <div class="search" style="flex:1;">{IC['search']}<span>搜教材 / 数码 / 自行车</span></div>
    <div style="position:relative;">{IC['bell']}<span style="position:absolute;top:-2px;right:-3px;width:7px;height:7px;border-radius:4px;background:#E5484D;"></span></div>
  </div>
  <div class="chips">
    <div class="chip on">全部</div><div class="chip">教材书籍</div><div class="chip">数码电子</div>
    <div class="chip">生活用品</div><div class="chip">运动户外</div>
  </div>
</div>
<div style="display:flex;align-items:center;gap:16px;padding:8px 16px;font-size:12.5px;color:#7A8798;background:#fff;border-bottom:1px solid #E9EEF4;">
  <span style="color:#0A7C56;font-weight:700;">最新发布</span><span>价格 ↑</span><span>离我最近</span>
  <span style="margin-left:auto;display:flex;align-items:center;gap:4px;color:#3C4A5A;">{IC['filter']}筛选</span>
</div>
<div style="flex:1;overflow:hidden;padding:12px 16px;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:11px;">
    {goods_card(GOODS[0])}{goods_card(GOODS[1])}{goods_card(GOODS[2])}{goods_card(GOODS[3])}{goods_card(GOODS[4])}{goods_card(GOODS[5])}
  </div>
</div>
""" + tabbar("home")
page("界面1.html", s1)

# =====================================================================
# 界面 2  商品详情 · 预约
# =====================================================================
s2 = sb() + f"""
<div style="position:relative;height:240px;background:linear-gradient(160deg,#A9CBB8,#6FAF92 78%);">
  <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,.9);font-size:13px;letter-spacing:4px;">商品图片 1/4</div>
  <div style="position:absolute;top:8px;left:14px;right:14px;display:flex;align-items:center;">
    <div style="width:32px;height:32px;border-radius:16px;background:rgba(255,255,255,.85);display:flex;align-items:center;justify-content:center;">{IC['back']}</div>
    <div style="margin-left:auto;display:flex;gap:8px;">
      <div style="width:32px;height:32px;border-radius:16px;background:rgba(255,255,255,.85);display:flex;align-items:center;justify-content:center;">{IC['share']}</div>
      <div style="width:32px;height:32px;border-radius:16px;background:rgba(255,255,255,.85);display:flex;align-items:center;justify-content:center;">{IC['more']}</div>
    </div>
  </div>
  <div style="position:absolute;bottom:14px;right:16px;background:rgba(15,23,33,.55);color:#fff;border-radius:11px;padding:3px 9px;font-size:11.5px;">1 / 4</div>
</div>
<div style="flex:1;overflow:hidden;background:#F4F6F9;margin-top:-14px;border-radius:16px 16px 0 0;padding:16px 16px 0;">
  <div style="display:flex;align-items:baseline;gap:8px;">
    <span class="price" style="font-size:27px;"><small>¥</small>28</span>
    <span style="color:#96A3B2;font-size:12px;text-decoration:line-through;">原价 ¥45</span>
    <span class="tag green" style="margin-left:auto;height:22px;">已发布</span>
  </div>
  <div style="font-size:16.5px;font-weight:700;line-height:1.45;margin-top:8px;">高等数学 第七版 上下册 同济大学出版社</div>
  <div style="font-size:12.5px;color:#7A8798;margin-top:8px;display:flex;gap:14px;">
    <span>九成新</span><span>教材书籍</span><span>浏览 236</span>
  </div>

  <div class="card" style="margin-top:14px;padding:13px 14px;display:flex;align-items:center;gap:10px;">
    <div style="width:38px;height:38px;border-radius:19px;background:#DCE5EE;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:#5B6B7C;">李</div>
    <div>
      <div style="font-size:14px;font-weight:700;">李同学 <span class="tag gray" style="margin-left:4px;">计算机学院</span></div>
      <div style="font-size:11.5px;color:#96A3B2;margin-top:2px;">在售 5 件 · 已完成交易 18 笔</div>
    </div>
    <div style="margin-left:auto;">{IC['right']}</div>
  </div>

  <div class="card" style="margin-top:10px;padding:4px 14px;">
    <div class="row" style="padding:11px 0;font-size:13px;"><span class="label">交易地点</span><span class="value">学生活动中心 1F</span></div>
    <div class="row" style="padding:11px 0;font-size:13px;"><span class="label">发布时间</span><span class="value">10-24 18:32</span></div>
    <div class="row" style="padding:11px 0;font-size:13px;"><span class="label">审核状态</span><span class="value"><span class="tag green">审核通过</span></span></div>
  </div>

  <div class="card" style="margin-top:10px;padding:13px 14px;">
    <div style="font-size:13.5px;font-weight:700;margin-bottom:6px;">商品描述</div>
    <div style="font-size:13px;line-height:1.7;color:#3C4A5A;">上下册合售，线代与微积分部分有少量笔记，书角略有磨损，不影响阅读。可当面验货，东校区内可送到宿舍楼下。</div>
  </div>

  <div style="display:flex;align-items:flex-start;gap:6px;margin-top:12px;background:#FDF6E9;border:1px solid #F2E3C8;border-radius:10px;padding:9px 11px;">
    <span style="color:#C58A2E;margin-top:1px;">{IC['clock']}</span>
    <div class="hint" style="color:#8A6A2F;">同一商品只支持一条有效预约。预约成功后卖家确认即进入线下交付，请在确认前与卖家沟通清楚。</div>
  </div>
</div>
<div style="flex:0 0 74px;background:#fff;border-top:1px solid #E9EEF4;display:flex;align-items:center;gap:12px;padding:0 16px;">
  <div style="display:flex;flex-direction:column;align-items:center;gap:2px;font-size:10.5px;color:#7A8798;">{IC['flag']}<span>举报</span></div>
  <div style="display:flex;flex-direction:column;align-items:center;gap:2px;font-size:10.5px;color:#7A8798;">{IC['chat']}<span>联系卖家</span></div>
  <div class="btn primary" style="flex:1;">立即预约</div>
</div>
"""
page("界面2.html", s2)

# =====================================================================
# 界面 3  举报商品（弹层）
# =====================================================================
REASONS = [
    ("虚假信息", "描述与实际商品不符、伪造图片", False),
    ("违禁物品", "涉及法律法规禁止交易的物品", False),
    ("价格欺诈", "标价与实际交易价格不一致", True),
    ("侵权盗版", "盗版书籍、软件或仿冒商品", False),
    ("其他", "请在下方向管理员补充说明", False),
]
def reason_row(name, desc, on):
    dot = ('<div style="width:18px;height:18px;border-radius:9px;border:2px solid #0E9F6E;display:flex;align-items:center;justify-content:center;">'
           '<div style="width:8px;height:8px;border-radius:4px;background:#0E9F6E;"></div></div>') if on else \
          '<div style="width:18px;height:18px;border-radius:9px;border:2px solid #D3DBE4;"></div>'
    return f"""<div style="display:flex;align-items:center;gap:11px;padding:12px 0;border-bottom:1px solid #F1F4F8;">
  {dot}
  <div><div style="font-size:14px;{'font-weight:700;color:#0A7C56;' if on else ''}">{name}</div>
  <div style="font-size:11.5px;color:#96A3B2;margin-top:2px;">{desc}</div></div>
</div>"""

s3 = sb() + f"""
<div style="position:relative;height:170px;background:linear-gradient(160deg,#A9CBB8,#6FAF92 78%);">
  <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,.9);font-size:13px;letter-spacing:4px;">商品图片</div>
  <div style="position:absolute;top:8px;left:14px;width:32px;height:32px;border-radius:16px;background:rgba(255,255,255,.85);display:flex;align-items:center;justify-content:center;">{IC['back']}</div>
</div>
<div style="padding:14px 16px;">
  <div class="price" style="font-size:24px;"><small>¥</small>28</div>
  <div style="font-size:16px;font-weight:700;margin-top:6px;">高等数学 第七版 上下册 同济大学出版社</div>
  <div class="card" style="margin-top:12px;padding:13px 14px;font-size:13px;color:#7A8798;">上下册合售，线代与微积分部分有少量笔记……</div>
</div>
<div class="mask"></div>
<div class="sheet" style="padding-top:16px;">
  <div style="display:flex;align-items:center;margin-bottom:4px;">
    <div style="font-size:16px;font-weight:700;">举报商品</div>
    <div style="margin-left:auto;color:#96A3B2;width:20px;height:20px;">
      <svg width="18" height="18" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;background:#F6F8FA;border-radius:10px;padding:9px;margin:10px 0 6px;">
    {thumb(34,34,'#9FC6B3','#6FAF92','')}
    <div style="font-size:12.5px;color:#3C4A5A;line-height:1.4;">高等数学 第七版 上下册<br><span style="color:#96A3B2;">李同学 · 教材书籍</span></div>
  </div>
  <div style="font-size:13px;font-weight:700;margin:12px 0 2px;">选择举报原因</div>
  {''.join(reason_row(*r) for r in REASONS)}
  <div style="margin-top:12px;background:#F6F8FA;border-radius:10px;padding:11px 12px;">
    <div style="font-size:12px;color:#96A3B2;">补充说明（选填）</div>
    <div style="font-size:13px;color:#3C4A5A;margin-top:6px;line-height:1.6;">卖家页面写"上下册合售"，实际只发上册，沟通后拒绝退款。</div>
    <div style="text-align:right;font-size:11px;color:#B6C1CD;">38 / 200</div>
  </div>
  <div class="hint" style="margin:10px 2px 12px;">同一用户对同一商品仅保留一条待处理举报，重复提交将返回原记录；恶意举报将被限制使用。</div>
  <div class="btn primary block">提交举报</div>
</div>
"""
page("界面3.html", s3)

# =====================================================================
# 界面 4  发布商品
# =====================================================================
def field(label, inner, required=True):
    return f"""<div style="padding:11px 0;border-bottom:1px solid #F1F4F8;">
  <div style="font-size:12px;color:#7A8798;margin-bottom:7px;">{label}{'<span style="color:#E5484D;"> *</span>' if required else ''}</div>
  {inner}</div>"""

def chip_row(items, on_idx=0):
    out = ""
    for i, it in enumerate(items):
        cls = "chip on" if i == on_idx else "chip"
        out += f'<div class="{cls}" style="height:28px;">{it}</div>'
    return f'<div style="display:flex;gap:7px;flex-wrap:wrap;">{out}</div>'

s4 = sb() + f"""
<div class="navbar"><div class="back">{IC['back']}</div><div class="title">发布商品</div>
  <div class="actions"><span style="font-size:13px;color:#0A7C56;font-weight:700;">草稿箱</span></div></div>
<div style="flex:1;overflow:hidden;padding:12px 16px;">
  <div class="card" style="padding:14px;">
    <div style="display:flex;gap:10px;align-items:flex-start;">
      <div style="width:88px;height:88px;border-radius:10px;background:linear-gradient(135deg,#9FC6B3,#6FAF92);position:relative;">
        <span style="position:absolute;bottom:5px;left:0;right:0;text-align:center;color:#fff;font-size:10px;">封面</span>
      </div>
      <div style="width:88px;height:88px;border-radius:10px;background:linear-gradient(135deg,#CBD5DF,#A9B7C6);"></div>
      <div style="width:88px;height:88px;border-radius:10px;border:1px dashed #CBD5DF;background:#FAFBFC;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;">
        {IC['camera']}<span style="font-size:10.5px;color:#9AA8B8;">2/9</span>
      </div>
    </div>
    <div class="hint" style="margin-top:9px;">最多上传 9 张，首张为封面；建议实拍图，避免网图影响审核通过率</div>
  </div>

  <div class="card" style="padding:2px 14px 6px;margin-top:10px;">
    {field('商品标题', '<div style="font-size:14.5px;font-weight:600;">高等数学 第七版 上下册 同济大学出版社</div><div style="font-size:11px;color:#B6C1CD;text-align:right;">21/30</div>')}
    {field('商品描述', '<div style="font-size:13.5px;line-height:1.65;color:#3C4A5A;">上下册合售，线代与微积分部分有少量笔记，书角略有磨损，不影响阅读。</div><div style="font-size:11px;color:#B6C1CD;text-align:right;">43/500</div>')}
    {field('价格', '<div style="display:flex;align-items:baseline;gap:4px;"><span style="color:#F4511E;font-size:18px;font-weight:800;">¥</span><span style="font-size:22px;font-weight:800;color:#F4511E;">28</span><span style="font-size:11.5px;color:#96A3B2;margin-left:6px;">参考同款均价：¥30 ~ ¥45</span></div>')}
    {field('商品分类', chip_row(['教材书籍','数码电子','生活用品','运动户外','其他']))}
    {field('商品成色', chip_row(['全新','95新','9成新','8成新','8成以下'], 2))}
    {field('交易地点', '<div style="font-size:14px;color:#3C4A5A;">学生活动中心 1F <span style="font-size:11.5px;color:#0A7C56;margin-left:8px;">修改</span></div>')}
  </div>

  <div style="display:flex;gap:6px;margin-top:12px;background:#F1F7FF;border:1px solid #D6E6F8;border-radius:10px;padding:10px 11px;">
    <span style="color:#2F5FA8;font-size:12px;">ⓘ</span>
    <div class="hint" style="color:#3B6395;">提交后进入审核队列，审核通过前不会出现在公开列表中；驳回时可在「我的商品」查看驳回原因并修改后重新提交。</div>
  </div>
</div>
<div style="flex:0 0 72px;border-top:1px solid #E9EEF4;background:#fff;display:flex;gap:10px;align-items:center;padding:0 16px;">
  <div class="btn ghost" style="width:110px;">保存草稿</div>
  <div class="btn primary" style="flex:1;">提交审核</div>
</div>
"""
page("界面4.html", s4)

# =====================================================================
# 界面 5  我的商品（卖家）
# =====================================================================
def my_item(title, cat, price, status_html, actions, c1, c2, lab, note=""):
    btns = "".join(f'<div class="btn sm {"btn-line" if i==0 else "ghost"}" style="{"border-color:#0E9F6E;color:#0A7C56;" if i==0 else "border:1px solid #E9EEF4;color:#3C4A5A;"}">{b}</div>'
                   for i, b in enumerate(actions))
    return f"""<div class="card" style="padding:13px 14px;">
  <div style="display:flex;align-items:center;gap:7px;font-size:11.5px;color:#96A3B2;margin-bottom:9px;white-space:nowrap;">
    <span class="tag {'green' if '已发布' in status_html or '已预约' in status_html else 'gray'}" style="flex:0 0 auto;">{status_html}</span>
    <span style="overflow:hidden;text-overflow:ellipsis;">{note}</span><span style="margin-left:auto;flex:0 0 auto;">10-24</span>
  </div>
  <div style="display:flex;gap:11px;">
    {thumb(72,72,c1,c2,lab)}
    <div style="flex:1;min-width:0;">
      <div style="font-size:13.5px;font-weight:600;line-height:1.4;height:38px;overflow:hidden;">{title}</div>
      <div style="display:flex;align-items:center;margin-top:5px;">
        <span class="price" style="font-size:15px;"><small>¥</small>{price}</span>
        <span style="font-size:11px;color:#96A3B2;margin-left:8px;">{cat}</span>
      </div>
    </div>
  </div>
  <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:11px;padding-top:11px;border-top:1px solid #F1F4F8;">{btns}</div>
</div>"""

s5 = sb() + f"""
<div class="navbar"><div class="back">{IC['back']}</div><div class="title">我的商品</div>
  <div class="actions"><span style="font-size:12.5px;">筛选</span>{IC['more']}</div></div>
<div style="background:#fff;padding:0 0 4px;">
  <div style="display:flex;gap:18px;padding:10px 16px 8px;font-size:13px;color:#7A8798;overflow:hidden;">
    <span style="color:#0A7C56;font-weight:700;position:relative;">全部<span style="position:absolute;left:0;right:0;bottom:-8px;height:2.5px;border-radius:2px;background:#0E9F6E;"></span></span>
    <span>草稿</span><span>待审核</span><span>已发布</span><span>已预约</span><span>已完成</span>
  </div>
  <div style="display:flex;gap:0;padding:8px 16px 12px;margin-top:4px;">
    <div style="flex:1;"><div class="kpi" style="font-size:19px;">12</div><div style="font-size:10.5px;color:#96A3B2;">已发布</div></div>
    <div style="flex:1;"><div class="kpi" style="font-size:19px;">5</div><div style="font-size:10.5px;color:#96A3B2;">在售中</div></div>
    <div style="flex:1;"><div class="kpi" style="font-size:19px;color:#C58A2E;">1</div><div style="font-size:10.5px;color:#96A3B2;">待处理预约</div></div>
    <div style="flex:1;"><div class="kpi" style="font-size:19px;">¥2,340</div><div style="font-size:10.5px;color:#96A3B2;">本月成交</div></div>
  </div>
</div>
<div style="flex:1;overflow:hidden;padding:11px 16px;background:#F4F6F9;">
  {my_item("高等数学 第七版 上下册 同济大学出版社", "教材书籍", "28", "已发布", ["查看预约", "下架"], "#9FC6B3", "#6FAF92", "教材", "有 1 条有效预约待确认")}
  <div style="height:10px;"></div>
  {my_item("iPad 9代 64G WiFi 版 含原装充电器", "数码电子", "1480", "已预约", ["确认交易", "取消预约"], "#9FB3CE", "#6B87AC", "数码", "买家：王同学 · 10-25")}
  <div style="height:10px;"></div>
  {my_item("罗技机械键盘 青轴 附手托", "数码电子", "180", "已发布·待审", ["查看审核进度"], "#C6B4CE", "#9A85A6", "数码", "新信息审核中，前台仍显示旧信息")}
  <div style="height:10px;"></div>
  {my_item("考研英语真题 2015-2024 全新未拆", "教材书籍", "22", "草稿", ["继续编辑", "提交审核"], "#E6C3A6", "#CE9C77", "教材", "上次编辑 3 天前")}
</div>
"""
page("界面5.html", s5, extra_css="")

# =====================================================================
# 界面 6  我的交易
# =====================================================================
def trade_card(status_tag, status_txt, title, price, c1, c2, lab, steps, tip, actions):
    st = ""
    for i, (t, done) in enumerate(steps):
        color = "#0E9F6E" if done else "#CBD5DF"
        st += f"""<div style="display:flex;flex-direction:column;align-items:center;flex:1;position:relative;">
      <div style="width:9px;height:9px;border-radius:5px;background:{color};z-index:1;"></div>
      {'' if i == len(steps)-1 else f'<div style="position:absolute;top:4px;left:50%;width:100%;height:1.5px;background:{color};"></div>'}
      <div style="font-size:10px;color:{'#3C4A5A' if done else '#AAB5C2'};margin-top:6px;text-align:center;line-height:1.3;">{t}</div>
    </div>"""
    btns = "".join(f'<div class="btn sm {"primary" if i==0 else "ghost"}" style="{"background:#0E9F6E;color:#fff;" if i==0 else "border:1px solid #E9EEF4;color:#3C4A5A;"}">{b}</div>' for i, b in enumerate(actions))
    return f"""<div class="card" style="padding:0;overflow:hidden;">
  <div style="display:flex;align-items:center;padding:11px 14px;background:#F7FAF9;border-bottom:1px solid #F1F4F8;">
    <span class="tag {'orange' if '等待' in status_txt else 'green'}">{status_tag}</span>
    <span style="font-size:12.5px;font-weight:700;margin-left:8px;">{status_txt}</span>
    <span style="margin-left:auto;font-size:11px;color:#96A3B2;">订单号 SE20261025007</span>
  </div>
  <div style="display:flex;gap:11px;padding:13px 14px 4px;">
    {thumb(64,64,c1,c2,lab)}
    <div style="flex:1;">
      <div style="font-size:13.5px;font-weight:600;line-height:1.4;height:38px;overflow:hidden;">{title}</div>
      <div class="price" style="font-size:15px;margin-top:3px;"><small>¥</small>{price}</div>
    </div>
  </div>
  <div style="display:flex;padding:10px 8px 2px;">{st}</div>
  <div style="display:flex;align-items:center;gap:6px;margin:0 14px 11px;background:#FDF6E9;border-radius:8px;padding:7px 10px;">
    <span style="color:#C58A2E;">{IC['clock']}</span><span style="font-size:11.5px;color:#8A6A2F;">{tip}</span>
  </div>
  <div style="display:flex;gap:8px;justify-content:flex-end;padding:0 14px 13px;">{btns}</div>
</div>"""

s6 = sb() + f"""
<div class="navbar"><div class="back">{IC['back']}</div><div class="title">我的交易</div>
  <div class="actions">{IC['more']}</div></div>
<div style="display:flex;gap:0;padding:10px 16px;background:#fff;border-bottom:1px solid #E9EEF4;">
  <div style="flex:1;text-align:center;font-size:14px;color:#7A8798;">我买到的</div>
  <div style="flex:1;text-align:center;font-size:14px;font-weight:700;color:#16202B;position:relative;">我卖出的
    <span style="position:absolute;left:50%;transform:translateX(-50%);bottom:-11px;width:26px;height:2.5px;border-radius:2px;background:#0E9F6E;"></span></div>
</div>
<div style="flex:1;overflow:hidden;padding:12px 16px;background:#F4F6F9;">
  <div style="display:flex;gap:7px;margin-bottom:11px;">
    <div class="chip on" style="height:28px;">待确认 <b style="margin-left:3px;">1</b></div>
    <div class="chip" style="height:28px;">待交付 2</div>
    <div class="chip" style="height:28px;">已完成</div>
  </div>
  {trade_card("已预约", "待卖家确认", "iPad 9代 64G WiFi 版 含原装充电器", "1480", "#9FB3CE", "#6B87AC", "数码",
              [("买家预约<br>10-25 09:12", True), ("卖家确认", False), ("线下交付", False), ("完成", False)],
              "确认交易后请在 7 天内完成线下交付，超时系统将自动标记完成",
              ["确认交易", "取消预约"])}
  <div style="height:11px;"></div>
  {trade_card("已确认", "等待线下交付", "捷安特山地车 21速 27.5寸", "460", "#B9C79C", "#8FA36B", "运动",
              [("预约<br>10-21", True), ("确认<br>10-22", True), ("交付中", True), ("完成", False)],
              "买家已确认收货后交易完成；满 7 天未确认将自动完成",
              ["联系买家", "查看详情"])}
</div>
<div class="tabbar">{"<div class='tab'><span>首页</span></div>"}
</div>
"""
# 简化底部：仅保留 tabbar 结构
s6 = s6.replace('<div class="tabbar"><div class=\'tab\'><span>首页</span></div>\n</div>', "")
s6 = s6 + tabbar("me")
page("界面6.html", s6)

# =====================================================================
# 界面 7  登录 / 注册
# =====================================================================
s7 = sb() + f"""
<div style="flex:1;overflow:hidden;padding:0 30px;background:linear-gradient(180deg,#EAF6F1 0%,#F4F6F9 42%);">
  <div style="margin-top:44px;display:flex;align-items:center;gap:11px;">
    <div style="width:46px;height:46px;border-radius:14px;background:linear-gradient(135deg,#12B784,#0A7C56);display:flex;align-items:center;justify-content:center;color:#fff;font-size:20px;font-weight:800;">校</div>
    <div>
      <div style="font-size:19px;font-weight:800;letter-spacing:.5px;">校园二手</div>
      <div style="font-size:11.5px;color:#7A8798;margin-top:2px;">让闲置在东校区流动起来</div>
    </div>
  </div>

  <div style="display:flex;gap:22px;margin-top:32px;font-size:15px;">
    <span style="font-weight:800;color:#16202B;position:relative;">登录
      <span style="position:absolute;left:0;right:0;bottom:-7px;height:3px;border-radius:2px;background:#0E9F6E;"></span></span>
    <span style="color:#96A3B2;">注册</span>
  </div>

  <div class="card" style="margin-top:22px;padding:6px 16px;">
    <div style="display:flex;align-items:center;gap:10px;padding:14px 0;border-bottom:1px solid #F1F4F8;">
      <span style="font-size:12.5px;color:#7A8798;width:38px;">学号</span>
      <span style="font-size:14.5px;font-weight:600;">241220107</span>
    </div>
    <div style="display:flex;align-items:center;gap:10px;padding:14px 0;">
      <span style="font-size:12.5px;color:#7A8798;width:38px;">密码</span>
      <span style="font-size:14.5px;letter-spacing:3px;">••••••••</span>
      <span style="margin-left:auto;font-size:11.5px;color:#96A3B2;">显示</span>
    </div>
  </div>
  <div style="display:flex;justify-content:space-between;font-size:11.5px;color:#96A3B2;margin-top:12px;">
    <span>学号仅限本校在籍学生</span><span style="color:#0A7C56;">忘记密码？</span>
  </div>
  <div class="btn primary block" style="margin-top:20px;">登录</div>
  <div style="display:flex;align-items:center;gap:8px;margin-top:16px;font-size:11px;color:#96A3B2;">
    <span style="width:13px;height:13px;border-radius:4px;border:1.5px solid #0E9F6E;display:flex;align-items:center;justify-content:center;color:#0E9F6E;">{IC['check']}</span>
    已阅读并同意《用户协议》与《隐私政策》
  </div>

  <div style="display:flex;align-items:center;gap:10px;margin-top:30px;color:#C3CCD7;font-size:11px;">
    <span style="flex:1;height:1px;background:#E4EAF0;"></span>其他登录方式<span style="flex:1;height:1px;background:#E4EAF0;"></span>
  </div>
  <div style="display:flex;gap:14px;margin-top:14px;">
    <div class="card" style="flex:1;height:44px;display:flex;align-items:center;justify-content:center;gap:7px;font-size:12.5px;color:#3C4A5A;">
      <span style="width:16px;height:16px;border-radius:8px;background:#E8F0FB;"></span>校园统一认证</div>
    <div class="card" style="flex:1;height:44px;display:flex;align-items:center;justify-content:center;gap:7px;font-size:12.5px;color:#96A3B2;">
      <span style="width:16px;height:16px;border-radius:8px;background:#FCE9E9;"></span>管理员登录</div>
  </div>
  <div class="hint" style="margin-top:18px;line-height:1.7;">管理员账号由系统管理员统一分配，不通过自助注册获得；登录后密码以加密方式存储，全部请求经 HTTPS 传输。</div>
</div>
"""
page("界面7.html", s7)

# =====================================================================
# 界面 8  个人中心
# =====================================================================
def menu_row(icon_bg, text, right="", last=False):
    return f"""<div style="display:flex;align-items:center;gap:11px;padding:14px 16px;{'border-bottom:1px solid #F1F4F8;' if not last else ''}">
  <span style="width:26px;height:26px;border-radius:8px;background:{icon_bg};display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#5B6B7C;">{icon_bg and text[0]}</span>
  <span style="font-size:13.5px;">{text}</span>
  <span style="margin-left:auto;font-size:12px;color:#96A3B2;">{right}</span>{IC['right']}
</div>"""

s8 = sb() + f"""
<div style="height:150px;background:linear-gradient(140deg,#12B784,#0A7C56);padding:16px 18px;position:relative;">
  <div style="display:flex;align-items:center;gap:9px;color:#fff;font-size:13px;">{IC['bell']}<span style="margin-left:auto;font-size:12px;opacity:.9;">设置</span></div>
  <div style="display:flex;align-items:center;gap:13px;margin-top:16px;">
    <div style="width:56px;height:56px;border-radius:28px;background:rgba(255,255,255,.92);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:#0A7C56;">黄</div>
    <div>
      <div style="color:#fff;font-size:17px;font-weight:800;">黄毅 <span style="font-size:11px;font-weight:700;background:rgba(255,255,255,.22);padding:2px 7px;border-radius:9px;margin-left:4px;">普通用户</span></div>
      <div style="color:rgba(255,255,255,.85);font-size:11.5px;margin-top:4px;">学号 241220107 · 计算机科学与技术学院</div>
    </div>
  </div>
</div>
<div style="flex:1;overflow:hidden;padding:0 16px;margin-top:-22px;position:relative;z-index:2;">
  <div class="card" style="padding:15px 0;display:flex;box-shadow:0 4px 16px rgba(15,60,40,.10);">
    <div style="flex:1;text-align:center;">
      <div style="font-size:18px;font-weight:800;">12</div><div style="font-size:10.5px;color:#96A3B2;margin-top:2px;">发布</div></div>
    <div style="width:1px;background:#EFF3F7;"></div>
    <div style="flex:1;text-align:center;">
      <div style="font-size:18px;font-weight:800;">8</div><div style="font-size:10.5px;color:#96A3B2;margin-top:2px;">卖出</div></div>
    <div style="width:1px;background:#EFF3F7;"></div>
    <div style="flex:1;text-align:center;">
      <div style="font-size:18px;font-weight:800;">5</div><div style="font-size:10.5px;color:#96A3B2;margin-top:2px;">买到</div></div>
    <div style="width:1px;background:#EFF3F7;"></div>
    <div style="flex:1;text-align:center;">
      <div style="font-size:18px;font-weight:800;color:#C58A2E;">1</div><div style="font-size:10.5px;color:#96A3B2;margin-top:2px;">待处理</div></div>
  </div>

  <div class="card" style="margin-top:12px;overflow:hidden;">
    {menu_row('#E7F6F0','我的商品','在售 5 件')}
    {menu_row('#E8F0FB','我的交易','进行中 2 笔')}
    {menu_row('#FDEEE3','我的举报','处理中 1 条')}
    {menu_row('#F0EAFB','审核记录','')}
  </div>

  <div class="card" style="margin-top:12px;overflow:hidden;">
    {menu_row('#EEF1F5','账号与安全','密码已加密')}
    {menu_row('#EEF1F5','通知设置','交易与审核提醒已开')}
    {menu_row('#EEF1F5','帮助与反馈','', True)}
  </div>

  <div style="display:flex;gap:8px;margin-top:12px;background:#F1F7FF;border:1px solid #D6E6F8;border-radius:10px;padding:10px 12px;">
    <span style="color:#2F5FA8;font-size:12px;">ⓘ</span>
    <div class="hint" style="color:#3B6395;">密码使用不可逆加密存储；越权访问他人商品或预约详情将被系统拦截并记录日志。</div>
  </div>
</div>
""" + tabbar("me")
page("界面8.html", s8)

# =====================================================================
# 管理后台通用外壳
# =====================================================================
def apage(name, active, title, crumb, body, extra_css=""):
    navs = [("审核工作台", True), ("举报处理", True), ("操作日志", True), ("数据统计", True), ("分类管理", False)]
    nav_html = ""
    for n, _ in navs:
        cls = "item on" if n == active else "item"
        nav_html += f'<div class="{cls}"><span class="dot"></span>{n}</div>'
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<link rel="stylesheet" href="app-admin.css"><style>{extra_css}</style></head><body>
<div class="app">
  <div class="side">
    <div class="brand"><div class="logo">校</div><div><div class="nm">校园二手 · 后台</div><div class="sub">CampusTrade Admin</div></div></div>
    <div class="nav">
      <div class="grp">运营管理</div>
      {nav_html}
    </div>
    <div class="foot">v1.0 · 241220107 黄毅</div>
  </div>
  <div class="main">
    <div class="top">
      <h1>{title}</h1><div class="crumb">{crumb}</div>
      <div class="right">
        <div style="width:200px;height:30px;border-radius:15px;background:#F1F4F8;display:flex;align-items:center;padding:0 12px;gap:7px;color:#96A3B2;font-size:12px;">{IC['search']}搜索商品 / 用户</div>
        {IC['bell']}
        <div class="avatar">黄</div>
        <div class="who"><b>黄毅</b><span>系统管理员</span></div>
      </div>
    </div>
    <div class="content">{body}</div>
  </div>
</div></body></html>"""
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", name)

AUDIT_ROWS = [
    ("高等数学 第七版 上下册 同济大学出版社", "李同学", "教材书籍", "¥28", "10-26 09:12", "#9FC6B3", "#6FAF92"),
    ("罗技机械键盘 青轴 附手托（修改待审）", "陈同学", "数码电子", "¥180", "10-26 08:40", "#C6B4CE", "#9A85A6"),
    ("宿舍静音小风扇 可摇头", "王同学", "生活用品", "¥35", "10-25 21:05", "#F0CBA0", "#D6A26B"),
    ("考研英语真题 2015-2024 全新", "赵同学", "教材书籍", "¥22", "10-25 19:33", "#E6C3A6", "#CE9C77"),
    ("捷安特山地车 21速 27.5寸", "刘同学", "运动户外", "¥460", "10-25 17:20", "#B9C79C", "#8FA36B"),
]
def audit_row(i, r):
    t, s, c, p, tm, c1, c2 = r
    return f"""<tr class="{'on' if i==0 else ''}">
  <td><div class="goods"><div class="th" style="background:linear-gradient(135deg,{c1},{c2})"></div>
    <div><div class="nm">{t}</div><div style="font-size:10.5px;color:#9AA8B8;margin-top:2px;">ID 2026102{i+4}</div></div></div></td>
  <td>{s}</td><td>{c}</td><td style="color:#F4511E;font-weight:700;">{p}</td><td class="muted">{tm}</td>
  <td>{'<span class="tag orange">修改待审</span>' if i==1 else '<span class="tag gray">首次提交</span>'}</td>
</tr>"""

audit_body = f"""
<div class="kpis">
  <div class="kpi"><div class="t">待审核</div><div class="v" style="color:#C25A16;">12</div><div class="d warn">最早提交距今 6 小时</div></div>
  <div class="kpi"><div class="t">今日通过</div><div class="v">26</div><div class="d">平均处理时长 42 分钟</div></div>
  <div class="kpi"><div class="t">今日驳回</div><div class="v">3</div><div class="d" style="color:#C0393D;">主要原因为图片与描述不符</div></div>
  <div class="kpi"><div class="t">审核通过率（近 7 天）</div><div class="v">89.6%</div><div class="d">共处理 214 条</div></div>
</div>
<div style="display:flex;gap:14px;flex:1;min-height:0;">
  <div class="panel" style="flex:1.35;min-width:0;">
    <div class="ph"><b>待审核队列</b>
      <div style="display:flex;gap:6px;margin-left:14px;">
        <span class="tag green">待审核 12</span><span class="tag gray">已通过</span><span class="tag gray">已驳回</span>
      </div>
      <div class="sp">按提交时间排序</div>
    </div>
    <div class="scroll" style="flex:1;">
      <table>
        <thead><tr><th>商品</th><th>卖家</th><th>分类</th><th>价格</th><th>提交时间</th><th>类型</th></tr></thead>
        <tbody>{''.join(audit_row(i, r) for i, r in enumerate(AUDIT_ROWS))}</tbody>
      </table>
    </div>
    <div style="padding:10px 16px;border-top:1px solid var(--line);display:flex;align-items:center;font-size:11.5px;color:var(--sub);">
      共 12 条 · 每页 20 条 <span style="margin-left:auto;">上一页　<b style="color:var(--ink)">1</b>　下一页</span>
    </div>
  </div>

  <div class="panel" style="flex:1;min-width:0;">
    <div class="ph"><b>审核详情</b><div class="sp">ID 20261024</div></div>
    <div class="detail scroll" style="flex:1;">
      <div style="display:flex;gap:11px;">
        <div style="width:78px;height:78px;border-radius:9px;background:linear-gradient(135deg,#9FC6B3,#6FAF92);flex:0 0 78px;"></div>
        <div style="flex:1;min-width:0;">
          <div style="font-size:13.5px;font-weight:700;line-height:1.45;">高等数学 第七版 上下册 同济大学出版社</div>
          <div style="color:#F4511E;font-weight:800;font-size:17px;margin-top:6px;">¥28</div>
        </div>
      </div>
      <div style="font-size:11.5px;color:var(--sub);line-height:1.7;margin-top:10px;background:#FAFBFC;border-radius:8px;padding:9px 11px;">
        上下册合售，线代与微积分部分有少量笔记，书角略有磨损，不影响阅读。可当面验货。
      </div>
      <div style="margin-top:12px;">
        <div class="kv"><span class="k">卖家</span><span class="v">李同学 · 计算机学院 · 在售 5 件</span></div>
        <div class="kv"><span class="k">分类</span><span class="v">教材书籍 / 九成新</span></div>
        <div class="kv"><span class="k">交易地点</span><span class="v">学生活动中心 1F</span></div>
        <div class="kv" style="border-bottom:none;"><span class="k">审核类型</span><span class="v">首次提交</span></div>
      </div>

      <div style="margin-top:12px;">
        <div style="font-size:12px;font-weight:700;margin-bottom:7px;">驳回原因（驳回时必填）</div>
        <div style="display:flex;gap:7px;flex-wrap:wrap;">
          <span class="tag gray" style="height:26px;padding:0 10px;font-weight:400;">图片与实物不符</span>
          <span class="tag gray" style="height:26px;padding:0 10px;font-weight:400;">描述含联系方式</span>
          <span class="tag gray" style="height:26px;padding:0 10px;font-weight:400;">疑似违禁物品</span>
          <span class="tag gray" style="height:26px;padding:0 10px;font-weight:400;">分类错误</span>
        </div>
      </div>

      <div style="display:flex;gap:9px;margin-top:14px;">
        <div class="btn primary" style="flex:1;height:34px;">审核通过并发布</div>
        <div class="btn danger" style="flex:1;height:34px;">驳回并退回草稿</div>
      </div>
      <div style="font-size:10.5px;color:#9AA8B8;margin-top:7px;line-height:1.6;">审核前系统已重新读取商品当前状态与版本，非「待审核」状态不可执行审核；本次操作人与时间将写入审核记录。</div>

      <div style="font-size:12px;font-weight:700;margin-top:14px;">审核历史</div>
      <div class="timeline">
        <div class="it"><div class="d"></div><div class="c">10-26 09:12 卖家提交审核<span>（首次提交）</span></div></div>
        <div class="it"><div class="d gray"></div><div class="c">— 尚无历史审核记录</div></div>
      </div>
    </div>
  </div>
</div>
"""
apage("界面9.html", "审核工作台", "审核工作台", "运营管理 / 商品审核", audit_body)

# =====================================================================
# 界面 10  举报处理
# =====================================================================
REPORTS = [
    ("高等数学 第七版 上下册", "王同学", "价格欺诈", "10-26 08:12", "待处理", "#9FC6B3", "#6FAF92"),
    ("代写课程设计 可加急", "李同学", "违禁物品", "10-25 22:40", "待处理", "#D9B0B0", "#B97C7C"),
    ("罗技机械键盘 青轴", "陈同学", "虚假信息", "10-25 20:11", "待处理", "#C6B4CE", "#9A85A6"),
    ("考研英语真题 全新", "赵同学", "侵权盗版", "10-25 15:02", "已下架", "#E6C3A6", "#CE9C77"),
    ("iPad 9代 64G", "刘同学", "其他", "10-24 11:36", "已驳回", "#9FB3CE", "#6B87AC"),
]
def report_row(i, r):
    t, u, rea, tm, st, c1, c2 = r
    cls = "green" if st == "待处理" else ("red" if st == "已下架" else "gray")
    return f"""<tr class="{'on' if i==0 else ''}">
  <td><div class="goods"><div class="th" style="background:linear-gradient(135deg,{c1},{c2})"></div>
    <div class="nm">{t}</div></div></td>
  <td>{u}</td><td>{rea}</td><td class="muted">{tm}</td>
  <td><span class="tag {cls}">{st}</span></td></tr>"""

report_body = f"""
<div class="kpis">
  <div class="kpi"><div class="t">待处理举报</div><div class="v" style="color:#C0393D;">3</div><div class="d warn">其中 1 条涉及违禁物品</div></div>
  <div class="kpi"><div class="t">今日已处理</div><div class="v">7</div><div class="d">平均处理时长 1.2 小时</div></div>
  <div class="kpi"><div class="t">本月处置下架</div><div class="v">14</div><div class="d" style="color:#C0393D;">占比 31%</div></div>
  <div class="kpi"><div class="t">有效举报率</div><div class="v">68.4%</div><div class="d">恶意举报将限制账号</div></div>
</div>
<div style="display:flex;gap:14px;flex:1;min-height:0;">
  <div class="panel" style="flex:1.35;min-width:0;">
    <div class="ph"><b>举报列表</b>
      <div style="display:flex;gap:6px;margin-left:14px;"><span class="tag green">待处理 3</span><span class="tag gray">已下架</span><span class="tag gray">已驳回</span></div>
      <div class="sp">按举报时间倒序</div>
    </div>
    <div class="scroll" style="flex:1;">
      <table>
        <thead><tr><th>被举报商品</th><th>举报人</th><th>原因</th><th>举报时间</th><th>状态</th></tr></thead>
        <tbody>{''.join(report_row(i, r) for i, r in enumerate(REPORTS))}</tbody>
      </table>
    </div>
    <div style="padding:10px 16px;border-top:1px solid var(--line);font-size:11.5px;color:var(--sub);">共 3 条待处理 · 已按规则去重（同一用户对同一商品仅一条待处理举报）</div>
  </div>

  <div class="panel" style="flex:1;min-width:0;">
    <div class="ph"><b>举报处理</b><div class="sp">REP-20261026-0031</div></div>
    <div class="detail scroll" style="flex:1;">
      <div style="display:flex;gap:11px;">
        <div style="width:70px;height:70px;border-radius:9px;background:linear-gradient(135deg,#9FC6B3,#6FAF92);flex:0 0 70px;"></div>
        <div style="flex:1;min-width:0;">
          <div style="font-size:13.5px;font-weight:700;line-height:1.45;">高等数学 第七版 上下册 同济大学出版社</div>
          <div style="font-size:11.5px;color:var(--sub);margin-top:6px;">卖家：李同学 · 当前状态 <span class="tag green">已发布</span></div>
        </div>
      </div>
      <div class="kv" style="margin-top:12px;"><span class="k">举报类型</span><span class="v"><span class="tag orange">价格欺诈</span></span></div>
      <div class="kv"><span class="k">举报人</span><span class="v">王同学（241220088）</span></div>
      <div class="kv"><span class="k">举报时间</span><span class="v">10-26 08:12</span></div>
      <div class="kv" style="border-bottom:none;"><span class="k">历史举报</span><span class="v">该商品累计被举报 2 次</span></div>

      <div style="font-size:11.5px;color:var(--sub);line-height:1.7;margin-top:10px;background:#FAFBFC;border-radius:8px;padding:9px 11px;">
        <b style="color:var(--ink-2);">举报说明：</b>商品页面标价 ¥28，联系卖家后要求 ¥58 才发货，与页面价格严重不符。
      </div>

      <div style="font-size:12px;font-weight:700;margin-top:13px;margin-bottom:8px;">处理动作</div>
      <div style="display:flex;flex-direction:column;gap:8px;">
        <div style="display:flex;align-items:center;gap:9px;border:1px solid #0E9F6E;background:#F3FAF7;border-radius:9px;padding:9px 11px;">
          <span style="width:16px;height:16px;border-radius:8px;border:2px solid #0E9F6E;display:flex;align-items:center;justify-content:center;"><span style="width:7px;height:7px;border-radius:4px;background:#0E9F6E;"></span></span>
          <div><div style="font-size:12.5px;font-weight:700;color:#0A7C56;">下架该商品并通知卖家</div>
            <div style="font-size:10.5px;color:#9AA8B8;margin-top:2px;">商品状态变为「已下架」，不再出现在公开查询结果，且不能被预约</div></div>
        </div>
        <div style="display:flex;align-items:center;gap:9px;border:1px solid var(--line);border-radius:9px;padding:9px 11px;">
          <span style="width:16px;height:16px;border-radius:8px;border:2px solid #D3DBE4;"></span>
          <div><div style="font-size:12.5px;font-weight:700;">驳回举报</div>
            <div style="font-size:10.5px;color:#9AA8B8;margin-top:2px;">记录驳回理由，商品保持原状态</div></div>
        </div>
      </div>
      <div style="display:flex;gap:9px;margin-top:12px;">
        <div class="btn ghost" style="flex:1;">查看卖家历史</div>
        <div class="btn primary" style="flex:1;">提交处理结果</div>
      </div>
      <div style="font-size:10.5px;color:#9AA8B8;margin-top:7px;line-height:1.6;">已处理举报不能重复处理；处置动作与理由将写入举报记录与操作日志，卖家可通过通知查看结果。</div>
    </div>
  </div>
</div>
"""
apage("界面10.html", "举报处理", "举报处理", "运营管理 / 违规处置", report_body)

# =====================================================================
# 界面 11  操作日志
# =====================================================================
LOGS = [
    ("2026-10-26 09:12:41", "黄毅", "管理员", "审核通过", "商品 ID 20261024 高等数学第七版", "成功", "green"),
    ("2026-10-26 08:52:07", "李同学", "普通用户", "提交审核", "商品 ID 20261025 罗技机械键盘", "成功", "green"),
    ("2026-10-26 08:41:33", "王同学", "普通用户", "预约商品", "商品 ID 20261024 高等数学第七版", "失败 · 商品已有有效预约", "red"),
    ("2026-10-26 08:12:55", "王同学", "普通用户", "提交举报", "举报 REP-20261026-0031", "成功", "green"),
    ("2026-10-25 22:40:10", "黄毅", "管理员", "处置举报（下架）", "商品 ID 20261018 代写课程设计", "成功", "green"),
    ("2026-10-25 21:07:48", "陈同学", "普通用户", "取消预约", "商品 ID 20261011 iPad 9代", "成功", "green"),
    ("2026-10-25 20:33:26", "赵同学", "普通用户", "访问受限资源", "全站统计接口", "失败 · 无管理员权限", "red"),
    ("2026-10-25 19:58:02", "系统调度", "系统", "超时自动完成", "商品 ID 20261002 宿舍台灯", "成功", "green"),
    ("2026-10-25 17:20:44", "刘同学", "普通用户", "发布商品草稿", "商品 ID 20261021 捷安特山地车", "成功", "green"),
    ("2026-10-25 16:03:19", "黄毅", "管理员", "驳回商品", "商品 ID 20261019 网图二手球鞋", "成功", "green"),
    ("2026-10-25 14:47:58", "李同学", "普通用户", "下架商品", "商品 ID 20261015 四六级词汇书", "成功", "green"),
    ("2026-10-25 11:22:35", "陈同学", "普通用户", "重复提交预约", "商品 ID 20261011 iPad 9代", "幂等返回原结果", "gray"),
]
def log_row(i, r):
    tm, op, role, act, obj, res, cls = r
    return f"""<tr><td class="muted" style="white-space:nowrap;">{tm}</td>
  <td><b style="color:var(--ink);font-weight:600;">{op}</b></td><td class="muted">{role}</td>
  <td>{act}</td><td>{obj}</td><td><span class="tag {cls}">{res}</span></td></tr>"""

log_body = f"""
<div class="panel" style="flex:1;min-height:0;">
  <div class="ph"><b>操作日志</b><div class="sp">日志只追加、不可修改与删除，保留 180 天</div></div>
  <div style="display:flex;gap:10px;padding:12px 16px;border-bottom:1px solid var(--line);align-items:center;flex-wrap:wrap;">
    <div style="height:30px;border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;padding:0 11px;font-size:12px;color:var(--sub);width:150px;">操作人 / 学号</div>
    <div style="height:30px;border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;padding:0 11px;font-size:12px;color:var(--ink-2);gap:26px;">操作类型<span style="color:#B6C1CD;">▾</span></div>
    <div style="height:30px;border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;padding:0 11px;font-size:12px;color:var(--ink-2);gap:10px;">2026-10-01 <span style="color:#B6C1CD;">→</span> 2026-10-26</div>
    <div class="btn primary" style="height:30px;">查询</div>
    <div class="btn ghost" style="height:30px;">重置</div>
    <div style="margin-left:auto;font-size:11.5px;color:var(--sub);">共 1,284 条记录</div>
  </div>
  <div class="scroll" style="flex:1;">
    <table>
      <thead><tr><th style="width:150px;">时间</th><th>操作人</th><th>角色</th><th>操作类型</th><th>操作对象</th><th>结果</th></tr></thead>
      <tbody>{''.join(log_row(i, r) for i, r in enumerate(LOGS))}</tbody>
    </table>
  </div>
  <div style="padding:11px 16px;border-top:1px solid var(--line);display:flex;align-items:center;font-size:11.5px;color:var(--sub);">
    <span>失败操作同样记录失败原因（如并发冲突、越权访问）</span>
    <span style="margin-left:auto;">每页 20 条 <b style="color:var(--ink);margin-left:8px;">1</b> 2 3 … 65</span>
  </div>
</div>
"""
apage("界面11.html", "操作日志", "操作日志", "运营管理 / 日志审计", log_body)

# =====================================================================
# 界面 12  数据统计
# =====================================================================
line_pts = "0,110 40,96 80,102 120,78 160,84 200,62 240,68 280,44 320,52 360,34 400,40 440,24 480,30 520,16"
line_area = line_pts + " 520,140 0,140"

stat_body = f"""
<div style="display:flex;align-items:center;gap:10px;">
  <div style="display:flex;gap:6px;">
    <span class="tag green" style="height:28px;padding:0 12px;">近 7 天</span>
    <span class="tag gray" style="height:28px;padding:0 12px;">近 30 天</span>
    <span class="tag gray" style="height:28px;padding:0 12px;">本学期</span>
  </div>
  <div class="btn ghost" style="height:28px;">导出报表</div>
  <div style="margin-left:auto;font-size:11.5px;color:var(--sub);">统计口径：已完成的预约计为一次成交；时间范围开始晚于结束将返回参数错误</div>
</div>
<div class="kpis">
  <div class="kpi"><div class="t">商品总数</div><div class="v">1,482</div><div class="d">较上周 +6.2%</div></div>
  <div class="kpi"><div class="t">用户总数</div><div class="v">936</div><div class="d">较上周 +3.1%</div></div>
  <div class="kpi"><div class="t">累计成交</div><div class="v">418</div><div class="d">成交额 ¥37,426</div></div>
  <div class="kpi"><div class="t">举报处理率</div><div class="v">96.4%</div><div class="d warn">3 条待处理</div></div>
</div>
<div style="display:flex;gap:14px;flex:1.35;min-height:0;">
  <div class="panel" style="flex:1.5;">
    <div class="ph"><b>近 14 天成交趋势</b><div class="sp">单位：笔</div></div>
    <div style="padding:14px 18px;flex:1;">
      <svg width="100%" height="180" viewBox="0 0 540 150" preserveAspectRatio="none">
        <defs><linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#0E9F6E" stop-opacity=".22"/><stop offset="100%" stop-color="#0E9F6E" stop-opacity="0"/>
        </linearGradient></defs>
        {''.join(f'<line x1="0" y1="{y}" x2="540" y2="{y}" stroke="#EFF3F7" stroke-width="1"/>' for y in (20,50,80,110,140))}
        <polygon points="{line_area}" fill="url(#g1)"/>
        <polyline points="{line_pts}" fill="none" stroke="#0E9F6E" stroke-width="2.4" stroke-linejoin="round"/>
        <circle cx="520" cy="16" r="3.5" fill="#fff" stroke="#0E9F6E" stroke-width="2.4"/>
      </svg>
      <div style="display:flex;justify-content:space-between;font-size:10.5px;color:#AAB5C2;margin-top:4px;">
        <span>10-13</span><span>10-16</span><span>10-19</span><span>10-22</span><span>10-26</span>
      </div>
    </div>
  </div>
  <div class="panel" style="flex:1;">
    <div class="ph"><b>分类分布</b><div class="sp">已发布商品</div></div>
    <div style="padding:14px 18px;flex:1;">
      {''.join(f'''<div style="margin-bottom:13px;">
        <div style="display:flex;font-size:11.5px;margin-bottom:5px;"><span>{n}</span><span style="margin-left:auto;color:#7A8798;">{v} 件</span></div>
        <div style="height:7px;border-radius:4px;background:#EFF3F7;"><div style="width:{p}%;height:7px;border-radius:4px;background:{c};"></div></div>
      </div>''' for n, v, p, c in [("教材书籍", 486, 88, "#0E9F6E"), ("数码电子", 372, 68, "#3E9E8A"), ("生活用品", 284, 52, "#66B79A"), ("运动户外", 198, 36, "#93C7A9"), ("其他", 142, 26, "#C3D8CB")])}
    </div>
  </div>
</div>
<div class="panel" style="flex:1.05;min-height:0;">
    <div class="ph"><b>分类明细（近 7 天）</b><div class="sp">成交率 = 已完成 / 已发布</div></div>
    <div class="scroll" style="flex:1;">
      <table>
        <thead><tr><th>分类</th><th>发布</th><th>被预约</th><th>已完成</th><th>成交额</th><th>成交率</th></tr></thead>
        <tbody><tr><td><b style="color:var(--ink);font-weight:600;">教材书籍</b></td><td>486</td><td>92</td><td>68</td><td style="color:#F4511E;font-weight:700;">¥4,286</td><td><span class="tag green">13.9%</span></td></tr><tr><td><b style="color:var(--ink);font-weight:600;">数码电子</b></td><td>372</td><td>61</td><td>47</td><td style="color:#F4511E;font-weight:700;">¥21,940</td><td><span class="tag green">12.6%</span></td></tr><tr><td><b style="color:var(--ink);font-weight:600;">生活用品</b></td><td>284</td><td>38</td><td>31</td><td style="color:#F4511E;font-weight:700;">¥2,316</td><td><span class="tag gray">10.9%</span></td></tr><tr><td><b style="color:var(--ink);font-weight:600;">运动户外</b></td><td>198</td><td>24</td><td>19</td><td style="color:#F4511E;font-weight:700;">¥5,120</td><td><span class="tag gray">9.6%</span></td></tr></tbody>
      </table>
    </div>
</div>
"""
apage("界面12.html", "数据统计", "数据统计", "运营管理 / 统计分析", stat_body)
