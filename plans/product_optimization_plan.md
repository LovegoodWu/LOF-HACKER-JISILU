# LOF 套利监控工具 - 产品优化方案

## 一、当前功能概述

### 1.1 已有能力
- ✅ 从集思录网站获取 LOF 套利数据
- ✅ 支持 Cookie 持久化登录
- ✅ 基础筛选功能（溢价率 > 0.5% 且 申购状态=限额）
- ✅ 邮件通知功能
- ✅ 定时任务（固定每天 13:00 运行）

### 1.2 技术架构
```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│                    (入口协调器)                              │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│   scraper/     │ │    filter/     │ │   notifier/    │ │  scheduler/    │
│   jisilu.py    │ │arbitrage_filter│ │email_notifier  │ │ daily_job.py   │
└────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   集思录 API                                │
│  https://www.jisilu.cn/data/lof/arb_list/                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、优化需求详细设计

### 2.1 灵活的定时任务配置（Cron 表达式）

#### 需求描述
用户希望通过 Cron 表达式自由配置任务执行时间，支持：
- 一天一次（如 `0 13 * * *` - 每天 13:00）
- 一天多次（如 `0 9,13,15 * * *` - 每天 9:00、13:00、15:00）
- 工作日执行（如 `0 13 * * 1-5` - 工作日 13:00）
- 自定义间隔（如 `*/30 9-15 * * *` - 交易时段每 30 分钟）

#### 技术方案

**配置文件设计（.env）**
```ini
# Cron 表达式配置
# 格式：分钟 小时 日 月 星期
SCHEDULE_CRON=0 13 * * *

# 时区配置
SCHEDULE_TIMEZONE=Asia/Shanghai
```

**实现方案**
```python
# 使用 croniter 库解析 Cron 表达式
from croniter import croniter
from datetime import datetime
import pytz

class CronScheduler:
    def __init__(self, cron_expr: str, timezone: str = "Asia/Shanghai"):
        self.cron = croniter(cron_expr)
        self.tz = pytz.timezone(timezone)
    
    def get_next_run_time(self) -> datetime:
        """获取下次执行时间"""
        now = datetime.now(self.tz)
        return self.cron.get_next(datetime)
    
    def is_time_to_run(self, current_time: datetime) -> bool:
        """检查是否应该执行"""
        # 实现逻辑
        pass
```

**Cron 表达式示例**
| 表达式 | 含义 | 适用场景 |
|--------|------|----------|
| `0 13 * * *` | 每天 13:00 | 午间收盘后检查 |
| `0 9,13,15 * * *` | 每天 9:00、13:00、15:00 | 开盘、午间、收盘检查 |
| `*/30 9-15 * * 1-5` | 交易日 9:00-15:00 每 30 分钟 | 高频监控 |
| `0 13 * * 1-5` | 工作日 13:00 | 仅工作日检查 |
| `5 9,10,11,13,14,15 * * *` | 整点后 5 分执行 | 避开开盘波动 |

---

### 2.2 可配置的筛选条件

#### 需求描述
用户希望自定义筛选条件，包括：
- 溢价率阈值（如 > 0.5%、> 1%、> 2%）
- 申购状态（限额、暂停申购、开放申购等）
- 基金类型（QDII、股票型、债券型等）
- 成交额阈值（避免流动性不足）
- 溢价率 + 折价率组合条件

#### 技术方案

**配置文件设计（.env）**
```ini
# 筛选条件配置
# 溢价率阈值（%）
FILTER_PREMIUM_THRESHOLD=0.5

# 申购状态（支持多个，逗号分隔）
# 可选值：限额，暂停申购，开放申购，限 10，限 100 万，etc.
FILTER_SUBSCRIPTION_STATUS=限额，限 10，限 100 万

# 最小成交额（万元）- 避免流动性不足
FILTER_MIN_VOLUME=100

