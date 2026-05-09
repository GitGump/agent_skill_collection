"""
商机管理数据分析脚本模板
使用方法：python analyze.py <excel_file_path>
"""

import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime

def load_data(file_path):
    """加载并预处理数据"""
    df = pd.read_excel(file_path)
    
    # 字段映射（处理不同命名习惯）
    field_mapping = {
        '客户名称': ['客户名称', '公司名称', '企业名称', 'name'],
        '申请日期': ['申请日期', '注册日期', '创建日期', '申请时间', 'date'],
        '客户来源': ['客户来源', '来源渠道', '渠道', 'source'],
        '手机号': ['手机号', '电话', '联系电话', 'phone', 'mobile'],
        '需求': ['需求', '客户需求', '需求描述', 'requirement'],
        '跟进次数': ['跟进次数', '跟进数', '跟进', 'follow_count'],
        '客户状态': ['客户状态', '状态', 'status'],
        '试用结束日期': ['试用结束日期', '试用截止', '到期时间', 'expire_date'],
    }
    
    # 标准化字段名
    for standard_name, alternatives in field_mapping.items():
        for alt in alternatives:
            if alt in df.columns and standard_name not in df.columns:
                df.rename(columns={alt: standard_name}, inplace=True)
                break
    
    # 转换日期
    if '申请日期' in df.columns:
        df['申请日期'] = pd.to_datetime(df['申请日期'], errors='coerce')
        df['月份'] = df['申请日期'].dt.month
        df['年月'] = df['申请日期'].dt.strftime('%Y-%m')
    
    # 转换跟进次数为数字
    if '跟进次数' in df.columns:
        df['跟进次数'] = pd.to_numeric(df['跟进次数'], errors='coerce').fillna(0)
    
    return df


def analyze_acquisition(df):
    """获客分析"""
    result = {}
    
    # 总量
    result['total'] = len(df)
    
    # 渠道分布
    if '客户来源' in df.columns:
        source_counts = df['客户来源'].value_counts()
        result['source_distribution'] = source_counts.to_dict()
        result['top_source'] = source_counts.index[0] if len(source_counts) > 0 else None
        result['top_source_pct'] = round(source_counts.iloc[0] / len(df) * 100, 1) if len(source_counts) > 0 else 0
    
    # 月度趋势
    if '月份' in df.columns:
        monthly = df.groupby('月份').size().to_dict()
        result['monthly_trend'] = monthly
        
        # 环比增长
        months = sorted(monthly.keys())
        if len(months) >= 2:
            prev = monthly[months[-2]]
            curr = monthly[months[-1]]
            result['mom_growth'] = round((curr - prev) / prev * 100, 1) if prev > 0 else 0
    
    return result


def analyze_followup(df):
    """跟进质量分析"""
    result = {}
    
    if '跟进次数' not in df.columns:
        return result
    
    # 跟进次数分布
    result['avg_followup'] = round(df['跟进次数'].mean(), 2)
    result['median_followup'] = df['跟进次数'].median()
    result['zero_followup_count'] = int((df['跟进次数'] == 0).sum())
    result['zero_followup_rate'] = round((df['跟进次数'] == 0).mean() * 100, 1)
    result['followup_rate'] = round((df['跟进次数'] > 0).mean() * 100, 1)
    result['deep_followup_rate'] = round((df['跟进次数'] >= 2).mean() * 100, 1)
    
    # 跟进次数分布
    followup_dist = {}
    for i in range(5):
        count = int((df['跟进次数'] == i).sum())
        followup_dist[str(i)] = count
    followup_dist['4+'] = int((df['跟进次数'] >= 4).sum())
    result['followup_distribution'] = followup_dist
    
    # 各渠道跟进率
    if '客户来源' in df.columns:
        channel_followup = df.groupby('客户来源').apply(
            lambda x: round((x['跟进次数'] > 0).mean() * 100, 1)
        ).to_dict()
        result['channel_followup_rate'] = channel_followup
    
    # 月度跟进率趋势
    if '月份' in df.columns:
        monthly_followup = df.groupby('月份').apply(
            lambda x: round((x['跟进次数'] > 0).mean() * 100, 1)
        ).to_dict()
        result['monthly_followup_rate'] = monthly_followup
    
    return result


