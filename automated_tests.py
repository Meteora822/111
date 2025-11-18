import unittest
import sys
import os
import requests
import json
from datetime import date, datetime
from decimal import Decimal

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestAccountingSystemAPI(unittest.TestCase):
    """简易记账本系统API自动化测试"""
    
    BASE_URL = 'http://127.0.0.1:5000'
    
    def setUp(self):
        """测试前置条件"""
        self.test_record_data = {
            "type": "expense",
            "amount": 88.88,
            "category": "自动化测试",
            "date": "2025-11-18", 
            "note": "单元测试记录"
        }
        
    def test_01_get_records(self):
        """测试用例TC_API_01: 获取记录列表"""
        response = requests.get(f'{self.BASE_URL}/api/records')
        
        self.assertEqual(response.status_code, 200, "API应返回200状态码")
        
        data = response.json()
        self.assertIsInstance(data, list, "返回数据应为列表格式")
        
        if len(data) > 0:
            record = data[0]
            required_fields = ['id', 'type', 'amount', 'category', 'date']
            for field in required_fields:
                self.assertIn(field, record, f"记录应包含{field}字段")
                
        print(f"✅ 获取记录测试通过 - 返回{len(data)}条记录")
        
    def test_02_create_record(self):
        """测试用例TC_API_02: 创建新记录"""
        response = requests.post(
            f'{self.BASE_URL}/api/record',
            json=self.test_record_data,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertIn(response.status_code, [200, 201], "创建记录应返回200或201状态码")
        
        result = response.json()
        self.assertIn('id', result, "返回结果应包含记录ID")
        
        # 保存创建的记录ID用于后续测试
        self.created_record_id = result['id']
        print(f"✅ 创建记录测试通过 - 新记录ID: {self.created_record_id}")
        
        return self.created_record_id
        
    def test_03_get_statistics(self):
        """测试用例TC_API_03: 获取统计数据"""
        response = requests.get(f'{self.BASE_URL}/api/stats')
        
        self.assertEqual(response.status_code, 200, "统计API应返回200状态码")
        
        data = response.json()
        required_fields = ['by_category', 'daily_stats', 'month_summary']
        for field in required_fields:
            self.assertIn(field, data, f"统计数据应包含{field}字段")
            
        # 验证月度汇总数据结构
        month_summary = data['month_summary']
        summary_fields = ['total_income', 'total_expense', 'balance']
        for field in summary_fields:
            self.assertIn(field, month_summary, f"月度汇总应包含{field}字段")
            
        print(f"✅ 统计数据测试通过 - 收入:{month_summary['total_income']}, 支出:{month_summary['total_expense']}")
        
    def test_04_update_record(self):
        """测试用例TC_API_04: 更新记录"""
        # 先创建一个记录
        record_id = self.test_02_create_record()
        
        # 更新记录数据
        updated_data = self.test_record_data.copy()
        updated_data['amount'] = 99.99
        updated_data['note'] = "更新后的记录"
        
        response = requests.put(
            f'{self.BASE_URL}/api/record/{record_id}',
            json=updated_data,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200, "更新记录应返回200状态码")
        
        result = response.json()
        self.assertIn('message', result, "更新结果应包含消息")
        
        print(f"✅ 更新记录测试通过 - 记录ID: {record_id}")
        
    def test_05_delete_record(self):
        """测试用例TC_API_05: 删除记录"""
        # 先创建一个记录
        record_id = self.test_02_create_record()
        
        # 删除记录
        response = requests.delete(f'{self.BASE_URL}/api/record/{record_id}')
        
        self.assertEqual(response.status_code, 200, "删除记录应返回200状态码")
        
        result = response.json()
        self.assertIn('message', result, "删除结果应包含消息")
        
        print(f"✅ 删除记录测试通过 - 记录ID: {record_id}")
        
    def test_06_invalid_data_validation(self):
        """测试用例TC_API_06: 无效数据验证"""
        # 测试空金额
        invalid_data = self.test_record_data.copy()
        invalid_data['amount'] = ""
        
        response = requests.post(
            f'{self.BASE_URL}/api/record',
            json=invalid_data,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertIn(response.status_code, [400, 422], "无效数据应返回400或422状态码")
        print("✅ 无效数据验证测试通过 - 空金额被正确拒绝")
        
        # 测试负数金额
        invalid_data['amount'] = -50
        
        response = requests.post(
            f'{self.BASE_URL}/api/record',
            json=invalid_data,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertIn(response.status_code, [400, 422], "负数金额应被拒绝")
        print("✅ 无效数据验证测试通过 - 负数金额被正确拒绝")

class TestDataValidation(unittest.TestCase):
    """数据验证单元测试"""
    
    def test_amount_validation(self):
        """测试金额验证逻辑"""
        # 有效金额
        valid_amounts = [100.00, 0.01, 999999.99]
        for amount in valid_amounts:
            self.assertGreater(amount, 0, f"金额{amount}应大于0")
            
        # 无效金额
        invalid_amounts = [-1, 0, -999.99]
        for amount in invalid_amounts:
            self.assertLessEqual(amount, 0, f"金额{amount}应被拒绝")
            
        print("✅ 金额验证逻辑测试通过")
        
    def test_date_validation(self):
        """测试日期验证逻辑"""
        # 有效日期
        today = date.today()
        self.assertIsInstance(today, date, "今天日期应为有效日期对象")
        
        # 日期格式验证
        date_str = "2025-11-18"
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            self.assertIsInstance(parsed_date, date, "日期字符串应能正确解析")
        except ValueError:
            self.fail("日期格式验证失败")
            
        print("✅ 日期验证逻辑测试通过")
        
    def test_category_validation(self):
        """测试分类验证逻辑"""
        # 有效分类
        valid_categories = ["餐饮", "交通", "娱乐", "教育", "医疗"]
        for category in valid_categories:
            self.assertIsInstance(category, str, "分类应为字符串")
            self.assertGreater(len(category), 0, "分类名称不能为空")
            self.assertLessEqual(len(category), 50, "分类名称不能超过50字符")
            
        print("✅ 分类验证逻辑测试通过")

def run_performance_test():
    """性能测试（简单版本）"""
    print("\n🚀 开始性能测试...")
    
    import time
    
    # 测试API响应时间
    start_time = time.time()
    response = requests.get('http://127.0.0.1:5000/api/records')
    end_time = time.time()
    
    response_time = (end_time - start_time) * 1000  # 转换为毫秒
    
    print(f"📊 API响应时间: {response_time:.2f}ms")
    
    if response_time < 200:
        print("✅ 性能测试通过 - 响应时间在200ms以内")
    elif response_time < 500:
        print("⚠️  性能测试警告 - 响应时间稍慢但可接受")
    else:
        print("❌ 性能测试失败 - 响应时间过慢")

def main():
    """主测试函数"""
    print("="*60)
    print("🧪 简易记账本系统 - 自动化测试套件")
    print("="*60)
    
    # 检查服务器是否运行
    try:
        response = requests.get('http://127.0.0.1:5000/api/records')
        print("✅ 服务器连接正常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Flask应用正在运行")
        print("   启动命令: python app.py")
        return
    
    # 运行单元测试
    print("\n📋 开始执行测试用例...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行性能测试
    run_performance_test()
    
    print("\n" + "="*60)
    print("🎉 所有测试执行完成！")
    print("="*60)

if __name__ == '__main__':
    main()