# 基金类型过滤
# QDII: Y/N, T0: Y/N
FILTER_QDII_ONLY=false
FILTER_T0_ONLY=false

# 溢价率上限（%）- 避免异常值
FILTER_PREMIUM_MAX=50
```

**筛选器类设计**
```python
@dataclass
class FilterConfig:
    """筛选配置"""
    premium_threshold: float = 0.5      # 溢价率下限
    premium_max: float = 50.0           # 溢价率上限
    subscription_status: list[str] = None  # 申购状态列表
    min_volume: float = 100.0           # 最小成交额（万）
    qdii_only: bool = False             # 仅 QDII
    t0_only: bool = False               # 仅 T0
    
    def __post_init__(self):
        if self.subscription_status is None:
            self.subscription_status = ["限额"]

class AdvancedArbitrageFilter:
    """高级套利过滤器"""
    
    def __init__(self, config: FilterConfig):
        self.config = config
    
    def filter(self, lof_data: list[dict]) -> list[dict]:
        """应用所有筛选条件"""
        result = []
        for fund in lof_data:
            if self._check_premium(fund) and \
               self._check_subscription_status(fund) and \
               self._check_volume(fund) and \
               self._check_fund_type(fund):
                result.append(fund)
        return result
    
    def _check_premium(self, fund: dict) -> bool:
        """检查溢价率条件"""
        premium = fund.get('premium_rate')
        if premium is None:
            return False
        return self.config.premium_threshold < premium <= self.config.premium_max
    
    def _check_subscription_status(self, fund: dict) -> bool:
        """检查申购状态"""
        status = fund.get('subscription_status', '')
        return status in self.config.subscription_status
    
    def _check_volume(self, fund: dict) -> bool:
        """检查成交额"""
        volume = fund.get('volume', 0)
        return volume >= self.config.min_volume
    
    def _check_fund_type(self, fund: dict) -> bool:
        """检查基金类型"""
        if self.config.qdii_only and fund.get('qdii') != 'Y':
            return False
        if self.config.t0_only and fund.get('t0') != 'Y':
            return False
        return True
```

---

### 2.3 可配置的邮件/通知内容字段

#### 需求描述
用户希望自定义通知中显示的字段，例如：
- 必选字段：代码、名称、溢价率、申购状态
- 可选字段：现价、估值、成交额、溢价率、申购费率、赎回费率等

#### 技术方案

**配置文件设计（.env）**
```ini
# 邮件通知字段配置
# 必选字段（始终显示）
NOTIFY_REQUIRED_FIELDS=code,name,premium_rate,subscription_status

# 可选字段（用户自定义）
NOTIFY_OPTIONAL_FIELDS=current_price,estimated_value,volume,apply_fee,redeem_fee

# 字段显示名称映射
NOTIFY_FIELD_LABELS={"code":"代码","name":"名称","premium_rate":"溢价率 (%)"}
```

**字段配置类**
```python
@dataclass
class NotifyFieldConfig:
    """通知字段配置"""
    required: list[str] = None
    optional: list[str] = None
    
    def __post_init__(self):
        if self.required is None:
            self.required = ['code', 'name', 'premium_rate', 'subscription_status']
        if self.optional is None:
            self.optional = []
    
    @property
    def all_fields(self) -> list[str]:
        return self.required + self.optional

