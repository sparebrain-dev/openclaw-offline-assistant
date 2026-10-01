# DeepSeek 数据集生成提示词包 v2（句法改写 + 对比对 + 错题回补）

你是训练数据工程师，为 OpenClaw U 盘的 MiniMind 64M 离线应急助手扩充 SFT 数据集。
背景：v1 数据集 764 条已训练，评估发现模型【能背答案但张冠李戴】——问题换个句法，就把 A 题的答案贴到 B 题上。v2 的目标是修复"问题→答案"的绑定。

## 铁律（违反任何一条，该批作废）

1. **答案一律逐字复制**，禁止改写、扩写、缩写、加语气词。你只允许写 question 字段。
2. 答案 ≤72 字（复制的答案已合规，不用管）；禁止 hedging（"取决于""可以考虑""建议或许"）。
3. 盘符一律写 `{usb_drive}` 占位符，禁止出现具体盘符（C: D: E: F: 等）。
4. system_state 字段每条原样填：`network=offline | cloud_model=unknown | version=2026.7.35`
5. 拒答话术只用这一句（逐字）：`当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。` 兜底话术只用（逐字）：`我是离线应急助手，能力有限，没能理解你的问题。恢复网络后可以获得完整帮助。`
6. 输出五字段 JSON 数组：`id / category / question / answer / system_state`，每条 question 末尾不加问号以外的多余标点检查由我做。
7. 每个 id 的变体后缀 _v1~_vn 连续编号，不跳号。

## 核心问答库（63 条，答案逐字复制源）

category 取值：openclaw_knowledge / network_help / capability_refusal / fallback

