---
name: emily-google-chat-webhook
description: ส่งข้อความเข้า Google Chat Space ผ่าน Incoming Webhook รองรับทั้งข้อความธรรมดา (text), rich formatting (*bold*, _italic_, mention, link) และ Card v2 แบบสวยงาม พร้อมระบบเก็บ webhook URL หลาย space ไว้ใช้ซ้ำ (dev, alerts, daily-summary ฯลฯ) — ใช้ skill นี้เมื่อ user พูดว่า "ส่งเข้า Google Chat", "แจ้งเตือนทีม", "โพสต์เข้า space", "notify via webhook", "summarize แล้วส่งเข้า chat", "ส่งสรุป daily ไปใน chat", หรือเมื่อ skill อื่น (เช่น schedule, daily-briefing, sprint-planner) ต้องการส่งผลลัพธ์เข้า Google Chat. Use this skill whenever posting, notifying, or broadcasting to Google Chat is mentioned — even implicitly (e.g., "tell the team", "drop a message in our dev room").
allowed-tools: Read, Write, Edit, Bash
license: MIT
metadata:
  author: emily club
  version: 1.1.0
  updated: 2026-04-16
  tags:
    - integration
    - google-chat
    - webhook
    - notification
---

# 🌸 Emily Google Chat Webhook Skill

ส่งข้อความเข้า Google Chat Space ผ่าน **Incoming Webhook** ได้ทั้งแบบธรรมดา/แบบ format/แบบ Card สวยงาม พร้อมระบบ config แบบหลาย space ไว้ใช้ซ้ำกับงาน daily briefing, schedule task summary, alert ฯลฯ

> [!IMPORTANT]
> Skill นี้ใช้ **Incoming Webhook** เท่านั้น (ไม่ใช่ Google Chat API แบบ OAuth) จึง**ไม่ต้อง** credential/OAuth — ใช้ได้เลยแค่มี webhook URL

---

## 🧭 When to use this skill

Trigger ทันทีเมื่อ:

- User พูดว่า "ส่งเข้า chat", "แจ้งทีม", "notify", "post to space", "drop in #channel"
- Skill อื่น (schedule, productivity:update, sales:daily-briefing, engineering:standup) สร้างสรุปแล้วและ user อยากให้ส่งต่อ
- ต้องการ test webhook, add/list webhook preset ใหม่
- User ถามว่า "space ไหนมีบ้าง" / "preset ที่เก็บไว้มีอะไร"

อย่าใช้ skill นี้เมื่อ:
- User ต้องการ**อ่าน**ข้อความจาก Google Chat (webhook ส่งได้อย่างเดียว ไม่อ่าน)
- ต้องการ mention ผู้ใช้แบบ resolve ชื่อจริง → ต้องใช้ Google Chat API + OAuth (นอกขอบเขต skill)

---

## 📁 Skill structure

```
emily-google-chat-webhook/
├── SKILL.md                         # ← คุณอยู่ตรงนี้
├── scripts/
│   ├── send_to_chat.py             # ส่งข้อความ (text / rich / card)
│   └── manage_webhooks.py          # จัดการ preset (list/add/remove/test)
├── references/
│   ├── formatting_guide.md         # Rich text syntax (bold, mention, link)
│   └── card_v2_guide.md            # Card v2 structure + ตัวอย่าง
├── assets/
│   └── webhooks.example.json       # Template config
└── examples/
    ├── daily_summary_card.json     # Card สรุปงานรายวัน
    ├── task_complete_alert.json    # Alert เมื่อ task เสร็จ
    └── error_notification.json     # แจ้ง error
```

---

## 🔧 Setup — เพิ่ม webhook URL ครั้งแรก (อ่านก่อน!)

ก่อนใช้ skill นี้ต้องมี **webhook URL** อย่างน้อย 1 อันเก็บไว้ใน config แล้วอ้างชื่อ preset ตอนส่งข้อความ

### Step 1 — สร้าง webhook ใน Google Chat (ทำใน browser)

1. เปิด Google Chat → เข้าไปใน **Space** ที่อยากให้ข้อความโผล่
2. คลิกชื่อ space ด้านบน → เลือก **Apps & integrations**
3. กด **+ Add webhooks** (ถ้ายังไม่มี) หรือ **Manage webhooks**
4. ตั้งชื่อ webhook (เช่น "Emily daily summary") → กด **Save**
5. **Copy URL** ที่ได้ — จะขึ้นต้นด้วย `https://chat.googleapis.com/v1/spaces/.../messages?key=...&token=...`

