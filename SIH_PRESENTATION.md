# EcoSmart Waste: SIH 2026 Pitch Pack

## 1. Problem
Campuses and cities have bins but no feedback loop. Overflowing bins and dumping go unreported, nobody knows which zones are hotspots, people don't know how to segregate, and there is no reason to participate.

## 2. Solution
One platform for citizens, sanitation staff and admin: report (photo + location) -> track status -> collect on schedule -> reward good behavior -> admin sees hotspots and acts.

## 3. Features
Garbage reporting with photo and pin | segregation guide (wet/dry/e-waste) | pickup scheduling | admin dashboard | rewards + leaderboard | hotspot heatmap | notifications + complaint tracking (Received > Assigned > In progress > Resolved).

## 4. Suggested PPT (10 slides)
1 Title + team | 2 Problem | 3 Existing gaps | 4 Our solution | 5 Demo screenshots (report, heatmap, admin)
6 Architecture | 7 What makes it different (reward loop + live hotspot heatmap) | 8 Impact + pilot data | 9 Scalability + business model | 10 Roadmap + ask

## 5. Architecture
Frontend (HTML/JS PWA) -> REST API (FastAPI) -> SQLite (demo) / PostgreSQL (production). Photos: object storage. Future: TF-Lite waste classifier.

## 6. Roadmap (8 weeks)
W1 survey 30-50 students + wireframes | W2 auth + database | W3 reporting + tracking | W4 wire frontend to API | W5 admin dashboard + heatmap
W6 rewards + scheduling | W7 pilot in one hostel block, collect real numbers | W8 polish, demo video, PPT.

## 7. Team roles (6)
Lead/pitch | Frontend | Admin UI/design | Backend | ML/data | Field research + QA.

## 8. Business model
SaaS subscription for colleges, housing societies and municipalities; sponsored rewards from local brands; paid sustainability reports.

## 9. Jury Q&A
- **How is it different?** Most apps only take complaints. We add guidance, scheduling, rewards and a live hotspot heatmap in one loop.
- **Will people use it?** 10-second reporting flow, points and leaderboards; we measure participation in the pilot.
- **Fake reports?** Location pin required, admin verification, flagged accounts lose points.
- **Scalability?** Add org_id to tables for multi-tenant use; move to PostgreSQL; one admin panel per institution or ward.
- **Privacy?** Minimal data; leaderboards show blocks, not names.
- **What's real vs. demo?** The prototype works end to end in the browser; the API is ready; real pilot data comes from week 7.

## 10. Future scope
AI photo classification, IoT fill sensors, collection route optimization, recycler marketplace, multi-language, municipal integration.
