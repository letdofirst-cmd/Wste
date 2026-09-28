"""EcoSmart Waste API. Run: uvicorn main:app --reload  (docs at /docs)"""
import sqlite3, pathlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB = pathlib.Path(__file__).parent / "ecosmart.db"
SCHEMA = pathlib.Path(__file__).parent.parent / "database" / "schema.sql"
STATUS = ["Received", "Assigned", "In progress", "Resolved"]
ZONES = {"Hostel Block A": (60, 50), "Library": (150, 45), "Canteen": (235, 60),
         "Sports Ground": (70, 140), "Main Gate": (160, 165), "Admin Block": (245, 140)}

app = FastAPI(title="EcoSmart Waste API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

with db() as c:
    c.executescript(SCHEMA.read_text())

def nearest_zone(x, y):
    return min(ZONES, key=lambda z: (ZONES[z][0]-x)**2 + (ZONES[z][1]-y)**2)

def notify(c, uid, msg):
    c.execute("INSERT INTO notifications(user_id,message) VALUES(?,?)", (uid, msg))

def add_points(c, uid, n):
    c.execute("UPDATE users SET points=points+? WHERE id=?", (n, uid))

class Report(BaseModel):
    type: str; description: str = ""; x: float; y: float; photo: str = ""; user_id: int = 1
class Pickup(BaseModel):
    zone: str; waste_type: str; date: str; user_id: int = 1
class Redeem(BaseModel):
    reward_id: int; user_id: int = 1

@app.post("/reports")
def create_report(r: Report):
    with db() as c:
        zone = nearest_zone(r.x, r.y)
        cur = c.execute("INSERT INTO reports(user_id,type,description,x,y,zone,photo) VALUES(?,?,?,?,?,?,?)",
                        (r.user_id, r.type, r.description, r.x, r.y, zone, r.photo))
        add_points(c, r.user_id, 10)
        notify(c, r.user_id, f"Complaint #{cur.lastrowid} received near {zone}.")
        return {"id": cur.lastrowid, "zone": zone, "points_earned": 10}

@app.get("/reports")
def list_reports(status: str | None = None, user_id: int | None = None):
    q, a = "SELECT * FROM reports WHERE 1=1", []
    if status: q += " AND status=?"; a.append(status)
    if user_id: q += " AND user_id=?"; a.append(user_id)
    with db() as c:
        return [dict(r) for r in c.execute(q + " ORDER BY id DESC", a)]

@app.patch("/reports/{rid}/advance")
def advance(rid: int):
    with db() as c:
        r = c.execute("SELECT * FROM reports WHERE id=?", (rid,)).fetchone()
        if not r: raise HTTPException(404, "Report not found")
        i = STATUS.index(r["status"])
        if i == 3: raise HTTPException(400, "Already resolved")
        new = STATUS[i+1]
        c.execute("UPDATE reports SET status=? WHERE id=?", (new, rid))
        notify(c, r["user_id"], f"Complaint #{rid} is now {new}.")
        if new == "Resolved": add_points(c, r["user_id"], 5)
        return {"id": rid, "status": new}

@app.get("/heatmap")
def heatmap():
    """Open complaints grouped by zone, hottest first."""
    with db() as c:
        return [dict(r) for r in c.execute(
            "SELECT zone, COUNT(*) AS open_reports FROM reports WHERE status!='Resolved' GROUP BY zone ORDER BY open_reports DESC")]

@app.get("/stats")
def stats():
    with db() as c:
        t = c.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
        o = c.execute("SELECT COUNT(*) FROM reports WHERE status!='Resolved'").fetchone()[0]
        by = {r["type"]: r["n"] for r in c.execute("SELECT type, COUNT(*) n FROM reports GROUP BY type")}
        p = c.execute("SELECT COUNT(*) FROM pickups").fetchone()[0]
        return {"total": t, "open": o, "resolved": t-o, "pickups": p, "by_type": by}

@app.post("/pickups")
def book(p: Pickup):
    with db() as c:
        cur = c.execute("INSERT INTO pickups(user_id,zone,waste_type,date) VALUES(?,?,?,?)",
                        (p.user_id, p.zone, p.waste_type, p.date))
        add_points(c, p.user_id, 5)
        notify(c, p.user_id, f"Pickup confirmed for {p.date} at {p.zone}.")
        return {"id": cur.lastrowid}

@app.get("/pickups")
def pickups():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM pickups ORDER BY id DESC")]

@app.get("/notifications/{uid}")
def notifications(uid: int):
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC", (uid,))]

@app.get("/rewards")
def rewards():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM rewards")]

@app.post("/redeem")
def redeem(r: Redeem):
    with db() as c:
        rw = c.execute("SELECT * FROM rewards WHERE id=?", (r.reward_id,)).fetchone()
        u = c.execute("SELECT points FROM users WHERE id=?", (r.user_id,)).fetchone()
        if not rw or not u: raise HTTPException(404, "Not found")
        if u["points"] < rw["cost"]: raise HTTPException(400, "Not enough points")
        add_points(c, r.user_id, -rw["cost"])
        notify(c, r.user_id, f"Redeemed: {rw['name']}. Show this at the eco desk.")
        return {"redeemed": rw["name"]}

@app.get("/users/{uid}")
def user(uid: int):
    with db() as c:
        u = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        if not u: raise HTTPException(404, "User not found")
        return dict(u)