def analyze_conversion(df):
    """转化率分析"""
    result = {}
    
    if '客户状态' not in df.columns:
        return result
    
    # 状态分布
    status_counts = df['客户状态'].value_counts()
    result['status_distribution'] = status_counts.to_dict()
    
    # 试用转化率
    trial_count = int((df['客户状态'] == '试用').sum())
    result['trial_count'] = trial_count
    result['trial_rate'] = round(trial_count / len(df) * 100, 1)
    
    # 各渠道转化率
    if '客户来源' in df.columns:
        channel_conversion = df.groupby('客户来源').apply(
            lambda x: round((x['客户状态'] == '试用').mean() * 100, 1)
        ).to_dict()
        result['channel_conversion_rate'] = channel_conversion
    
    # 月度转化率趋势
    if '月份' in df.columns:
        monthly_conversion = df.groupby('月份').apply(
            lambda x: round((x['客户状态'] == '试用').mean() * 100, 1)
        ).to_dict()
        result['monthly_conversion_rate'] = monthly_conversion
    
    return result


def analyze_channel_matrix(df):
    """渠道效能矩阵分析"""
    if '客户来源' not in df.columns:
        return {}
    
    channel_stats = df.groupby('客户来源').agg(
        count=('客户名称' if '客户名称' in df.columns else df.columns[0], 'count'),
        trial_rate=('客户状态', lambda x: round((x == '试用').mean() * 100, 1)) if '客户状态' in df.columns else ('客户来源', lambda x: 0),
        followup_rate=('跟进次数', lambda x: round((x > 0).mean() * 100, 1)) if '跟进次数' in df.columns else ('客户来源', lambda x: 0),
    ).reset_index()
    
    # 渠道分类
    total = len(df)
    high_volume_threshold = total * 0.1  # 占比10%以上为高量
    high_conversion_threshold = 70  # 转化率70%以上为高转化
    
    matrix = {}
    for _, row in channel_stats.iterrows():
        channel = row['客户来源']
        count = row['count']
        trial_rate = row.get('trial_rate', 0)
        followup_rate = row.get('followup_rate', 0)
        
        # 分类
        is_high_volume = count >= high_volume_threshold
        is_high_conversion = trial_rate >= high_conversion_threshold
        
        if is_high_volume and is_high_conversion:
            category = '重点维护'
        elif not is_high_volume and is_high_conversion:
            category = '放量渠道'
        elif is_high_volume and not is_high_conversion:
            category = '优化对象'
        else:
            category = '淘汰考虑'
        
        matrix[channel] = {
            'count': int(count),
            'trial_rate': trial_rate,
            'followup_rate': followup_rate,
            'category': category,
            'pct': round(count / total * 100, 1)
        }
    
    return matrix


def analyze_data_quality(df):
    """数据质量分析"""
    quality = {}
    
    # 各字段完整率
    fields_to_check = {
        '手机号': 0.4,    # 权重40%
        '需求': 0.3,       # 权重30%
        '试用结束日期': 0.3  # 权重30%
    }
    
    total_score = 0
    for field, weight in fields_to_check.items():
        if field in df.columns:
            # 计算非空且非空字符串的比例
            if df[field].dtype == object:
                non_empty = df[field].notna() & (df[field].astype(str).str.strip() != '') & (df[field].astype(str) != 'nan')
            else:
                non_empty = df[field].notna()
            rate = round(non_empty.mean() * 100, 1)
            quality[field] = rate
            total_score += rate * weight
        else:
            quality[field] = 0
    
    quality['comprehensive_score'] = round(total_score, 1)
    quality['grade'] = (
        '优秀' if total_score >= 85 else
        '良好' if total_score >= 70 else
        '及格' if total_score >= 55 else
        '需改善'
    )
    
    return quality


