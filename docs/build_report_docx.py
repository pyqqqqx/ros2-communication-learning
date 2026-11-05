# -*- coding: utf-8 -*-
import os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

OUT = r"C:\Users\lenovo\Documents\deepseek-harness\default-workspace\车队通讯任务_交付报告.docx"

DARK = (0x1F, 0x3B, 0x73)
GREY = (0x59, 0x59, 0x59)


def set_run_font(run, latin='宋体', east='宋体', size=None, bold=None, color=None):
    run.font.name = latin
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = rPr.makeelement(qn('w:rFonts'), {})
        rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), east)
    rFonts.set(qn('w:ascii'), latin)
    rFonts.set(qn('w:hAnsi'), latin)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor(*color)


def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    if level == 1:
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        size = 15
    elif level == 2:
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        size = 12.5
    else:
        size = 11
    r = p.add_run(text)
    set_run_font(r, latin='黑体', east='黑体', size=size, bold=True, color=DARK)
    return p


def add_body(doc, text, size=10.5, bold_prefix=None, center=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.35
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if bold_prefix:
        r0 = p.add_run(bold_prefix)
        set_run_font(r0, size=size, bold=True)
    r = p.add_run(text)
    set_run_font(r, size=size)
    return p


def add_code_block(doc, text, size=8.5):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    cell = t.rows[0].cells[0]
    cell.width = Cm(15.6)
    t.columns[0].width = Cm(15.6)
    _tblPr = t._tbl.tblPr
    _tblW = _tblPr.find(qn('w:tblW'))
    if _tblW is None:
        _tblW = _tblPr.makeelement(qn('w:tblW'), {})
        _tblPr.append(_tblW)
    _tblW.set(qn('w:type'), 'dxa')
    _tblW.set(qn('w:w'), str(int(round(15.6 * 566.93))))
    tcPr = cell._tc.get_or_add_tcPr()
    shd = tcPr.makeelement(qn('w:shd'), {})
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'F3F3F3')
    tcPr.append(shd)
    cell.text = ''
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    lines = text.rstrip('\n').split('\n')
    for i, line in enumerate(lines):
        if i > 0:
            p.add_run().add_break()
        r = p.add_run(line if line else ' ')
        set_run_font(r, latin='Consolas', east='宋体', size=size)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def add_table(doc, headers, rows, widths=None, center_cols=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ''
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        set_run_font(r, size=9.5, bold=True)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ''
            p = cells[i].paragraphs[0]
            if center_cols and i in center_cols:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val))
            set_run_font(r, size=9)
    if widths:
        total_tw = int(round(sum(widths) * 566.93))
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
        tblPr = t._tbl.tblPr
        tblW = tblPr.find(qn('w:tblW'))
        if tblW is None:
            tblW = tblPr.makeelement(qn('w:tblW'), {})
            tblPr.append(tblW)
        tblW.set(qn('w:type'), 'dxa')
        tblW.set(qn('w:w'), str(total_tw))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


# ---------------- build ----------------
doc = Document()
normal = doc.styles['Normal']
normal.font.name = '宋体'
normal.font.size = Pt(10.5)
rpr = normal.element.get_or_add_rPr()
rfonts = rpr.find(qn('w:rFonts'))
if rfonts is None:
    rfonts = rpr.makeelement(qn('w:rFonts'), {})
    rpr.append(rfonts)
rfonts.set(qn('w:eastAsia'), '宋体')
rfonts.set(qn('w:ascii'), '宋体')
rfonts.set(qn('w:hAnsi'), '宋体')

sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.2)
sec.bottom_margin = Cm(2.2)
sec.left_margin = Cm(2.4)
sec.right_margin = Cm(2.4)

# title
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('智能巴哈车队 · 规控组')
set_run_font(r, latin='黑体', east='黑体', size=13, bold=True, color=GREY)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(2)
p.paragraph_format.space_after = Pt(10)
r = p.add_run('ROS2 通讯任务交付报告')
set_run_font(r, latin='黑体', east='黑体', size=22, bold=True, color=DARK)