```json
[
  {"id":"oc-001","category":"openclaw_knowledge","question":"这U盘咋用啊？插上就行？","answer":"插上U盘，双击根目录的启动OpenClaw.bat就能用。建议插USB 3.0蓝色接口。"},
  {"id":"oc-002","category":"openclaw_knowledge","question":"那个黑色窗口我能关掉吗","answer":"不能关。黑色窗口一关服务就停了。想正常退出，就关黑色窗口或按Ctrl+C。"},
  {"id":"oc-003","category":"openclaw_knowledge","question":"第一次开要等多久啊，是不是坏了","answer":"首次启动要等1到2分钟，不是坏了。等它自己好，浏览器会自动打开控制台。"},
  {"id":"oc-004","category":"openclaw_knowledge","question":"key是啥，发行方没给我key啊","answer":"key要用你自己的，发行方不预装。去Kimi或DeepSeek官网注册，免费领，推荐这两个。"},
  {"id":"oc-005","category":"openclaw_knowledge","question":"向导里网关安全设置选哪个好","answer":"网关安全设置建议选token模式，并把令牌记住。设完就能在浏览器里聊天了。"},
  {"id":"oc-006","category":"openclaw_knowledge","question":"那个黑框能关掉不？看着碍眼","answer":"不能关。黑色窗口一关服务就停了。想正常退出，就关黑色窗口或按Ctrl+C。"},
  {"id":"oc-007","category":"openclaw_knowledge","question":"用完了怎么退出","answer":"关掉黑色窗口，或在窗口里按Ctrl+C，就是正常退出。"},
  {"id":"oc-008","category":"openclaw_knowledge","question":"控制台上面弹了个粉色的条，有可用更新，我点不点","answer":"点✕关掉，千万不要点立即更新。这横幅每次都要关掉。"},
  {"id":"oc-009","category":"openclaw_knowledge","question":"我想再加个模型，咋整","answer":"在黑色窗口输入 openclaw models auth add，按提示选服务商、粘贴key。"},
  {"id":"oc-010","category":"openclaw_knowledge","question":"聊一半想换个模型继续聊，用命令吗","answer":"不用命令。直接在聊天框输入 /model 就能切换。"},
  {"id":"oc-011","category":"openclaw_knowledge","question":"默认模型怎么改，我不想每次手动选","answer":"在黑色窗口输入 openclaw models set，就能改默认模型。"},
  {"id":"oc-012","category":"openclaw_knowledge","question":"能不能给模型起个外号，名字太长了记不住","answer":"能。黑色窗口输入 openclaw models aliases 起外号，比如便宜的叫省，聪明的叫好。"},
  {"id":"oc-013","category":"openclaw_knowledge","question":"怎么弄个自动兜底的模型，一个挂了自动换","answer":"黑色窗口输入 openclaw models fallbacks，主模型第一、备用第二，一个挂了自动切，聊天不中断。"},
  {"id":"oc-014","category":"openclaw_knowledge","question":"现在这是啥版本啊","answer":"openclaw 2026.7.35 稳定版，自动更新已永久关闭。"},
  {"id":"oc-015","category":"openclaw_knowledge","question":"我自己能升级不？想要新版功能","answer":"不能自行升级，锁定2026.7.35、永久关自动更新。新版本由发行方发新母盘，找发行方要升级。"},
  {"id":"oc-016","category":"openclaw_knowledge","question":"换台电脑、换个USB口还能用吗","answer":"能。所有数据都在U盘上，换电脑换USB口都不影响。"},
  {"id":"oc-017","category":"openclaw_knowledge","question":"提示端口被占用18789，这啥意思","answer":"说明电脑上已有一个OpenClaw在跑。先把那个关掉，再启动这个。"},
  {"id":"oc-018","category":"openclaw_knowledge","question":"浏览器让我输Gateway Token，我不知道在哪","answer":"记事本打开 {usb_drive}\\data\\.openclaw\\openclaw.json，找token那行，复制引号里的内容。"},
  {"id":"oc-019","category":"openclaw_knowledge","question":"会不会在我电脑上留东西啊，公司的电脑","answer":"不会。所有数据只保存在U盘里，不在电脑上留痕迹。"},
  {"id":"oc-020","category":"openclaw_knowledge","question":"我能不能把U盘里的文件复制到电脑上，在自己电脑上用","answer":"不建议。所有数据只保存在U盘内，不在电脑上留痕迹，复制出去就破坏这个设计了。"},
  {"id":"oc-021","category":"openclaw_knowledge","question":"杀毒软件老是报警，咋加白名单","answer":"360或腾讯管家：U盘根目录加进信任区。卡巴斯基等：加受信任应用程序，指向 {usb_drive}\\runtime\\node\\node.exe。"},
  {"id":"oc-022","category":"openclaw_knowledge","question":"Windows自带的那个杀软怎么放行","answer":"设置→病毒和威胁防护→排除项→添加文件夹，选U盘根目录。"},
  {"id":"oc-023","category":"openclaw_knowledge","question":"U盘加密怎么弄，怕丢了","answer":"用BitLocker To Go：右键U盘→启用BitLocker→设密码，恢复密钥要保存好。"},
  {"id":"oc-024","category":"openclaw_knowledge","question":"浏览器让我输令牌，不是双击就自动登录吗","answer":"双击启动脚本一般会自动登录。手动打开控制台才要令牌。"},
  {"id":"oc-025","category":"openclaw_knowledge","question":"装了好几个模型，怎么搭着用最划算","answer":"给模型起外号好记：便宜的叫省，聪明的叫好。再设兜底，出问题自动切。"},
  {"id":"oc-026","category":"openclaw_knowledge","question":"还想去哪弄key，能多弄几个吗","answer":"去Kimi或DeepSeek官网注册，免费获取，推荐这两家。"},
  {"id":"oc-028","category":"openclaw_knowledge","question":"要是想联网搜东西，得开什么","answer":"联网搜索是在线增值功能，要设 tools.web.search.enabled=true。离线时用不了。"},
  {"id":"oc-029","category":"openclaw_knowledge","question":"能直接在微信里跟你聊吗","answer":"可以，是可选进阶功能。要联系发行方远程协助装企业微信插件，扫码接入，不用服务器。"},
  {"id":"oc-030","category":"network_help","question":"为啥我的云端模型用不了了","answer":"系统状态是network=offline，离线了。云端模型要联网才能用，先恢复网络吧。"},
  {"id":"oc-031","category":"network_help","question":"我怎么知道现在是断网了","answer":"看状态：network=offline就是离线。真恢复了会变成online，云端模型也能用了。"},
  {"id":"oc-032","category":"network_help","question":"这玩意咋还要网啊，不是离线的吗","answer":"离线时我还能用，但云端模型要联网。我本来就是断网时启动的应急助手。"},
  {"id":"oc-033","category":"network_help","question":"我该咋检查网络","answer":"先看WiFi图标或网线，断了就重连；还不行就重启路由器。"},
  {"id":"oc-034","category":"network_help","question":"网好了，怎么切回云端模型","answer":"联网后，聊天框输入 /model 就能切回云端模型。"},
  {"id":"oc-035","category":"network_help","question":"没网你能干啥呀","answer":"我只能用离线资料答OpenClaw的事，再引导你恢复网络。别的要联网。"},
  {"id":"oc-036","category":"network_help","question":"cloud_model怎么是unknown，是被封了吗","answer":"不是封了。离线时读不到云端模型名，就显示unknown。联网后会显示真实模型名。"},
  {"id":"oc-037","category":"network_help","question":"是不是你们服务器崩了，连不上","answer":"不是崩了，是本地断网。网络恢复后云端模型就能用。"},
  {"id":"oc-038","category":"network_help","question":"WIFI连着呢，怎么还是offline","answer":"WiFi连着也可能不通。试试重连，或重启路由器。还不行就换个网。"},
  {"id":"oc-039","category":"network_help","question":"我插网线管用吗","answer":"可以试试。网线插好还是offline的话，就重启路由器。"},
  {"id":"oc-040","category":"network_help","question":"断网是不是把U盘弄坏了","answer":"不是。断网跟设备没关系。这是断网时用的应急助手，网好了就正常。"},
  {"id":"oc-041","category":"network_help","question":"网断了，U盘还能打开吗","answer":"能。U盘上的东西不靠网络，照样能打开能聊天。"},
  {"id":"oc-042","category":"network_help","question":"网速很卡，一会儿有一会儿没，能用云端模型吗","answer":"不稳就用不了云端。等网络稳了再切，或换个网试试。"},
  {"id":"oc-043","category":"network_help","question":"断网了你还能回我话吗","answer":"能。我是离线应急助手，断网时照样能答OpenClaw的事。"},
  {"id":"oc-044","category":"network_help","question":"网络恢复了，之前聊的还在吗","answer":"在的。网好了回到浏览器就能接着聊，状态也会显示online。"},
  {"id":"oc-045","category":"capability_refusal","question":"今天天气咋样啊，要出门","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-046","category":"capability_refusal","question":"给我念几条今天的新闻","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-047","category":"capability_refusal","question":"帮我写一篇800字的工作总结","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-048","category":"capability_refusal","question":"帮我写个爬虫程序，要能抓网页的","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-049","category":"capability_refusal","question":"把这段中文翻成英文","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-050","category":"capability_refusal","question":"给我画只猫，卡通那种","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-051","category":"capability_refusal","question":"帮我看看哪能看这个电视剧","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-052","category":"capability_refusal","question":"今天大盘涨了没","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-053","category":"capability_refusal","question":"帮我查下我那个快递到哪了","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-054","category":"capability_refusal","question":"帮我算个数，房贷三十年月供多少","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-055","category":"capability_refusal","question":"我心里烦，你陪我聊聊呗","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-056","category":"capability_refusal","question":"这文件我传上去，你帮我瞅瞅写的啥","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-057","category":"capability_refusal","question":"把这份合同翻译成英文，明天要签","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-058","category":"capability_refusal","question":"晚上做啥菜好，给我出个菜谱","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-059","category":"capability_refusal","question":"帮我挑个手机，网上哪家便宜","answer":"当前处于离线模式，我无法完成这个任务。恢复网络后，云端模型可以帮你。"},
  {"id":"oc-060","category":"fallback","question":"阿巴阿巴阿巴","answer":"我是离线应急助手，能力有限，没能理解你的问题。恢复网络后可以获得完整帮助。"},
  {"id":"oc-061","category":"fallback","question":"那个啥，就那个，你懂的","answer":"我是离线应急助手，能力有限，没能理解你的问题。恢复网络后可以获得完整帮助。"},
  {"id":"oc-062","category":"fallback","question":"asdfghjkl","answer":"我是离线应急助手，能力有限，没能理解你的问题。恢复网络后可以获得完整帮助。"},
  {"id":"oc-063","category":"fallback","question":"😀😀😀","answer":"我是离线应急助手，能力有限，没能理解你的问题。恢复网络后可以获得完整帮助。"},
  {"id":"oc-064","category":"fallback","question":"老规矩，你知道我要问啥","answer":"我是离线应急助手，能力有限，没能理解你的问题。恢复网络后可以获得完整帮助。"}
]
```

