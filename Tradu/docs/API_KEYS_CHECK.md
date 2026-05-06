# 旅渡 APP V1 第二步：API 账号与接口测试准备

## 1. 本步骤目标

本步骤的目标是把旅渡 V1 依赖的外部能力先独立跑通，包括 DeepSeek API 与高德地图 API。只有这些能力验证通过，后续再进入数据库、后端服务和前端页面开发。

本步骤不开发业务系统，只完成账号、Key、环境变量、测试脚本和接口返回样例准备。

---

## 2. 本步骤产出

完成后，项目中应包含以下文件和目录：

```text
.env.example
backend/tests_external/test_amap_poi.py
backend/tests_external/test_amap_geocode.py
backend/tests_external/test_amap_route.py
backend/tests_external/test_amap_weather.py
backend/tests_external/test_deepseek_basic.py
backend/tests_external/test_deepseek_json.py
backend/tests_external/test_deepseek_function_call.py
docs/API_KEYS_CHECK.md
docs/api_samples/
```

其中：

- `.env.example`：环境变量模板，不包含真实 Key；
- `backend/tests_external/`：外部 API 独立测试脚本；
- `docs/api_samples/`：保存真实 API 返回样例；
- `docs/API_KEYS_CHECK.md`：记录账号、Key、测试项和验收结果。

---

## 3. 需要准备的账号与 Key

### 3.1 DeepSeek API

需要准备：

```text
DeepSeek API Key
DeepSeek base_url
DeepSeek model
```

V1 默认配置：

```text
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

DeepSeek 在旅渡中的作用：

1. 解析用户自然语言需求；
2. 将用户输入转成结构化 JSON；
3. 从攻略文本中抽取 POI、标签、推荐时间和避坑信息；
4. 理解用户的路线调整意图；
5. 生成行程解释文本；
6. 后续通过 Function Calling 决定是否调用 POI 搜索、路线规划或天气查询工具。

---

### 3.2 高德地图 API

需要准备：

```text
高德 Web 服务 API Key
高德 JS API Key
高德 JS API 安全密钥 jscode（如控制台启用）
```

高德在旅渡中的作用：

1. POI 关键字搜索；
2. 地理编码；
3. 路线规划；
4. 距离和时间估算；
5. 城市级天气查询；
6. 前端地图展示；
7. 点位 Marker 标注；
8. 路线 Polyline 绘制。

---

## 4. Key 存放规则

### 4.1 后端 Key

以下 Key 只允许放在后端 `.env` 文件中：

```text
DEEPSEEK_API_KEY
AMAP_WEB_SERVICE_KEY
```

原因：

1. DeepSeek API Key 直接关联调用费用；
2. 高德 Web 服务 Key 可调用 POI、路线、天气等服务；
3. 这两类 Key 不应暴露给浏览器端。

---

### 4.2 前端 Key

以下 Key 可在前端使用，但仍需按高德平台要求配置安全策略：

```text
AMAP_JS_API_KEY
AMAP_JS_SECURITY_JSCODE
```

用途：

1. 加载高德 JS 地图；
2. 展示地图容器；
3. 绘制 Marker；
4. 绘制 Polyline；
5. 完成地图交互。

---

### 4.3 Git 提交规则

`.env` 禁止提交。

`.gitignore` 中必须包含：

```text
.env
.env.*
!.env.example
```

`.env.example` 可以提交，因为它只包含变量名，不包含真实 Key。

---

## 5. `.env.example` 内容

项目根目录创建 `.env.example`：

```text
APP_ENV=development
DEFAULT_CITY=重庆
DEFAULT_CITY_ADCODE=500000
HTTP_TIMEOUT_SECONDS=10

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