for k, v in [
    ('提交人', 'pyqqqqx（规控组）'),
    ('提交日期', '2026-11-04'),
    ('运行环境', 'VMware 虚拟机 + Ubuntu 22.04 + ROS2 Humble'),
    ('代码仓库', 'https://github.com/pyqqqqx/ros2-communication-learning'),
]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    r1 = p.add_run(k + '：')
    set_run_font(r1, size=10, bold=True)
    r2 = p.add_run(v)
    set_run_font(r2, size=10)

# 一
add_heading(doc, '一、任务概述', 1)
add_body(doc, '本次任务完整走通一次 ROS2 通讯链路，覆盖以下四个环节：')
for i, t in enumerate([
    '读队友发布：接收队友（陈明丰）的 5 个发布节点数据；',
    '接收方计算：订阅队友数据，按指定公式计算并发布结果；',
    '自定义接口：定义自定义消息 MyData.msg；',
    '自己的发布：参数化节点 + launch 一键启动 5 个发布节点。',
], 1):
    add_body(doc, t, bold_prefix='%d. ' % i)

# 二
add_heading(doc, '二、交付内容', 1)
add_body(doc, '共 5 个功能包，位于仓库 src/ 目录，也可通过 ros2_task_deliver.tar.gz 一键解压使用。')
add_table(doc,
    ['包名', '类型', '作用'],
    [
        ['data_publisher', 'ament_python', '队友发布方，5 个节点向 /node1~5 发数据（5Hz）'],
        ['status_interfaces', 'ament_cmake', '队友的消息接口 Data.msg'],
        ['data_subscriber', 'ament_python', '接收计算：calc1 / calc2 / final 三个节点'],
        ['my_interfaces', 'ament_cmake', '自定义消息接口 MyData.msg'],
        ['my_publisher', 'ament_python', '参数化发布节点 my_pub_1~5 + launch'],
    ],
    widths=[4.0, 3.0, 8.6], center_cols={1})

add_heading(doc, '消息定义', 2)
add_code_block(doc,
    'builtin_interfaces/Time stamp      # 时间戳\n'
    'float32[3] data_group              # 三维数组，分别记为 a、b、c')

add_heading(doc, '计算逻辑', 2)
add_table(doc,
    ['节点', '订阅', '公式', '输出话题'],
    [
        ['calc1_node', '/node1 /node2 /node3', '(a1+a2+a3) - (b1+b2+b3) + (c1+c2+c3)', '/calc1_result'],
        ['calc2_node', '/node4 /node5', '(a4+b4) * (a5-b5)', '/calc2_result'],
        ['final_node', '/calc1_result /calc2_result', '捕获并打印两路结果', '—'],
    ],
    widths=[3.0, 4.0, 5.6, 3.0])

# 三
add_heading(doc, '三、通讯链路', 1)
add_code_block(doc,
    '队友链：data_pub_1~5 ──► /node1~5 ──► calc1/calc2 ──► /calc1_result、/calc2_result ──► final_node\n'
    '自己链：my_pub_1~5  ──► /pub1~5 (MyData, 5Hz)')

# 四
add_heading(doc, '四、复现步骤', 1)
add_body(doc, '环境：Ubuntu 22.04 + ROS2 Humble。', bold_prefix='')
add_code_block(doc,
    '# 1. 放入工作空间\n'
    'mkdir -p ~/ros2_ws/src\n'
    'tar xzf ros2_task_deliver.tar.gz -C ~/ros2_ws/src\n'
    '\n'
    '# 2. 编译\n'
    'cd ~/ros2_ws\n'
    'colcon build\n'
    '\n'
    '# 3. 配置环境（每个新终端都要执行）\n'
    'source /opt/ros/humble/setup.bash\n'
    'source ~/ros2_ws/install/setup.bash\n'
    '\n'
    '# 4. 启动节点\n'
    'ros2 launch data_publisher pub_launch.py   # 队友的 5 个发布节点\n'
    'ros2 launch my_publisher pub_launch.py     # 自己的 5 个发布节点\n'
    'ros2 run data_subscriber calc1_node\n'
    'ros2 run data_subscriber calc2_node\n'
    'ros2 run data_subscriber final_node\n'
    '\n'
    '# 5. 验证\n'
    'ros2 topic list\n'
    'ros2 topic echo /pub1\n'
    'ros2 topic echo /node1\n'
    'ros2 topic echo /calc1_result\n'
    'ros2 topic hz /pub1')

