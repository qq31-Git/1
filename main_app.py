"""
住境通：无障碍社区AI规划平台
主应用程序文件
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
import base64
import json
import requests
from datetime import datetime
import os
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="住境通：无障碍社区AI规划",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1B4965;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #2E86AB;
        padding-left: 15px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #2E86AB;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1B4965;
    }
    .highlight {
        background-color: #E8F4F8;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #2E86AB;
    }
    .icon {
        font-size: 1.5rem;
        margin-right: 10px;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)

# 应用标题
st.markdown('<h1 class="main-header">♿ 住境通：无障碍社区AI规划平台</h1>', unsafe_allow_html=True)

# 初始化会话状态
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'generated_plan' not in st.session_state:
    st.session_state.generated_plan = None
if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = []
if 'community_data' not in st.session_state:
    st.session_state.community_data = None

# 侧边栏导航
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/accessibility2.png", width=80)
    st.markdown("## 导航菜单")
    
    page = st.radio(
        "选择功能模块",
        ["🏠 首页总览", "📊 社区数据上传", "🖼️ 无障碍设施分析", "🧠 AI智能规划", "📋 改造方案生成", "📈 效果评估模拟", "👥 社区参与反馈"]
    )
    
    st.markdown("---")
    st.markdown("### 社区信息")
    community_name = st.text_input("社区名称", "阳光花园社区")
    community_type = st.selectbox(
        "社区类型",
        ["老旧小区", "新建商品房", "混合型社区", "保障房社区", "其他"]
    )
    
    st.markdown("---")
    st.markdown("### 无障碍关注群体")
    focus_groups = st.multiselect(
        "重点服务群体",
        ["老年人", "轮椅使用者", "视障人士", "听障人士", "孕妇儿童", "临时行动不便者"],
        default=["老年人", "轮椅使用者"]
    )
    
    st.markdown("---")
    st.markdown("#### 技术支持")
    st.caption("基于开源AI模型构建")
    st.caption("数据安全 | 隐私保护")

# 首页总览模块
if page == "🏠 首页总览":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("无障碍设施覆盖率", "65%", "12%")
        st.caption("基于AI识别分析")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("高风险区域", "8处", "-3处")
        st.caption("需要优先改造")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("预计受益居民", "342人", "15%")
        st.caption("重点群体覆盖")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="sub-header">平台核心功能</h2>', unsafe_allow_html=True)
    
    features = [
        {"title": "智能图像识别", "desc": "自动识别无障碍设施问题", "icon": "🖼️"},
        {"title": "多维度评估", "desc": "全面评估社区无障碍水平", "icon": "📊"},
        {"title": "AI规划方案", "desc": "生成个性化改造方案", "icon": "🧠"},
        {"title": "三维可视化", "desc": "模拟改造效果", "icon": "👁️"},
        {"title": "成本效益分析", "desc": "优化资源配置", "icon": "💰"},
        {"title": "社区参与", "desc": "收集居民反馈建议", "icon": "👥"}
    ]
    
    cols = st.columns(3)
    for i, feature in enumerate(features):
        with cols[i % 3]:
            st.markdown(f'<div class="highlight"><span class="icon">{feature["icon"]}</span><strong>{feature["title"]}</strong><br><small>{feature["desc"]}</small></div>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="sub-header">快速开始指南</h2>', unsafe_allow_html=True)
    
    steps = [
        "1. 上传社区基本数据和图片",
        "2. AI自动分析无障碍设施现状",
        "3. 获取智能生成的改造方案",
        "4. 模拟改造效果并优化",
        "5. 导出完整规划报告"
    ]
    
    for step in steps:
        st.markdown(f'<div class="highlight">{step}</div>', unsafe_allow_html=True)

# 社区数据上传模块
elif page == "📊 社区数据上传":
    st.markdown('<h2 class="sub-header">社区数据上传与管理</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["基础信息", "空间数据", "人口数据"])
    
    with tab1:
        st.subheader("社区基本信息")
        
        col1, col2 = st.columns(2)
        with col1:
            total_area = st.number_input("社区总面积（㎡）", min_value=0.0, value=50000.0, step=1000.0)
            building_count = st.number_input("建筑物数量", min_value=1, value=25, step=1)
            road_length = st.number_input("道路总长度（米）", min_value=0.0, value=3500.0, step=100.0)
        
        with col2:
            establishment_year = st.number_input("建成年代", min_value=1950, max_value=2023, value=1998, step=1)
            property_type = st.selectbox("产权类型", ["单位房改房", "商品房", "保障房", "混合产权", "其他"])
            management_type = st.selectbox("物业管理类型", ["专业物业", "社区代管", "业委会自管", "无管理"])
        
        # 无障碍设施现状调查
        st.subheader("现有无障碍设施调查")
        
        facilities = {
            "无障碍坡道": st.slider("无障碍坡道（处）", 0, 50, 12),
            "无障碍电梯": st.slider("无障碍电梯（部）", 0, 20, 3),
            "盲道系统": st.slider("盲道长度（米）", 0, 5000, 850),
            "无障碍卫生间": st.slider("无障碍卫生间（个）", 0, 30, 5),
            "扶手栏杆": st.slider("扶手栏杆（米）", 0, 1000, 320),
            "无障碍车位": st.slider("无障碍车位（个）", 0, 50, 8)
        }
        
        # 保存数据到会话状态
        if st.button("保存基础信息"):
            st.session_state.community_data = {
                "basic_info": {
                    "total_area": total_area,
                    "building_count": building_count,
                    "road_length": road_length,
                    "establishment_year": establishment_year,
                    "property_type": property_type,
                    "management_type": management_type
                },
                "facilities": facilities
            }
            st.success("基础信息保存成功！")
    
    with tab2:
        st.subheader("空间数据上传")
        
        # 上传社区平面图
        uploaded_map = st.file_uploader("上传社区平面图（支持JPG, PNG）", type=['jpg', 'jpeg', 'png'])
        if uploaded_map is not None:
            image = Image.open(uploaded_map)
            st.image(image, caption="社区平面图", use_column_width=True)
            st.session_state.community_map = image
        
        # 上传设施图片
        uploaded_images = st.file_uploader(
            "上传无障碍设施照片（可多选）", 
            type=['jpg', 'jpeg', 'png'], 
            accept_multiple_files=True
        )
        
        if uploaded_images:
            st.session_state.uploaded_images = []
            cols = st.columns(3)
            for i, img_file in enumerate(uploaded_images):
                img = Image.open(img_file)
                st.session_state.uploaded_images.append(img)
                with cols[i % 3]:
                    st.image(img, caption=f"设施图片 {i+1}", width=200)
    
    with tab3:
        st.subheader("人口结构与需求数据")
        
        col1, col2 = st.columns(2)
        with col1:
            total_residents = st.number_input("总居民数", min_value=1, value=1250, step=10)
            elderly_count = st.number_input("65岁以上老年人数", min_value=0, value=186, step=1)
            disabled_count = st.number_input("持证残疾人数", min_value=0, value=42, step=1)
        
        with col2:
            children_count = st.number_input("12岁以下儿童数", min_value=0, value=153, step=1)
            pregnant_count = st.number_input("孕妇人数", min_value=0, value=18, step=1)
            temporary_disabled = st.number_input("临时行动不便者", min_value=0, value=25, step=1)
        
        # 需求调研
        st.subheader("无障碍需求调研")
        needs = st.multiselect(
            "居民最关注的无障碍需求",
            [
                "楼道加装扶手", "坡道改造", "电梯加装",
                "卫生间改造", "道路平整", "盲道完善",
                "停车位优化", "标识系统", "休息座椅"
            ],
            default=["楼道加装扶手", "坡道改造", "电梯加装"]
        )
        
        urgency = st.slider("改造紧迫性评分", 1, 10, 7)
        
        if st.button("保存人口数据"):
            st.session_state.population_data = {
                "total_residents": total_residents,
                "elderly_count": elderly_count,
                "disabled_count": disabled_count,
                "children_count": children_count,
                "pregnant_count": pregnant_count,
                "temporary_disabled": temporary_disabled,
                "needs": needs,
                "urgency": urgency
            }
            st.success("人口数据保存成功！")

# 无障碍设施分析模块
elif page == "🖼️ 无障碍设施分析":
    st.markdown('<h2 class="sub-header">AI无障碍设施智能分析</h2>', unsafe_allow_html=True)
    
    if 'uploaded_images' not in st.session_state or len(st.session_state.uploaded_images) == 0:
        st.warning("请先上传社区设施图片")
        if st.button("前往数据上传页面"):
            st.switch_page("📊 社区数据上传")
    else:
        st.success(f"已加载 {len(st.session_state.uploaded_images)} 张设施图片")
        
        # AI分析选项
        analysis_type = st.radio(
            "选择分析类型",
            ["自动全面分析", "特定设施分析", "问题检测分析"]
        )
        
        # 模拟AI分析功能
        class AIController:
            """模拟AI控制器"""
            
            @staticmethod
            def analyze_image(image):
                """模拟图像分析"""
                # 在实际应用中，这里会调用实际的AI模型
                # 例如：YOLO进行物体检测，SegFormer进行分割
                np.random.seed(hash(image.tobytes()) % 10000)
                
                # 模拟检测结果
                facilities = ["坡道", "扶手", "盲道", "电梯", "卫生间", "车位", "标识"]
                detected = np.random.choice(facilities, size=np.random.randint(2, 5), replace=False)
                
                # 模拟问题检测
                problems = ["高度不符", "宽度不足", "表面破损", "坡度超标", "缺乏防滑", "照明不足"]
                detected_problems = np.random.choice(problems, size=np.random.randint(1, 3), replace=False)
                
                # 模拟合规性评分
                compliance_score = np.random.randint(60, 95)
                
                return {
                    "detected_facilities": list(detected),
                    "detected_problems": list(detected_problems),
                    "compliance_score": compliance_score,
                    "recommendations": [
                        "建议增加防滑处理",
                        "宽度需扩大至1.2米",
                        "建议增加夜间照明"
                    ][:np.random.randint(1, 3)]
                }
            
            @staticmethod
            def generate_community_report(images_data):
                """生成社区整体报告"""
                total_score = np.mean([data["compliance_score"] for data in images_data])
                
                # 收集所有问题
                all_problems = []
                for data in images_data:
                    all_problems.extend(data["detected_problems"])
                
                # 统计问题频率
                from collections import Counter
                problem_counts = Counter(all_problems)
                
                return {
                    "overall_score": round(total_score, 1),
                    "total_facilities": len(images_data),
                    "problem_distribution": dict(problem_counts),
                    "priority_areas": [
                        {"area": "主入口坡道", "priority": "高"},
                        {"area": "3号楼电梯", "priority": "中"},
                        {"area": "社区服务中心", "priority": "高"}
                    ]
                }
        
        # 执行分析
        if st.button("开始AI分析", type="primary"):
            with st.spinner("AI正在分析设施图片..."):
                import time
                
                # 模拟分析过程
                progress_bar = st.progress(0)
                analysis_results = []
                
                for i, img in enumerate(st.session_state.uploaded_images):
                    time.sleep(0.5)  # 模拟处理时间
                    result = AIController.analyze_image(img)
                    analysis_results.append({
                        "image_id": i,
                        "result": result
                    })
                    progress_bar.progress((i + 1) / len(st.session_state.uploaded_images))
                
                # 生成整体报告
                images_data = [r["result"] for r in analysis_results]
                community_report = AIController.generate_community_report(images_data)
                
                # 保存到会话状态
                st.session_state.analysis_results = {
                    "detailed": analysis_results,
                    "community": community_report
                }
                
                st.success("分析完成！")
        
        # 显示分析结果
        if st.session_state.analysis_results:
            st.markdown("### 分析结果总览")
            
            report = st.session_state.analysis_results["community"]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总体合规分数", f"{report['overall_score']}/100")
            with col2:
                st.metric("分析设施数量", report["total_facilities"])
            with col3:
                st.metric("主要问题类型", len(report["problem_distribution"]))
            
            # 问题分布图表
            st.subheader("问题分布分析")
            if report['problem_distribution']:
                problem_df = pd.DataFrame({
                    '问题类型': list(report['problem_distribution'].keys()),
                    '出现次数': list(report['problem_distribution'].values())
                })
                
                fig = px.bar(problem_df, x='问题类型', y='出现次数', 
                           color='出现次数', title="无障碍问题分布")
                st.plotly_chart(fig, use_container_width=True)
            
            # 详细分析结果
            st.subheader("详细分析结果")
            for i, result in enumerate(st.session_state.analysis_results["detailed"]):
                with st.expander(f"图片 {i+1} 分析结果"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(st.session_state.uploaded_images[i], width=300)
                    with col2:
                        data = result["result"]
                        st.markdown(f"**检测到设施:** {', '.join(data['detected_facilities'])}")
                        st.markdown(f"**合规分数:** {data['compliance_score']}/100")
                        st.markdown(f"**发现问题:** {', '.join(data['detected_problems'])}")
                        st.markdown("**改进建议:**")
                        for rec in data.get('recommendations', []):
                            st.markdown(f"- {rec}")

# AI智能规划模块
elif page == "🧠 AI智能规划":
    st.markdown('<h2 class="sub-header">AI智能规划方案生成</h2>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_results:
        st.warning("请先进行无障碍设施分析")
        if st.button("前往分析页面"):
            st.switch_page("🖼️ 无障碍设施分析")
    else:
        # 规划参数设置
        st.subheader("规划参数设置")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            budget = st.number_input("预算总额（万元）", min_value=10.0, max_value=500.0, value=50.0, step=5.0)
            timeframe = st.selectbox("实施时间", ["1个月内", "3个月内", "6个月内", "1年内"])
        
        with col2:
            priority_focus = st.multiselect(
                "重点改造方向",
                ["出入口通达性", "楼内无障碍", "公共空间", "道路系统", "信息无障碍"],
                default=["出入口通达性", "楼内无障碍"]
            )
            
        with col3:
            implementation_phase = st.select_slider(
                "实施阶段",
                options=["试点改造", "重点区域", "全面推进", "完善提升"],
                value="重点区域"
            )
        
        # AI规划方案生成
        class AIPlanner:
            """AI规划方案生成器"""
            
            @staticmethod
            def generate_plan(analysis_results, params):
                """生成规划方案"""
                report = analysis_results["community"]
                
                # 基于分析结果生成方案
                plan = {
                    "basic_info": {
                        "budget": params["budget"],
                        "timeframe": params["timeframe"],
                        "priority_focus": params["priority_focus"],
                        "phase": params["phase"]
                    },
                    "projects": [],
                    "cost_breakdown": {},
                    "expected_benefits": {},
                    "timeline": []
                }
                
                # 根据问题分布生成项目
                problems = report.get("problem_distribution", {})
                
                # 坡道改造项目
                if any("坡" in p for p in problems):
                    plan["projects"].append({
                        "name": "主出入口坡道改造",
                        "description": "改造现有坡道，符合无障碍规范",
                        "cost": min(15, params["budget"] * 0.3),
                        "priority": "高",
                        "beneficiaries": ["轮椅使用者", "老年人", "婴儿车"],
                        "duration": "2周"
                    })
                
                # 扶手安装项目
                if any("扶手" in p for p in problems):
                    plan["projects"].append({
                        "name": "楼道扶手加装",
                        "description": "在主要楼道加装连续性扶手",
                        "cost": min(8, params["budget"] * 0.15),
                        "priority": "高",
                        "beneficiaries": ["老年人", "临时行动不便者"],
                        "duration": "3周"
                    })
                
                # 标识系统项目
                plan["projects"].append({
                    "name": "无障碍标识系统",
                    "description": "建立完整的无障碍导向标识",
                    "cost": min(5, params["budget"] * 0.1),
                    "priority": "中",
                    "beneficiaries": ["视障人士", "老年人", "访客"],
                    "duration": "1周"
                })
                
                # 休息设施项目
                plan["projects"].append({
                    "name": "休息座椅设置",
                    "description": "在关键节点设置休息座椅",
                    "cost": min(3, params["budget"] * 0.05),
                    "priority": "低",
                    "beneficiaries": ["老年人", "孕妇", "儿童"],
                    "duration": "1周"
                })
                
                # 成本分解
                total_cost = sum(p["cost"] for p in plan["projects"])
                plan["cost_breakdown"] = {
                    "工程费用": total_cost * 0.7,
                    "设计费用": total_cost * 0.1,
                    "管理费用": total_cost * 0.1,
                    "预备费用": total_cost * 0.1
                }
                
                # 预期效益
                plan["expected_benefits"] = {
                    "无障碍覆盖率提升": f"{min(40, int(problems.get('宽度不足', 0) * 10))}%",
                    "受益居民增加": f"{min(200, int(len(problems) * 30))}人",
                    "安全隐患减少": f"{len(problems)}处",
                    "居民满意度提升": "预计提升25%"
                }
                
                # 时间线
                plan["timeline"] = [
                    {"week": 1, "task": "现场勘察与设计"},
                    {"week": 2, "task": "材料采购与准备"},
                    {"week": 3, "task": "坡道改造施工"},
                    {"week": 4, "task": "扶手安装"},
                    {"week": 5, "task": "标识系统安装"},
                    {"week": 6, "task": "验收与调试"}
                ]
                
                return plan
        
        # 生成方案
        if st.button("生成AI规划方案", type="primary"):
            with st.spinner("AI正在生成优化方案..."):
                import time
                time.sleep(2)  # 模拟AI处理时间
                
                params = {
                    "budget": budget,
                    "timeframe": timeframe,
                    "priority_focus": priority_focus,
                    "phase": implementation_phase
                }
                
                plan = AIPlanner.generate_plan(st.session_state.analysis_results, params)
                st.session_state.generated_plan = plan
                
                st.success("规划方案生成完成！")
        
        # 显示方案
        if st.session_state.generated_plan:
            plan = st.session_state.generated_plan
            
            st.subheader("📋 规划方案总览")
            
            # 基本信息
            cols = st.columns(4)
            with cols[0]:
                st.metric("总预算", f"{plan['basic_info']['budget']}万元")
            with cols[1]:
                st.metric("实施周期", plan['basic_info']['timeframe'])
            with cols[2]:
                st.metric("项目数量", len(plan['projects']))
            with cols[3]:
                st.metric("重点方向", ", ".join(plan['basic_info']['priority_focus'][:2]))
            
            # 项目列表
            st.subheader("🏗️ 改造项目清单")
            for i, project in enumerate(plan['projects']):
                with st.expander(f"项目{i+1}: {project['name']} (优先级: {project['priority']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**描述:** {project['description']}")
                        st.markdown(f"**预算:** {project['cost']}万元")
                        st.markdown(f"**工期:** {project['duration']}")
                    with col2:
                        st.markdown("**受益群体:**")
                        for beneficiary in project['beneficiaries']:
                            st.markdown(f"- {beneficiary}")
            
            # 成本分析
            st.subheader("💰 成本分解")
            cost_df = pd.DataFrame({
                '项目': list(plan['cost_breakdown'].keys()),
                '金额(万元)': list(plan['cost_breakdown'].values())
            })
            
            fig = px.pie(cost_df, values='金额(万元)', names='项目', 
                        title="成本构成分析")
            st.plotly_chart(fig, use_container_width=True)
            
            # 预期效益
            st.subheader("📈 预期效益")
            benefits_df = pd.DataFrame({
                '指标': list(plan['expected_benefits'].keys()),
                '提升值': list(plan['expected_benefits'].values())
            })
            
            fig = px.bar(benefits_df, x='指标', y='提升值', 
                        color='指标', title="预期效益分析")
            st.plotly_chart(fig, use_container_width=True)
            
            # 实施时间线
            st.subheader("📅 实施时间线")
            timeline_df = pd.DataFrame(plan['timeline'])
            fig = px.timeline(timeline_df, x_start="week", x_end="week", y="task", 
                            title="项目实施时间线")
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

# 改造方案生成模块
elif page == "📋 改造方案生成":
    st.markdown('<h2 class="sub-header">完整改造方案生成</h2>', unsafe_allow_html=True)
    
    if not st.session_state.generated_plan:
        st.warning("请先生成AI规划方案")
        if st.button("前往规划页面"):
            st.switch_page("🧠 AI智能规划")
    else:
        plan = st.session_state.generated_plan
        
        # 方案自定义调整
        st.subheader("方案调整与优化")
        
        # 项目优先级调整
        st.markdown("#### 调整项目优先级")
        for i, project in enumerate(plan['projects']):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{project['name']}**")
            with col2:
                new_priority = st.selectbox(
                    "优先级",
                    ["高", "中", "低"],
                    index=["高", "中", "低"].index(project['priority']),
                    key=f"priority_{i}"
                )
                project['priority'] = new_priority
            with col3:
                new_cost = st.number_input(
                    "预算(万元)",
                    value=float(project['cost']),
                    min_value=0.0,
                    step=0.5,
                    key=f"cost_{i}"
                )
                project['cost'] = new_cost
        
        # 生成详细方案文档
        if st.button("生成详细方案报告", type="primary"):
            # 创建方案文档
            report_content = {
                "社区信息": st.session_state.community_data,
                "分析结果": st.session_state.analysis_results,
                "规划方案": plan,
                "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 显示方案报告
            st.subheader("📄 完整方案报告")
            
            tabs = st.tabs(["执行摘要", "技术方案", "施工图纸", "预算明细", "实施计划"])
            
            with tabs[0]:
                st.markdown("""
                ### 执行摘要
                
                **项目名称：** 无障碍社区改造项目
                **实施社区：** 阳光花园社区
                **核心目标：** 创建全龄友好、无障碍通达的宜居社区
                
                **主要改造内容：**
                1. 出入口无障碍坡道系统改造
                2. 楼道连续性扶手加装
                3. 无障碍标识系统完善
                4. 公共空间休息设施增设
                
                **预期成效：**
                - 无障碍设施覆盖率提升至85%以上
                - 惠及社区内全部行动不便居民
                - 创建可复制的社区改造样板
                """)
            
            with tabs[1]:
                st.markdown("""
                ### 技术方案详情
                
                **一、坡道改造技术标准**
                - 坡度：不大于1:12
                - 宽度：不小于1.2米
                - 防滑：采用防滑地砖或防滑条
                - 扶手：双侧设置，高度0.65-0.85米
                
                **二、扶手安装规范**
                - 材质：防锈防腐材料
                - 直径：35-45mm
                - 连续性：全程无间断
                - 末端处理：圆弧状延伸
                
                **三、标识系统设计**
                - 符合国家无障碍标识标准
                - 中英文对照
                - 夜间反光处理
                - 触觉标识辅助
                """)
            
            with tabs[2]:
                st.markdown("### 施工图纸示意")
                # 这里可以显示实际的CAD图纸或示意图
                st.image("https://via.placeholder.com/800x400?text=施工图纸示意", use_column_width=True)
                
                # 图纸说明
                st.markdown("""
                **图例说明：**
                - 红色：改造区域
                - 蓝色：新增设施
                - 绿色：保留设施
                - 虚线：建议路线
                """)
            
            with tabs[3]:
                st.markdown("### 详细预算表")
                budget_df = pd.DataFrame([
                    {"项目": "坡道改造", "单位": "处", "数量": 5, "单价(万元)": 2.5, "小计(万元)": 12.5},
                    {"项目": "扶手安装", "单位": "米", "数量": 200, "单价(万元)": 0.04, "小计(万元)": 8.0},
                    {"项目": "标识系统", "单位": "套", "数量": 1, "单价(万元)": 5.0, "小计(万元)": 5.0},
                    {"项目": "休息座椅", "单位": "个", "数量": 10, "单价(万元)": 0.3, "小计(万元)": 3.0},
                    {"项目": "设计监理", "单位": "项", "数量": 1, "单价(万元)": 4.0, "小计(万元)": 4.0},
                    {"项目": "预备费用", "单位": "项", "数量": 1, "单价(万元)": 2.5, "小计(万元)": 2.5},
                ])
                budget_df["总计(万元)"] = budget_df["小计(万元)"].sum()
                st.dataframe(budget_df, use_container_width=True)
            
            with tabs[4]:
                st.markdown("### 实施计划表")
                schedule_df = pd.DataFrame([
                    {"阶段": "准备阶段", "时间": "第1周", "任务": "现场勘测、方案确认", "负责人": "项目经理"},
                    {"阶段": "准备阶段", "时间": "第2周", "任务": "材料采购、施工准备", "负责人": "采购专员"},
                    {"阶段": "施工阶段", "时间": "第3-4周", "任务": "坡道改造施工", "负责人": "施工队长"},
                    {"阶段": "施工阶段", "时间": "第5周", "任务": "扶手安装", "负责人": "施工队长"},
                    {"阶段": "施工阶段", "时间": "第6周", "任务": "标识系统安装", "负责人": "技术员"},
                    {"阶段": "验收阶段", "时间": "第7周", "任务": "竣工验收", "负责人": "监理工程师"},
                    {"阶段": "维护阶段", "时间": "长期", "任务": "设施维护管理", "负责人": "物业公司"},
                ])
                st.dataframe(schedule_df, use_container_width=True)
            
            # 导出功能
            st.subheader("📤 方案导出")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("导出为PDF"):
                    st.success("PDF导出功能准备中...")
            
            with col2:
                if st.button("导出为Word"):
                    st.success("Word导出功能准备中...")
            
            with col3:
                if st.button("导出施工图纸"):
                    st.success("图纸导出功能准备中...")
            
            # 保存方案
            if st.button("保存方案到数据库"):
                st.session_state.saved_plans = st.session_state.get('saved_plans', []) + [report_content]
                st.success("方案保存成功！")

# 效果评估模拟模块
elif page == "📈 效果评估模拟":
    st.markdown('<h2 class="sub-header">改造效果评估与模拟</h2>', unsafe_allow_html=True)
    
    # 效果模拟参数
    st.subheader("模拟参数设置")
    
    col1, col2 = st.columns(2)
    with col1:
        simulation_type = st.selectbox(
            "模拟类型",
            ["无障碍通达性", "居民满意度", "经济效益", "社会效益"]
        )
        
        if simulation_type == "无障碍通达性":
            target_coverage = st.slider("目标覆盖率(%)", 50, 100, 85)
            implementation_rate = st.slider("实施进度(%)", 0, 100, 75)
        
        elif simulation_type == "居民满意度":
            before_score = st.slider("改造前满意度", 0, 100, 65)
            expected_improvement = st.slider("预期提升幅度", 0, 50, 25)
    
    with col2:
        time_horizon = st.selectbox(
            "时间范围",
            ["短期(1年)", "中期(3年)", "长期(5年)"]
        )
        
        compare_scenario = st.selectbox(
            "对比场景",
            ["维持现状", "部分改造", "全面改造", "理想方案"]
        )
    
    # 模拟结果可视化
    if st.button("运行模拟分析"):
        st.subheader("📊 模拟分析结果")
        
        # 生成模拟数据
        np.random.seed(42)
        
        if simulation_type == "无障碍通达性":
            # 通达性模拟
            months = list(range(1, 13))
            current_coverage = [65 + i * (target_coverage - 65) / 12 for i in range(12)]
            ideal_coverage = [65 + i * (95 - 65) / 12 for i in range(12)]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=current_coverage,
                                    mode='lines+markers',
                                    name='当前方案',
                                    line=dict(color='blue', width=3)))
            fig.add_trace(go.Scatter(x=months, y=ideal_coverage,
                                    mode='lines+markers',
                                    name='理想方案',
                                    line=dict(color='green', width=3, dash='dash')))
            
            fig.update_layout(
                title="无障碍通达性覆盖率模拟",
                xaxis_title="月份",
                yaxis_title="覆盖率(%)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 通达性指标
            metrics_cols = st.columns(4)
            with metrics_cols[0]:
                st.metric("当前通达指数", "72", "7")
            with metrics_cols[1]:
                st.metric("可达建筑数量", "18栋", "3栋")
            with metrics_cols[2]:
                st.metric("无障碍路径", "2.8km", "0.5km")
            with metrics_cols[3]:
                st.metric("关键节点覆盖", "85%", "15%")
        
        elif simulation_type == "居民满意度":
            # 满意度模拟
            groups = ['老年人', '轮椅使用者', '视障人士', '全体居民']
            before_scores = [60, 55, 50, 65]
            after_scores = [before_scores[i] + expected_improvement for i in range(4)]
            
            fig = go.Figure(data=[
                go.Bar(name='改造前', x=groups, y=before_scores, marker_color='lightgray'),
                go.Bar(name='改造后', x=groups, y=after_scores, marker_color='skyblue')
            ])
            
            fig.update_layout(
                title="不同群体满意度变化",
                barmode='group',
                yaxis_title="满意度评分"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 效益分析
        st.subheader("💰 效益成本分析")
        
        # 创建效益数据
        years = ['第1年', '第2年', '第3年', '第4年', '第5年']
        costs = [50, 10, 8, 7, 6]  # 维护成本逐年减少
        benefits = [30, 40, 50, 55, 60]  # 效益逐年增加
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=costs,
                                mode='lines+markers',
                                name='成本(万元)',
                                line=dict(color='red', width=2)))
        fig.add_trace(go.Scatter(x=years, y=benefits,
                                mode='lines+markers',
                                name='效益(万元)',
                                line=dict(color='green', width=2)))
        
        fig.update_layout(
            title="成本效益分析（5年周期）",
            xaxis_title="年份",
            yaxis_title="金额(万元)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ROI计算
        total_cost = sum(costs)
        total_benefit = sum(benefits)
        roi = ((total_benefit - total_cost) / total_cost) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总成本", f"{total_cost}万元")
        with col2:
            st.metric("总效益", f"{total_benefit}万元")
        with col3:
            st.metric("投资回报率", f"{roi:.1f}%")
        
        # 敏感性分析
        st.subheader("🔍 敏感性分析")
        
        sensitivity_factors = ['预算变化', '工期延迟', '材料涨价', '居民参与度']
        impact_scores = [8.5, 7.2, 6.8, 9.1]
        
        fig = px.bar(x=sensitivity_factors, y=impact_scores,
                    labels={'x': '影响因素', 'y': '影响程度'},
                    title="方案敏感性分析",
                    color=impact_scores,
                    color_continuous_scale='RdYlGn_r')
        
        st.plotly_chart(fig, use_container_width=True)

# 社区参与反馈模块
elif page == "👥 社区参与反馈":
    st.markdown('<h2 class="sub-header">社区参与与反馈收集</h2>', unsafe_allow_html=True)
    
    # 反馈收集
    st.subheader("📝 方案反馈收集")
    
    feedback_tabs = st.tabs(["居民反馈", "专家意见", "在线投票", "历史记录"])
    
    with feedback_tabs[0]:
        st.markdown("### 居民意见反馈")
        
        # 反馈表单
        with st.form("resident_feedback"):
            col1, col2 = st.columns(2)
            
            with col1:
                resident_type = st.selectbox(
                    "您属于哪类群体？",
                    ["老年人", "残障人士", "家属", "普通居民", "社区工作者"]
                )
                
                age_group = st.selectbox(
                    "年龄段",
                    ["18岁以下", "18-35岁", "36-59岁", "60-74岁", "75岁以上"]
                )
            
            with col2:
                contact_pref = st.selectbox(
                    "希望如何参与？",
                    ["提供意见", "参与讨论", "担任志愿者", "不需要参与"]
                )
                
                urgency_level = st.slider("改造紧迫性", 1, 10, 7)
            
            # 方案评分
            st.markdown("#### 方案评分")
            rating_cols = st.columns(5)
            
            ratings = {}
            with rating_cols[0]:
                ratings['实用性'] = st.slider("实用性", 1, 5, 4)
            with rating_cols[1]:
                ratings['可行性'] = st.slider("可行性", 1, 5, 3)
            with rating_cols[2]:
                ratings['经济性'] = st.slider("经济性", 1, 5, 3)
            with rating_cols[3]:
                ratings['美观性'] = st.slider("美观性", 1, 5, 4)
            with rating_cols[4]:
                ratings['满意度'] = st.slider("总体满意度", 1, 5, 4)
            
            # 意见反馈
            st.markdown("#### 具体意见")
            suggestions = st.text_area(
                "您的具体建议或意见",
                "例如：希望优先改造3号楼出入口，那里台阶太高..."
            )
            
            concerns = st.text_area(
                "您的担忧或顾虑",
                "例如：施工期间如何保证居民正常通行..."
            )
            
            # 提交按钮
            submitted = st.form_submit_button("提交反馈")
            
            if submitted:
                feedback_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": resident_type,
                    "age": age_group,
                    "ratings": ratings,
                    "suggestions": suggestions,
                    "concerns": concerns,
                    "urgency": urgency_level,
                    "contact_pref": contact_pref
                }
                
                # 保存反馈
                if 'feedback_list' not in st.session_state:
                    st.session_state.feedback_list = []
                
                st.session_state.feedback_list.append(feedback_data)
                st.success("感谢您的反馈！您的意见已记录。")
    
    with feedback_tabs[1]:
        st.markdown("### 专家评审意见")
        
        # 模拟专家意见
        expert_opinions = [
            {
                "专家": "王教授（无障碍设计）",
                "意见": "方案整体合理，建议增加触觉引导系统的设计",
                "评分": "8.5/10",
                "日期": "2024-01-15"
            },
            {
                "专家": "李工程师（建筑工程）",
                "意见": "施工方案可行，但需注意雨季施工安排",
                "评分": "8.0/10",
                "日期": "2024-01-18"
            },
            {
                "专家": "张主任（社区治理）",
                "意见": "居民参与机制需要进一步完善",
                "评分": "7.5/10",
                "日期": "2024-01-20"
            }
        ]
        
        for opinion in expert_opinions:
            with st.expander(f"{opinion['专家']} - 评分: {opinion['评分']}"):
                st.write(opinion["意见"])
                st.caption(f"提交日期: {opinion['日期']}")
    
    with feedback_tabs[2]:
        st.markdown("### 在线投票")
        
        voting_topics = [
            "是否同意优先改造主出入口？",
            "是否愿意为无障碍改造分摊部分费用？",
            "施工期间是否能接受暂时不便？",
            "是否愿意参与监督小组？"
        ]
        
        results = {}
        for topic in voting_topics:
            st.markdown(f"**{topic}**")
            
            if topic not in results:
                results[topic] = {"同意": 0, "反对": 0, "弃权": 0}
            
            cols = st.columns(3)
            with cols[0]:
                if st.button(f"👍 同意", key=f"agree_{topic}"):
                    results[topic]["同意"] += 1
            with cols[1]:
                if st.button(f"👎 反对", key=f"disagree_{topic}"):
                    results[topic]["反对"] += 1
            with cols[2]:
                if st.button(f"🤝 弃权", key=f"abstain_{topic}"):
                    results[topic]["弃权"] += 1
            
            # 显示当前结果
            total = sum(results[topic].values())
            if total > 0:
                st.progress(results[topic]["同意"] / total)
                st.caption(f"同意: {results[topic]['同意']} | 反对: {results[topic]['反对']} | 弃权: {results[topic]['弃权']}")
            
            st.markdown("---")
    
    with feedback_tabs[3]:
        st.markdown("### 历史反馈记录")
        
        if 'feedback_list' in st.session_state and st.session_state.feedback_list:
            feedback_df = pd.DataFrame(st.session_state.feedback_list)
            st.dataframe(feedback_df, use_container_width=True)
            
            # 反馈分析
            if len(st.session_state.feedback_list) >= 3:
                st.subheader("反馈分析")
                
                # 计算平均评分
                all_ratings = [f['ratings'] for f in st.session_state.feedback_list]
                avg_ratings = {}
                for key in all_ratings[0].keys():
                    avg_ratings[key] = sum(r[key] for r in all_ratings) / len(all_ratings)
                
                # 可视化评分
                rating_df = pd.DataFrame({
                    '指标': list(avg_ratings.keys()),
                    '平均分': list(avg_ratings.values())
                })
                
                fig = px.bar(rating_df, x='指标', y='平均分',
                            title="居民评分平均分",
                            color='平均分',
                            color_continuous_scale='RdYlGn')
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无反馈记录")
    
    # 参与度统计
    st.subheader("📊 社区参与度统计")
    
    participation_data = {
        "指标": ["反馈人数", "平均满意度", "建议采纳率", "参与积极性"],
        "数值": [
            len(st.session_state.get('feedback_list', [])),
            4.2 if st.session_state.get('feedback_list') else 0,
            78,
            85
        ],
        "目标": [50, 4.5, 80, 90]
    }
    
    participation_df = pd.DataFrame(participation_data)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='当前值',
        x=participation_df['指标'],
        y=participation_df['数值'],
        marker_color='lightblue'
    ))
    fig.add_trace(go.Bar(
        name='目标值',
        x=participation_df['指标'],
        y=participation_df['目标'],
        marker_color='lightgray',
        opacity=0.5
    ))
    
    fig.update_layout(
        title="社区参与度统计",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# 页脚
st.markdown("---")
footer_cols = st.columns(3)
with footer_cols[0]:
    st.caption("© 2024 住境通无障碍社区AI规划平台")
with footer_cols[1]:
    st.caption("技术支持：开源AI模型 + Streamlit")
with footer_cols[2]:
    st.caption("数据安全 | 隐私保护 | 持续更新")

# 运行说明
st.sidebar.markdown("---")
st.sidebar.markdown("### 运行说明")
st.sidebar.info("""
1. 首先上传社区数据和图片
2. 进行AI无障碍设施分析
3. 生成并优化规划方案
4. 模拟效果并收集反馈
5. 导出完整实施方案
""")