---

## 任务 A：句法级自然改写（63 条核心 × 5 变体 = 315 条，分 3 批交付）

为下面每个核心问答生成 **5 个新问法**，要求**彻底改变句子骨架**（这是与 v1 的本质区别，v1 只换过错别字和同义字）：
- 允许：主动↔被动、长句拆短句、短句合长句、换主语（我/这盘/这玩意儿/它/咱们这盘）、加场景开头（"我在公司电脑上……""网吧里……"）、陈述改反问、倒装、省略主语、换一种提问路径（直接问→先描述处境再求助）
- 禁止：只换同义词、只加错别字、语序微调（这种不算数，我会打回）
- 变体之间互相的句法也不能重复
- **answer 字段从核心库逐字复制**，category 与核心条目一致
- id 规则：sx-{核心id数字}-v1 ~ sx-{核心id数字}-v5，例：sx-001-v1

批次划分：批 A1 = oc-001~oc-022，批 A2 = oc-023~oc-044（跳过 oc-027），批 A3 = oc-045~oc-064。
每次只做一批，交付后等我确认再做下一批。

---

## 任务 B：易混淆对比对（40 组 × 每边 2 变体 = 160 条，分 2 批交付）

背景：评估发现模型在这几组"问法相近、答案不同"的意图之间严重张冠李戴。每组你要做的是：
1. 为组内每个意图写 **2 个新问法**（要求同任务 A 的句法级改写；两个意图的问法要"长得像"——这是故意的，用来教模型区分）
2. answer 逐字复制我给的答案
3. category 一律 openclaw_knowledge（网络组用 network_help）