class FieldFormatter:
    """字段格式化器"""
    
    # 字段标签映射
    FIELD_LABELS = {
        'code': '代码',
        'name': '名称',
        'premium_rate': '溢价率 (%)',
        'subscription_status': '申购状态',
        'current_price': '现价',
        'estimated_value': '估值',
        'volume': '成交额 (万)',
        'apply_fee': '申购费率',
        'redeem_fee': '赎回费率',
        'nav': '净值',
        'turnover_rate': '换手率 (%)',
    }
    
    def __init__(self, config: NotifyFieldConfig):
        self.config = config
    
    def format_for_email(self, opportunities: list[dict]) -> str:
        """格式化为 HTML 表格"""
        html = self._build_table_header()
        for fund in opportunities:
            html += self._build_table_row(fund)
        html += "</table>"
        return html
    
    def _build_table_header(self) -> str:
        """构建表头"""
        html = '<table border="1" cellpadding="5" cellspacing="0">'
        html += '<tr style="background-color: #f2f2f2;">'
        for field in self.config.all_fields:
            label = self.FIELD_LABELS.get(field, field)
            html += f'<th>{label}</th>'
        html += '</tr>'
        return html
    
    def _build_table_row(self, fund: dict) -> str:
        """构建单行数据"""
        html = '<tr>'
        for field in self.config.all_fields:
            value = fund.get(field, 'N/A')
            # 特殊字段格式化
            if field == 'premium_rate' and isinstance(value, (int, float)):
                value = f'<span style="color: red; font-weight: bold;">{value:.2f}%</span>'
            elif field == 'current_price' and isinstance(value, (int, float)):
                value = f'{value:.3f}'
            html += f'<td>{value}</td>'
        html += '</tr>'
        return html
```

---

### 2.4 飞书通知支持

#### 需求描述
除了邮件通知外，增加飞书机器人 webhook 通知，支持：
- 文本消息
- 卡片消息（更丰富的展示）
- @特定人员

#### 技术方案

**配置文件设计（.env）**
```ini
# 飞书通知配置
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
FEISHU_ENABLED=true
FEISHU_MESSAGE_TYPE=interactive  # text / interactive

# 邮件通知配置（保留）
EMAIL_ENABLED=true
SMTP_SERVER=smtp.126.com
SMTP_PORT=465
```

**飞书通知类**
```python
import requests
import json

class FeishuNotifier:
    """飞书通知器"""
    
    def __init__(self, webhook_url: str, message_type: str = "interactive"):
        self.webhook_url = webhook_url
        self.message_type = message_type
    
    def send_arbitrage_alert(self, opportunities: list[dict], count: int) -> bool:
        """发送套利提醒"""
        if self.message_type == "interactive":
            message = self._build_interactive_message(opportunities, count)
        else:
            message = self._build_text_message(opportunities, count)
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.webhook_url, json=message, headers=headers)
        return response.status_code == 200
    
    def _build_text_message(self, opportunities: list[dict], count: int) -> dict:
        """构建文本消息"""
        text = f"🔔 LOF 套利提醒 - 发现 {count} 个机会\n\n"
        for fund in opportunities[:10]:  # 最多显示 10 条
            text += f"{fund['name']}({fund['code']}): "
            text += f"溢价率 {fund['premium_rate']:.2f}%, "
            text += f"申购状态：{fund['subscription_status']}\n"
        
        if len(opportunities) > 10:
            text += f"\n... 还有 {len(opportunities) - 10} 条，请查看详情"
        
        return {
            "msg_type": "text",
            "content": {"text": text}
        }
    
    def _build_interactive_message(self, opportunities: list[dict], count: int) -> dict:
        """构建卡片消息"""
        elements = []
        
        # 标题
        elements.append({
            "tag": "div",
            "text": {
                "content": f"**🔔 LOF 套利提醒 - 发现 {count} 个机会**",
                "tag": "lark_md"
            }
        })
        
        # 基金列表（最多 5 条）
        for fund in opportunities[:5]:
            elements.append({
                "tag": "div",
                "text": {
                    "content": f"**{fund['name']}**({fund['code']})\n"
                              f"溢价率：{fund['premium_rate']:.2f}% | "
                              f"申购状态：{fund['subscription_status']}",
                    "tag": "lark_md"
                }
            })
        
        if len(opportunities) > 5:
            elements.append({
                "tag": "div",
                "text": {
                    "content": f"... 还有 {len(opportunities) - 5} 条机会",
                    "tag": "lark_md"
                }
            })
        
        return {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "template": "red",
                    "title": {"content": "LOF 套利提醒", "tag": "plain_text"}
                },
                "elements": elements
            }
        }