AMAP_WEB_SERVICE_KEY=
AMAP_JS_API_KEY=
AMAP_JS_SECURITY_JSCODE=
```

本地开发时复制为 `.env`：

```bash
cp .env.example .env
```

然后手动填入真实 Key。

---

## 6. Python 依赖准备

在后端虚拟环境中安装：

```bash
pip install python-dotenv requests openai
```

后续正式后端开发时，还会加入：

```bash
pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy alembic httpx pytest loguru
```

但第二步只需要先安装：

```bash
pip install python-dotenv requests openai
```

---

## 7. 高德接口测试清单

### 7.1 POI 搜索测试

测试脚本：

```text
backend/tests_external/test_amap_poi.py
```

测试目标：

```text
输入：重庆 + 洪崖洞
接口：/v3/place/text
期望：返回 status=1，pois 非空，且结果中包含洪崖洞相关 POI
样例保存：docs/api_samples/amap_poi_hongyadong.json
```

通过标准：

1. 接口返回 HTTP 200；
2. JSON 中 `status` 为 `1`；
3. `pois` 数组非空；
4. 至少一个 POI 名称与“洪崖洞”相关。

---

### 7.2 地理编码测试

测试脚本：

```text
backend/tests_external/test_amap_geocode.py
```

测试目标：

```text
输入：重庆解放碑
接口：/v3/geocode/geo
期望：返回解放碑相关经纬度
样例保存：docs/api_samples/amap_geocode_jiefangbei.json
```

通过标准：

1. 接口返回 HTTP 200；
2. JSON 中 `status` 为 `1`；
3. `geocodes` 数组非空；
4. 结果中存在 `location` 字段。

---

### 7.3 路径规划测试

测试脚本：

```text
backend/tests_external/test_amap_route.py
```

测试目标：

```text
输入：解放碑经纬度 -> 洪崖洞经纬度
接口：/v3/direction/walking
期望：返回步行路线、距离和预计时间
样例保存：docs/api_samples/amap_route_walking_jiefangbei_to_hongyadong.json
```

通过标准：

1. 接口返回 HTTP 200；
2. JSON 中 `status` 为 `1`；
3. `route.paths` 非空；
4. 结果中存在距离或耗时字段。

---

### 7.4 天气查询测试

测试脚本：

```text
backend/tests_external/test_amap_weather.py
```

测试目标：

```text
输入：重庆 adcode=500000
接口：/v3/weather/weatherInfo
期望：返回重庆当前或未来天气
样例保存：docs/api_samples/amap_weather_chongqing.json
```

通过标准：

1. 接口返回 HTTP 200；
2. JSON 中 `status` 为 `1`；
3. `forecasts` 或 `lives` 字段非空；
4. 结果可用于判断晴雨、温度和风力。

---

## 8. DeepSeek 接口测试清单

### 8.1 基础对话测试

测试脚本：

```text
backend/tests_external/test_deepseek_basic.py
```

测试目标：

```text
确认 API Key、base_url、model 能正常调用。
```

通过标准：

1. 接口返回正常；
2. 模型返回非空文本；
3. 不出现鉴权错误、额度错误或连接错误。

---

### 8.2 JSON Output 测试

测试脚本：

```text
backend/tests_external/test_deepseek_json.py
```

测试目标：

```text
输入自然语言旅行需求，要求模型输出合法 JSON。
```

测试输入：

```text
我想去重庆玩3天，预算2500，喜欢美食和拍照，不想太累。
```

期望输出字段：

```json
{
  "destination": "重庆",
  "days": 3,
  "budget": 2500,
  "preferences": ["美食", "拍照"],
  "avoid": ["高强度路线"],
  "travel_style": "relaxed"
}
```

通过标准：

1. 返回内容可以被 `json.loads()` 成功解析；
2. 必须包含 `destination`、`days`、`budget`、`preferences` 字段；
3. `destination` 应为“重庆”；
4. `days` 应为整数 3。

---

### 8.3 Function Calling 测试

测试脚本：

```text
backend/tests_external/test_deepseek_function_call.py
```

测试目标：

```text
确认模型可以根据用户问题生成工具调用参数。
```

测试输入：

```text
帮我查一下重庆洪崖洞这个 POI。
```

期望：

模型返回对 `search_poi` 工具的调用请求，参数包含：

```json
{
  "city": "重庆",
  "keyword": "洪崖洞"
}
```

通过标准：

1. 返回 `tool_calls`；
2. 工具名称为 `search_poi`；
3. 参数中包含 `city` 和 `keyword`；
4. 参数可以被解析成合法 JSON。

---

## 9. API 返回样例保存规范

所有真实 API 返回结果保存在：

```text
docs/api_samples/
```

命名规则：

```text
amap_poi_hongyadong.json
amap_geocode_jiefangbei.json
amap_route_walking_jiefangbei_to_hongyadong.json
amap_weather_chongqing.json
deepseek_intent_parse_sample.json
deepseek_function_call_sample.json
```

用途：

1. 后续写 Pydantic Schema 时参考字段；
2. 后续写解析函数时做单元测试；
3. 便于排查 API 返回结构变化；
4. 便于前端 mock 数据。

---

## 10. 本步骤执行顺序

推荐顺序：

```text
1. 注册并登录高德开放平台
2. 创建高德应用
3. 获取 Web 服务 API Key
4. 获取 JS API Key
5. 注册并登录 DeepSeek 开放平台
6. 获取 DeepSeek API Key
7. 创建 .env.example
8. 复制 .env.example 为 .env
9. 填入真实 Key
10. 安装测试依赖
11. 运行高德 POI 测试
12. 运行高德地理编码测试
13. 运行高德路线规划测试
14. 运行高德天气测试
15. 运行 DeepSeek 基础调用测试
16. 运行 DeepSeek JSON Output 测试
17. 运行 DeepSeek Function Calling 测试
18. 保存所有 API 样例
19. 记录测试结果
```

---

## 11. 运行命令

在项目根目录执行：

```bash
cp .env.example .env
pip install python-dotenv requests openai
```

填好 `.env` 后依次运行：

```bash
python backend/tests_external/test_amap_poi.py
python backend/tests_external/test_amap_geocode.py
python backend/tests_external/test_amap_route.py
python backend/tests_external/test_amap_weather.py
python backend/tests_external/test_deepseek_basic.py
python backend/tests_external/test_deepseek_json.py
python backend/tests_external/test_deepseek_function_call.py
```

---

## 12. 本步骤完成标准

第二步完成时，必须满足：

1. `.env.example` 已创建；
2. `.env` 已在本地创建并填入真实 Key；
3. 高德 POI 搜索测试通过；
4. 高德地理编码测试通过；
5. 高德路线规划测试通过；
6. 高德天气查询测试通过；
7. DeepSeek 基础调用测试通过；
8. DeepSeek JSON Output 测试通过；
9. DeepSeek Function Calling 测试通过；
10. `docs/api_samples/` 中已保存返回样例；
11. Key 未出现在 GitHub 仓库中；
12. 所有测试脚本可以独立运行。

只有完成第二步，才进入第三步：重庆 POI 种子数据集准备。
