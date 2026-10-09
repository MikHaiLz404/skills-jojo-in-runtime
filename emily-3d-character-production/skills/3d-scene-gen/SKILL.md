---
name: 3d-scene-gen
description: Guided 3D scene prompt builder — survey → validate → generate scene-gen prompt
metadata:
  author: jojo-in-runtime
  tags: [3d, scene, prompt-builder, blender-mcp]
  version: 1.0.0
  updated: 2026-09-09
---

# 3d-scene-gen

Prompt builder สำหรับงาน 3D scene/environment gen — environment, props, object animation, camera choreography

**ไม่รวม**: character design, rigging, animation retarget → ดู Redirect Rules

## Workflow

```
Survey → Validate → Generate → Review
```

## Survey (1 turn — batched bullet, ห้ามถามทีละข้อ)

**Required (ต้องครบ 4 ข้อก่อน generate):**
- Scene description? e.g. "Japanese flower shop exterior"
- Object inventory? e.g. "vending machine, bikes, flower pots, awnings, trees"
- Visual style? [Photorealistic / Cartoon / Anime / Low-poly / Isometric]
- Tool environment? [Blender MCP / ComfyUI / Other]

**Should (ว่าง → ใช้ default):**
- Reference image? [มี / ไม่มี] → default: ไม่มี
- Animation? [Static / Object keyframe / 3-phase explode] → default: Static
- Camera? [Fixed / Orbit / Dolly / Fly-through] → default: Fixed 3/4
- Frame range + fps? e.g. "250 frames @ 24fps" → default: 250 @ 24fps
- Render resolution? [1920x1080 / 3840x2160 / Custom] → default: 1920x1080
- Render engine? [Cycles / Eevee / Both] → default: Cycles
- Technical constraint? e.g. "quads only, ~50k polys" _(optional)_

**ตัวอย่างต้องปรับตาม domain ของ scene ที่ user ให้ไว้ตอนแรก** — ไม่ใช้ตัวอย่างของ scene อื่น

## Validate

- ครบ required 4/4 → generate ทันที
- ขาด required → ถามเฉพาะ field ที่ขาด (max 2 follow-ups) — ห้ามวนถาม survey ทั้งชุด
- Should ว่าง → ใช้ default

## Redirect Rules

| งาน | ส่งไป |
|-----|-------|
| Character design / character sheet | `character-sheet-pipeline` |
| Animation retarget | `blender-retarget-workflow` |
| Rigging / armature | domain-specific Blender skill |

## Prompt Pattern (output)

```
[Tool] + [Subject]
  → [Enumerated inventory — จาก survey]
  → [Style + mood]
  → [Animation phases — 3-phase / static / object-keyframe]
  → [Camera + background]
  → [Render spec — resolution, samples, format]
  → [Deliverables + naming]
```

## Anti-patterns

- ห้ามถามทีละข้อ (one-by-one) — เสีย token ซ้ำกับ context overhead
- ห้าม generate เมื่อ required ไม่ครบ — ส่ง prompt อ่อนให้ MCP เปล่าประโยชน์
- ห้าม scope creep character/rigging เข้า survey
- ห้ามวนลูปถาม field เดิมซ้ำ (max 2 follow-ups)