```

---

### 2.5 其他优化建议

#### 2.5.1 多通知渠道支持
```python
# 通知策略模式
class NotificationStrategy:
    """通知策略接口"""
    def send(self, message: dict) -> bool:
        pass

class EmailNotification(NotificationStrategy):
    pass

class FeishuNotification(NotificationStrategy):
    pass

class WechatNotification(NotificationStrategy):
    """企业微信通知（未来扩展）"""
    pass

class NotificationManager:
    """通知管理器"""
    def __init__(self):
        self.strategies: list[NotificationStrategy] = []
    
    def add_strategy(self, strategy: NotificationStrategy):
        self.strategies.append(strategy)
    
    def notify_all(self, message: dict):
        """通过所有渠道发送"""
        for strategy in self.strategies:
            try:
                strategy.send(message)
            except Exception as e:
                logger.error(f"Notification failed: {e}")
```

#### 2.5.2 数据持久化与历史对比
```python
# 记录历史数据，用于趋势分析
class DataPersistence:
    """数据持久化"""
    
    def __init__(self, db_path: str = "data/lof_history.db"):
        self.db_path = db_path
    
    def save_snapshot(self, data: list[dict], timestamp: datetime):
        """保存数据快照"""
        pass
    
    def get_premium_history(self, fund_code: str, days: int = 7) -> list[dict]:
        """获取某基金的历史溢价率"""
        pass
    
    def detect_anomaly(self, fund_code: str, threshold: float = 2.0) -> bool:
        """检测溢价率异常（超过历史均值 2 个标准差）"""
        pass
```

#### 2.5.3 黑白名单机制
```ini
# 黑名单 - 永不提醒的基金
FILTER_BLACKLIST=160123,160125,160127

# 白名单 - 优先提醒的基金
FILTER_WHITELIST=161128,501225

# 溢价率异常阈值（超过此值发送紧急提醒）
ALERT_URGENT_THRESHOLD=5.0
```

#### 2.5.4 健康检查与告警
```python
class HealthCheck:
    """健康检查"""
    
    def check_scraper(self) -> bool:
        """检查数据抓取是否正常"""
        pass
    
    def check_login_status(self) -> bool:
        """检查登录状态"""
        pass
    
    def send_health_report(self) -> bool:
        """发送健康报告（如每周运行统计）"""
        pass
```

#### 2.5.5 Web 管理界面（远期规划）
```
功能：
- 可视化配置筛选条件
- 实时查看监控状态
- 历史数据图表展示
- 手动触发检查
- 通知记录查看

技术栈：
- Flask/FastAPI 后端
- Vue/React 前端
- SQLite 数据库
```

---

## 三、配置示例

### 3.1 保守型配置（低频监控）
```ini
# 定时任务 - 每天 13:00 执行一次
SCHEDULE_CRON=0 13 * * *

# 筛选条件 - 只关注高溢价
FILTER_PREMIUM_THRESHOLD=2.0
FILTER_SUBSCRIPTION_STATUS=限额
FILTER_MIN_VOLUME=500

# 通知字段
NOTIFY_REQUIRED_FIELDS=code,name,premium_rate,subscription_status
NOTIFY_OPTIONAL_FIELDS=volume

# 通知渠道
EMAIL_ENABLED=true
FEISHU_ENABLED=false
```

### 3.2 激进型配置（高频监控）
```ini
# 定时任务 - 交易时段每 15 分钟执行
SCHEDULE_CRON=*/15 9-15 * * 1-5

# 筛选条件 - 宽松筛选
FILTER_PREMIUM_THRESHOLD=0.3
FILTER_SUBSCRIPTION_STATUS=限额，限 10，限 100 万
FILTER_MIN_VOLUME=50
FILTER_QDII_ONLY=true