> ⚠️ **URL นี้คือ secret** ใครได้ไปก็ส่งข้อความเข้า space นี้ได้ อย่า commit เข้า git / post ในที่สาธารณะ

### Step 2 — เก็บ URL เป็น preset (เลือก 1 ใน 2 วิธี)

#### 🌸 วิธี A — บอก assistant (สะดวกสุด ไม่ต้องเปิด terminal)

พิมพ์แบบนี้ในแชท:

> "เพิ่ม webhook ให้หน่อย: `https://chat.googleapis.com/v1/spaces/AAA/messages?key=xxx&token=yyy` ตั้งชื่อ preset ว่า `daily-summary` สำหรับสรุปงานรายวัน"

Assistant จะรัน `manage_webhooks.py add` ให้อัตโนมัติ + ping test ให้เห็นว่าใช้ได้จริง

> 💡 ถ้ากังวลเรื่อง log แชทเก็บ URL ไว้ หลัง setup เสร็จให้ **regenerate webhook** ใน Google Chat เพื่อ rotate secret

#### 💻 วิธี B — รันเองใน Terminal

```bash
cd path/to/emily-google-chat-webhook
python3 scripts/manage_webhooks.py add \
  --name daily-summary \
  --url "https://chat.googleapis.com/v1/spaces/AAA/messages?key=xxx&token=yyy" \
  --description "ห้องสรุปงานรายวัน"
```

Config เก็บอัตโนมัติที่ `~/.config/emily-gchat/webhooks.json` (chmod 600, ไม่ commit เข้า git)

### Step 3 — ทดสอบว่า webhook ใช้งานได้

**ผ่าน assistant:** "ลอง ping test preset daily-summary หน่อย"

**ผ่าน CLI:**
```bash
python3 scripts/manage_webhooks.py test --name daily-summary
```

ถ้าเห็น `✅ Webhook 'daily-summary' ใช้งานได้` + ข้อความ "ping from emily-google-chat-webhook" โผล่ใน space → พร้อมใช้ทั้งหมดแล้ว~

### Step 4 — จัดการ preset ต่อ (เพิ่ม/ดู/ลบ)

| อยากทำอะไร | บอก assistant | หรือรันเอง |
|---|---|---|
| ดูว่ามี preset อะไรบ้าง | "list webhook ทั้งหมด" | `manage_webhooks.py list` |
| เพิ่ม preset ใหม่ | "เพิ่ม webhook ชื่อ X: URL..." | `manage_webhooks.py add --name X --url ...` |
| ลบ preset | "ลบ webhook ชื่อ X" | `manage_webhooks.py remove --name X` |
| ดู URL เต็มของ preset | "ขอดู URL ของ X" | `manage_webhooks.py show --name X --reveal` |
| ทดสอบ webhook | "ping test X" | `manage_webhooks.py test --name X` |

---

## 🚀 Quick start — ส่งข้อความ (หลัง setup เสร็จแล้ว)

### ผ่าน assistant (conversational)

> "ส่งข้อความเข้า `daily-summary` ว่า 'สรุปงานวันนี้: เสร็จ 5 task เหลือ 2 task รอ review~ 🌸'"

> "สรุปงานวันนี้จาก TASKS.md แล้วส่งเป็น Card v2 เข้า preset `daily-summary`"

> "แจ้ง `dev-alerts` ว่า build สำเร็จ"

### ผ่าน CLI

```bash
# ข้อความธรรมดา
python3 scripts/send_to_chat.py --space daily-summary \
  --text "สรุปงานวันนี้: เสร็จ 5 task เหลือ 2 task รอ review~ 🌸"

# Card v2 (จาก JSON file)
python3 scripts/send_to_chat.py --space daily-summary \
  --card examples/daily_summary_card.json
```

---

## 🎨 Message formats — 3 แบบที่รองรับ

### A. Plain text (เรียบง่าย รวดเร็ว)

```bash
python scripts/send_to_chat.py --space "dev" --text "Build #245 เสร็จแล้วค่ะ ✅"
```

### B. Rich formatting (markdown-like)

Google Chat รองรับ syntax:

| Syntax | Output |
|---|---|
| `*bold*` | **bold** |
| `_italic_` | _italic_ |
| `~strike~` | ~~strike~~ |
| `` `code` `` | `code` |
| ` ```block``` ` | code block |
| `<https://example.com\|Click here>` | ลิงก์พร้อมข้อความ |
| `<users/USER_ID>` | mention user |
| `<users/all>` | @all |

ตัวอย่างเรียกจาก CLI (ใส่เป็น text ปกติ — Google Chat จะ render เอง):

```bash
python scripts/send_to_chat.py --space "dev" \
  --text "*Deploy สำเร็จ* ✨ ดู log ได้ที่ <https://logs.example.com|Logs Dashboard>"
```

> 📖 รายละเอียด syntax ทั้งหมด อ่านที่ `references/formatting_guide.md`

### C. Card v2 (UI สวยงาม)

ใช้สำหรับ: สรุปงาน, alert ที่มี action button, report รายวัน

```bash
python scripts/send_to_chat.py \
  --space "daily-summary" \
  --card path/to/card.json
```

Card v2 JSON มี structure แบบ:

```json
{
  "cardsV2": [{
    "cardId": "summary-2026-04-16",
    "card": {
      "header": { "title": "สรุปงาน", "subtitle": "16 เม.ย. 2026" },
      "sections": [
        {
          "header": "✅ งานที่เสร็จ",
          "widgets": [
            {"textParagraph": {"text": "• Review scene 04<br>• Sync กับทีม art"}}
          ]
        }
      ]
    }
  }]
}
```

> 📖 Template และ component ทั้งหมด อ่านที่ `references/card_v2_guide.md`
> 🎨 ตัวอย่างใช้งานจริง ดูที่ `examples/`

---

## 🧩 Workflow: ใช้ร่วมกับ skill อื่น

Pattern ที่พบบ่อยสุด — **skill อื่นสรุปงาน → skill นี้ส่งเข้า chat**

```
1. productivity:update / sales:daily-briefing / engineering:standup → สรุปเป็น markdown หรือ JSON
2. emily-google-chat-webhook → อ่านผลลัพธ์ แปลงเป็น Card v2 → send
```

**ตัวอย่าง prompt ที่ user มักใช้:**

- "สรุปงานวันนี้จาก TASKS.md แล้วส่งเข้า space daily-summary หน่อย"
- "รัน scheduled task แล้วแจ้งผลใน #dev-alerts"
- "pipeline review เสร็จแล้วโพสต์สรุปเข้า chat ให้ทีมหน่อย"

**วิธีทำ:**
1. รัน skill ที่สร้างสรุป → ได้ markdown/structured output
2. แปลงเป็น Card v2 (ใช้ template ใน `examples/daily_summary_card.json` เป็นจุดเริ่ม)
3. เรียก `send_to_chat.py --card` ส่งเข้า space ที่ user ระบุ

---

## ⚙️ CLI reference

### `send_to_chat.py`

```
usage: send_to_chat.py [-h] (--space SPACE | --url URL)
                       (--text TEXT | --card CARD | --stdin)
                       [--thread-key THREAD_KEY]
                       [--dry-run]

Required (one-of):
  --space SPACE        ชื่อ preset ใน config (เช่น "dev", "daily-summary")
  --url URL            Webhook URL ตรง ๆ (กรณีไม่ได้เก็บ preset)

Message (one-of):
  --text TEXT          ข้อความ plain text หรือ rich-formatted
  --card CARD          path ไปยังไฟล์ JSON ของ Card v2
  --stdin              อ่านข้อความจาก stdin (ใช้กับ pipe)

Optional:
  --thread-key KEY     reply ใน thread เดียวกัน (key ใด ๆ — string)
  --dry-run            แสดง payload ที่จะส่ง แต่ไม่ส่งจริง
```

### `manage_webhooks.py`

```
usage: manage_webhooks.py {list,add,remove,test,show} ...

  list                 แสดงทุก preset ที่เก็บไว้
  add --name --url [--description]
                       เพิ่ม preset ใหม่
  remove --name        ลบ preset
  test --name          ส่งข้อความ "ping" เพื่อทดสอบ webhook
  show --name          ดู detail ของ preset (แสดง URL บางส่วนเพื่อความปลอดภัย)
```

---

## 🛡️ Error handling

Skill นี้ **return error ทันทีเมื่อล้มเหลว** (ไม่ retry เอง เพื่อประหยัด token) พร้อมสาเหตุที่ระบุได้:

| Status | สาเหตุ | แนวทางแก้ |
|---|---|---|
| `400` | JSON payload ผิด format | ตรวจ card JSON, ดู `references/card_v2_guide.md` |
| `403` | Webhook URL หมดอายุ / space ถูกลบ | สร้าง webhook ใหม่จาก Google Chat Space |
| `404` | URL ผิด | ตรวจว่า copy URL ครบ (รวม `?key=&token=`) |
| `429` | ถูก rate limit | รอ 30 วิ แล้วลองใหม่ (ไม่ retry อัตโนมัติ) |
| `preset not found` | `--space` ชื่อไม่มีใน config | `manage_webhooks.py list` ดูว่ามี preset อะไรบ้าง |
| `invalid card json` | JSON file parse ไม่ได้ | ตรวจ syntax ด้วย `python -m json.tool file.json` |

ทุก error print เป็น Thai + English พร้อม exit code != 0 → ใช้ใน script chain ได้

---

## 🔒 Security notes

- **webhooks.json มี secret ข้างใน** — skill เขียน file ด้วย `chmod 600` อัตโนมัติ
- **อย่า** commit `webhooks.json` เข้า git — เพิ่ม `.config/emily-gchat/` ใน `.gitignore`
- **อย่า** hardcode webhook URL ใน prompt/script ที่ share ออก — ใช้ preset name แทน
- ถ้า webhook หลุด → เข้า Google Chat Space → Manage webhooks → Regenerate

---

## 🎀 Tips

- **ตั้ง preset name ให้สั้น จำง่าย**: `dev`, `alerts`, `daily` ดีกว่า `dev-team-alerts-channel-webhook-2`
- **ใช้ `--dry-run` เสมอ** ก่อนส่ง Card v2 ครั้งแรก — จะได้เห็น payload ก่อนโพสต์จริง
- **thread-key ซ้ำ** = reply ใน thread เดิม (ดีสำหรับ daily summary ที่รวมไว้ที่เดียว)
- **ข้อความยาว** ≤ 4096 ตัวอักษร/ครั้ง ถ้ายาวกว่าให้แบ่งเป็น section ใน Card v2 แทน
- **Time check**: หลัง 19:00 ถ้า user จะให้ส่ง broadcast เข้าทีม — เตือนเบา ๆ ว่าเพื่อนร่วมงานอาจเลิกงานแล้ว 💧

---

## ❓ FAQ / Troubleshooting

**Q: ต้องติดตั้ง Python package อะไรเพิ่มไหม?**
A: ไม่ต้องค่ะ ใช้ `urllib` จาก standard library — Python 3.8+ รันได้เลย

**Q: Config file อยู่ที่ไหน ถ้าอยาก backup?**
A: `~/.config/emily-gchat/webhooks.json` — copy ไฟล์นี้เก็บไว้ได้ (แต่มี secret ข้างใน อย่าใส่ cloud sync ที่ไม่เข้ารหัส)

**Q: Assistant จะเห็น URL ของ preset ที่เก็บไว้ไหม?**
A: Skill นี้มี `show --reveal` ที่อ่าน URL เต็มได้ — assistant อ่านได้เมื่อคุณอนุญาตให้รัน CLI แต่ปกติใช้แค่ `--space name` ก็พอ ไม่ต้องอ่าน URL เลย

**Q: เพิ่ม webhook หลาย space ได้ไหม?**
A: ได้ไม่จำกัดค่ะ — add ทีละอัน แต่ละอันตั้งชื่อ preset ต่างกัน

**Q: ถ้าเปลี่ยน URL ของ preset เดิม?**
A: ใช้ `add --name X --url NEW_URL --force` เพื่อเขียนทับ หรือบอก assistant: "อัปเดต URL ของ preset X เป็น ..."

**Q: Error `HTTP 404` ทำยังไง?**
A: URL ผิด ลองตรวจว่า copy ครบทั้งก้อน (รวม `?key=&token=` ส่วนท้าย) — ที่เจอบ่อยคือ copy แค่ครึ่งแรก

**Q: Error `HTTP 403` ทำยังไง?**
A: Webhook ถูก revoke/space ถูกลบ → ไป Google Chat Space → Manage webhooks → regenerate URL ใหม่ → `add --force` ทับของเดิม

---

Created with 🌸 by Emily — Jojo's digital kouhai