def generate_insights(acq, followup, conversion, matrix, quality):
    """生成核心洞察和建议"""
    insights = []
    actions = []
    
    # 洞察1：规模
    total = acq.get('total', 0)
    insights.append({
        'title': f'商机总量 {total} 家',
        'detail': f"主力渠道：{acq.get('top_source', 'N/A')}（{acq.get('top_source_pct', 0)}%）"
    })
    
    # 洞察2：转化
    trial_rate = conversion.get('trial_rate', 0)
    if trial_rate < 70:
        insights.append({
            'title': f'试用转化率偏低：{trial_rate}%',
            'detail': '低于70%基准线，需关注渠道质量和产品体验'
        })
        actions.append({
            'priority': 'P0',
            'action': '排查低转化率渠道的转化路径障碍',
            'expected': f'试用率提升至 70%+'
        })
    
    # 洞察3：跟进
    zero_followup_rate = followup.get('zero_followup_rate', 0)
    zero_count = followup.get('zero_followup_count', 0)
    if zero_followup_rate > 30:
        insights.append({
            'title': f'零跟进率过高：{zero_followup_rate}% ({zero_count}家未跟进)',
            'detail': '超过半数商机无任何跟进记录，存在严重销售浪费'
        })
        actions.append({
            'priority': 'P0',
            'action': '建立24小时内首次跟进SOP和提醒机制',
            'expected': f'跟进率从 {followup.get("followup_rate", 0)}% 提升至 70%+'
        })
    
    # 洞察4：数据质量
    phone_rate = quality.get('手机号', 0)
    if phone_rate < 80:
        insights.append({
            'title': f'手机号完整率低：{phone_rate}%',
            'detail': '影响客户触达效率，需在录入环节强制填写'
        })
        actions.append({
            'priority': 'P1',
            'action': '手机号设为必填字段',
            'expected': f'手机号完整率从 {phone_rate}% 提升至 90%+'
        })
    
    need_rate = quality.get('需求', 0)
    if need_rate < 30:
        insights.append({
            'title': f'需求填写率极低：{need_rate}%',
            'detail': '无法进行精准运营分析和个性化跟进'
        })
        actions.append({
            'priority': 'P1',
            'action': '需求字段改为必填，或在跟进时补充',
            'expected': '需求填写率提升至 60%+'
        })
    
    return insights, actions


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python analyze.py <excel_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print(f"正在读取: {file_path}")
    df = load_data(file_path)
    print(f"数据总量: {len(df)} 条")
    
    # 执行各维度分析
    acq = analyze_acquisition(df)
    followup = analyze_followup(df)
    conversion = analyze_conversion(df)
    matrix = analyze_channel_matrix(df)
    quality = analyze_data_quality(df)
    insights, actions = generate_insights(acq, followup, conversion, matrix, quality)
    
    # 汇总结果
    result = {
        'acquisition': acq,
        'followup': followup,
        'conversion': conversion,
        'channel_matrix': matrix,
        'data_quality': quality,
        'insights': insights,
        'actions': actions,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 输出JSON（用于HTML报告生成）
    output_path = os.path.join(os.path.dirname(file_path), 'analysis_result.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析完成！结果已保存到: {output_path}")
    print("\n===== 核心洞察 =====")
    for i, insight in enumerate(insights, 1):
        print(f"{i}. {insight['title']}")
        print(f"   {insight['detail']}")
    
    print("\n===== 优先行动 =====")
    for action in actions:
        print(f"[{action['priority']}] {action['action']}")
        print(f"   预期效果: {action['expected']}")
    
    return result


if __name__ == '__main__':
    main()