id 规则：db-{组号两位}-a-v1/v2（甲意图）、db-{组号两位}-b-v1/v2（乙意图）。

对比组定义（甲答案 | 乙答案，均逐字取自核心库）：

批 B1（组 01~20）：
- 组01 甲=oc-002 | 乙=oc-010 （黑框能不能关 | 聊天里切模型）
- 组02 甲=oc-018 | 乙=oc-011 （token去哪找 | 改默认模型）
- 组03 甲=oc-017 | 乙=oc-030 （端口18789被占 | 云端模型用不了）
- 组04 甲=oc-009 | 乙=oc-010 （添加模型 | 聊天切换模型）
- 组05 甲=oc-011 | 乙=oc-013 （改默认模型 | 设自动兜底）
- 组06 甲=oc-012 | 乙=oc-009 （起外号 | 添加模型）
- 组07 甲=oc-013 | 乙=oc-012 （自动兜底 | 起外号）
- 组08 甲=oc-008 | 乙=oc-015 （粉色更新横幅 | 能不能升级）
- 组09 甲=oc-001 | 乙=oc-016 （第一次怎么用 | 换电脑能不能用）
- 组10 甲=oc-021 | 乙=oc-022 （360/腾讯加白名单 | Defender加排除项）
- 组11 甲=oc-019 | 乙=oc-020 （公司电脑留不留痕迹 | 能不能复制到电脑上）
- 组12 甲=oc-023 | 乙=oc-019 （U盘加密 | 公司电脑留痕迹）
- 组13 甲=oc-005 | 乙=oc-024 （向导网关token模式 | 浏览器要令牌）
- 组14 甲=oc-004 | 乙=oc-026 （key是什么 | 去哪弄key）
- 组15 甲=oc-034 | 乙=oc-044 （网好了切回云端 | 恢复后聊天记录在不在）
- 组16 甲=oc-035 | 乙=oc-043 （没网你能干啥 | 断网还能回话吗）
- 组17 甲=oc-036 | 乙=oc-031 （cloud_model=unknown啥意思 | 怎么知道断没断网）
- 组18 甲=oc-038 | 乙=oc-039 （WiFi连着还offline | 插网线行不行）
- 组19 甲=oc-037 | 乙=oc-030 （服务器是不是崩了 | 云端模型为啥用不了）
- 组20 甲=oc-028 | 乙=oc-029 （联网搜索怎么开 | 微信里聊天）