# 五
add_heading(doc, '五、实测验证结果', 1)
add_table(doc,
    ['验证项', '结果'],
    [
        ['colcon build', '5 packages finished，编译成功'],
        ['节点启动', 'data_pub_1~5、my_pub_1~5、calc1/calc2/final 共 13 个'],
        ['话题齐全', '/node1~5、/pub1~5、/calc1_result、/calc2_result'],
        ['/pub1 频率', '实测 5.0 Hz'],
        ['计算结果', '/calc1_result、/calc2_result 实时输出'],
        ['final_node', '正常捕获并打印两路结果'],
    ],
    widths=[3.6, 12.0])
add_body(doc, '示例输出：')
add_code_block(doc,
    '==PUB1_ECHO==\n'
    'stamp: { sec: 1793795255, nanosec: 823358244 }\n'
    'data_group: [0.00327, -15.10059, 15.15399]\n'
    '\n'
    '==CALC1_RESULT== data: -49.33376693725586\n'
    '==CALC2_RESULT== data: -262.0841064453125\n'
    '\n'
    '==HZ_PUB1== average rate: 5.001\n'
    '\n'
    '[final_node] [捕获] 计算节点1结果 = -34.6329\n'
    '[final_node] [捕获] 计算节点2结果 = -258.7744')

# 六
add_heading(doc, '六、本次修复说明', 1)
add_body(doc, 'calc1_node.py、calc2_node.py、final_node.py、my_pub.py 四个文件末尾的守卫语句被写成 '
             'if __name__ == \'__&#8203;main__\':，其中混入了字面量 &#8203;（零宽字符）。', bold_prefix='问题：')
add_body(doc, '直接 python3 xxx.py 运行不会进入 main()。', bold_prefix='现象：')
add_body(doc, '仅影响「脚本直接运行」。ros2 run / ros2 launch 走 setup.py 的 entry_points 直接调用 main()，不受影响。', bold_prefix='影响范围：')
add_body(doc, '统一改为标准的「if __name__ == \'__main__\':」写法。', bold_prefix='修复：')
add_body(doc, '已修复、重新打包，并推送至 GitHub（commit d97566b）。', bold_prefix='状态：')

# 七
add_heading(doc, '七、已知问题与建议', 1)
for i, t in enumerate([
    '计算节点采用「缓存最新值」策略（做法 A），多个话题之间未做时间戳对齐，属任务允许的简化。',
    '环境未安装 Gazebo（本任务不需要；如有仿真需求可后续安装 ros2-humble-gazebo-ros-pkgs）。',
    '编码建议：Python 代码优先用 VS Code 编辑，终端只敲命令，避免粘贴引入零宽字符等不可见字符。',
], 1):
    add_body(doc, t, bold_prefix='%d. ' % i)

# 八
add_heading(doc, '八、交付清单', 1)
add_table(doc,
    ['序号', '交付物', '位置'],
    [
        ['1', '5 个功能包源码', 'GitHub 仓库 src/ 目录'],
        ['2', '交付压缩包', 'ros2_task_deliver.tar.gz'],
        ['3', '复现步骤', '本报告第四节'],
    ],
    widths=[1.6, 4.4, 10.0], center_cols={0})

# 九
add_heading(doc, '九、结论', 1)
add_body(doc, '本次车队通讯任务已完成，兼容 ROS2 Humble，发布/订阅/计算/自定义接口链路全部跑通，'
             '相关零宽字符缺陷已修复并上传仓库，可交付验收。')

doc.save(OUT)
print('SAVED:', OUT)
print('SIZE:', os.path.getsize(OUT))