# 通知字段 - 详细信息
NOTIFY_REQUIRED_FIELDS=code,name,premium_rate,subscription_status
NOTIFY_OPTIONAL_FIELDS=current_price,estimated_value,volume,apply_fee,redeem_fee,turnover_rate

# 通知渠道 - 双渠道
EMAIL_ENABLED=true
FEISHU_ENABLED=true
FEISHU_MESSAGE_TYPE=interactive
```

### 3.3 白名单配置（只关注特定基金）
```ini
# 定时任务
SCHEDULE_CRON=0 10,13,15 * * *

# 白名单模式
FILTER_WHITELIST=161128,501225,164906
FILTER_WHITELIST_ONLY=true

# 通知
FEISHU_ENABLED=true
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
```

---

## 四、项目结构规划

```
LOFHacker/
├── config/
│   ├── __init__.py
│   ├── settings.py          # 配置管理（支持热重载）
│   └── cron_parser.py       # Cron 表达式解析
│
├── scraper/
│   ├── __init__.py
│   ├── jisilu.py            # 集思录爬虫
│   └── data_validator.py    # 数据验证
│
├── filter/
│   ├── __init__.py
│   ├── arbitrage_filter.py  # 基础过滤器
│   ├── advanced_filter.py   # 高级过滤器
│   └── filter_config.py     # 筛选配置
│
├── notifier/
│   ├── __init__.py
│   ├── base_notifier.py     # 通知基类
│   ├── email_notifier.py    # 邮件通知
│   ├── feishu_notifier.py   # 飞书通知
│   └── notification_manager.py  # 通知管理器
│
├── formatter/
│   ├── __init__.py
│   ├── field_formatter.py   # 字段格式化
│   └── message_builder.py   # 消息构建器
│
├── scheduler/
│   ├── __init__.py
│   ├── cron_scheduler.py    # Cron 调度器
│   └── task_runner.py       # 任务执行器
│
├── storage/
│   ├── __init__.py
│   ├── data_persistence.py  # 数据持久化
│   └── history_analyzer.py  # 历史分析
│
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── health_check.py      # 健康检查
│
├── tools/
│   ├── test_cookies.py
│   ├── import_cookies.py
│   └── config_validator.py  # 配置验证工具
│
├── main.py                   # 主入口
├── requirements.txt
├── .env.example              # 配置模板
└── README.md
```

---

## 五、实施优先级

### Phase 1 - 核心功能（1-2 周）
1. ✅ Cron 表达式调度器
2. ✅ 可配置筛选条件
3. ✅ 可配置通知字段
4. ✅ 飞书通知支持

### Phase 2 - 增强功能（2-3 周）
1. 黑白名单机制
2. 多通知渠道管理
3. 健康检查与报告
4. 配置验证工具

### Phase 3 - 高级功能（4-6 周）
1. 数据持久化
2. 历史数据分析
3. 溢价率异常检测
4. Web 管理界面原型

---

## 六、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 集思录 API 变更 | 高 | 添加 API 版本检测，快速适配 |
| Cookie 过期 | 中 | 添加自动登录重试，过期告警 |
| 飞书 webhook 限流 | 低 | 添加请求频率控制 |
| 配置错误导致误报 | 中 | 添加配置验证工具 |
| 高频请求被封禁 | 高 | 添加请求间隔，使用代理 |

---

## 七、总结

本优化方案旨在将 LOF 套利监控工具从单一功能的脚本升级为可配置、可扩展的监控平台。核心改进包括：

1. **灵活性**：Cron 表达式支持任意时间配置
2. **可定制**：筛选条件和通知字段完全可配置
3. **多渠道**：邮件 + 飞书双通知，未来可扩展企业微信等
4. **可扩展**：模块化设计便于添加新功能

通过分阶段实施，可以快速上线核心功能，同时为未来的高级功能预留扩展空间。