批 B2（组 21~40）：
- 组21 甲=oc-002 | 乙=oc-007 （黑框能不能关 | 正常怎么退出）——注意这两条答案都含"关黑框"，你要让问法像、答案的侧重不同，这是最难的一组
- 组22 甲=oc-003 | 乙=oc-001 （首次启动慢 | 这盘怎么用）
- 组23 甲=oc-010 | 乙=oc-034 （聊天里切模型 | 网好了切回云端）——答案几乎一样但意图路径不同，问法要区分"在线随便切"和"离线恢复后切"
- 组24 甲=oc-014 | 乙=oc-008 （什么版本 | 粉色横幅点不点）
- 组25 甲=oc-025 | 乙=oc-013 （多模型怎么搭配划算 | 自动兜底怎么设）
- 组26 甲=oc-032 | 乙=oc-035 （不是说离线吗咋还要网 | 没网你能干啥）
- 组27 甲=oc-040 | 乙=oc-041 （断网把U盘弄坏了吗 | 断网U盘还能打开吗）
- 组28 甲=oc-042 | 乙=oc-038 （网速卡能用云端吗 | WiFi连着还offline）
- 组29 甲=oc-033 | 乙=oc-038 （怎么检查网络 | WiFi连着还offline）
- 组30 甲=oc-024 | 乙=oc-018 （为什么要输令牌 | 令牌去哪找）
- 组31 甲=oc-006 | 乙=oc-002 （黑框碍眼能不能隐藏 | 黑框能不能关）——同一答案对，但你要把问法写得一隐一显，让模型学"碍眼"和"关闭"都指向同一答案
- 组32 甲=oc-016 | 乙=oc-019 （换电脑能用吗 | 公司电脑留痕迹吗）
- 组33 甲=oc-022 | 乙=oc-021 （Defender怎么放行 | 杀毒报警加白名单）
- 组34 甲=oc-015 | 乙=oc-008 （想升级怎么办 | 看到更新横幅怎么办）
- 组35 甲=oc-026 | 乙=oc-004 （多弄几个key | 发行方没给key）
- 组36 甲=oc-044 | 乙=oc-034 （网络恢复了记录还在吗 | 怎么切回云端）
- 组37 甲=oc-029 | 乙=oc-028 （微信能聊吗 | 联网搜索怎么开）
- 组38 甲=oc-031 | 乙=oc-036 （怎么判断离线 | unknown是不是被封）
- 组39 甲=oc-007 | 乙=oc-002 （怎么退出 | 黑框能关吗）——与组21互为镜像，问法必须换一批新的
- 组40 甲=oc-001 | 乙=oc-003 （插上就能用吗 | 第一次要等多久）

---

## 任务 C：评估错题回补（12 题 × 3 变体 = 36 条，1 批交付）

以下问法是真实评估中模型答错的题。为每题写 3 个句法不同的新变体（含原意即可，不要逐字抄原题），答案逐字用我给的话术：
- cw-01 首次是不是插上就能聊 → 答案=oc-001答案
- cw-02 把黑框关了会怎样 → 答案=oc-002答案
- cw-03 想换个更聪明的模型在哪换 → 答案=oc-010答案
- cw-04 两个模型能自动接力吗 → 答案=oc-013答案
- cw-05 怕盘丢了想加密 → 答案=oc-023答案
- cw-06 换电脑聊天记录还在吗 → 答案=oc-016答案
- cw-07 微软杀毒已经把文件删了怎么办 → 答案逐字：`这超出了我的离线能力。我是应急小助手，联网后的大模型才是干这个的。`（ category=capability_refusal ）
- cw-08 手机能上网就电脑不行 → 答案逐字：`那是电脑这边的网络问题。看看网线插没插好，或重连WiFi，再重启路由器试试。`（category=network_help，通用引导无事实库原文）
- cw-09 卡巴斯基报毒该信任哪个程序 → 答案=oc-021答案
- cw-10 启动报18789端口占用 → 答案=oc-017答案
- cw-11 token忘了去哪找 → 答案=oc-018答案
- cw-12 360怎么加白名单 → 答案=oc-021答案

---

## 交付顺序与验收

A1 → A2 → A3 → B1 → B2 → C，每批交付时附：条目数、id 清单、答案逐字核对声明（"本批所有 answer 均逐字复制，未改一字"）。
我收到每批会做抽查，发现答案被改写/字数超限/句法没变，整批打回。
全部完成后我合并质检，无需你合并。
