"""
API 测试脚本
用于验证后端接口是否正常工作
"""
import requests
import json
from datetime import date

BASE_URL = 'http://127.0.0.1:5000'

def test_get_records():
    """测试获取记录列表"""
    print('\n=== 测试：获取记录列表 ===')
    try:
        response = requests.get(f'{BASE_URL}/api/records')
        print(f'状态码: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'记录数: {len(data)}')
            if data:
                print(f'第一条记录: {data[0]}')
            return True
        else:
            print(f'失败: {response.text}')
            return False
    except Exception as e:
        print(f'错误: {e}')
        return False

def test_add_record():
    """测试添加记录"""
    print('\n=== 测试：添加记录 ===')
    try:
        payload = {
            'type': 'expense',
            'amount': 88.88,
            'category': '测试',
            'date': str(date.today()),
            'note': 'API测试记录'
        }
        print(f'发送数据: {payload}')
        response = requests.post(
            f'{BASE_URL}/api/record',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        print(f'状态码: {response.status_code}')
        if response.status_code == 201:
            data = response.json()
            print(f'返回数据: {data}')
            return data.get('id')
        else:
            print(f'失败: {response.text}')
            return None
    except Exception as e:
        print(f'错误: {e}')
        return None

def test_delete_record(record_id):
    """测试删除记录"""
    print(f'\n=== 测试：删除记录 ID={record_id} ===')
    try:
        response = requests.delete(f'{BASE_URL}/api/record/{record_id}')
        print(f'状态码: {response.status_code}')
        if response.status_code == 200:
            print(f'删除成功: {response.json()}')
            return True
        else:
            print(f'失败: {response.text}')
            return False
    except Exception as e:
        print(f'错误: {e}')
        return False

def test_stats():
    """测试统计接口"""
    print('\n=== 测试：获取统计 ===')
    try:
        response = requests.get(f'{BASE_URL}/api/stats')
        print(f'状态码: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'分类统计: {data.get("by_category")}')
            print(f'月度汇总: {data.get("month_summary")}')
            return True
        else:
            print(f'失败: {response.text}')
            return False
    except Exception as e:
        print(f'错误: {e}')
        return False

def main():
    print('=' * 60)
    print('开始 API 测试')
    print('=' * 60)
    
    # 测试获取记录
    if not test_get_records():
        print('\n✗ 获取记录失败，请检查服务是否正常运行')
        return
    
    # 测试添加记录
    new_id = test_add_record()
    if not new_id:
        print('\n✗ 添加记录失败')
    else:
        print(f'\n✓ 添加记录成功，ID={new_id}')
        
        # 再次获取记录，验证是否添加成功
        test_get_records()
        
        # 测试删除记录
        if test_delete_record(new_id):
            print('\n✓ 删除记录成功')
        else:
            print('\n✗ 删除记录失败')
    
    # 测试统计
    if test_stats():
        print('\n✓ 统计接口正常')
    else:
        print('\n✗ 统计接口失败')
    
    print('\n' + '=' * 60)
    print('测试完成')
    print('=' * 60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n测试中断')
    except Exception as e:
        print(f'\n测试异常: {e}')
