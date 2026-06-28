import os
import csv
import re

def norm(name):
    return name.replace("’", "'").replace("“", '"').replace("”", '"').replace("Fightin' (Michael) Busch Lights", "Fightin' Busch Lights").strip().lower()

def parse_standings(file_path):
    standings = []
    matchups = {}
    current_period = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    mode = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line == '"Standings"':
            mode = "standings"
            continue
        elif "Scoring Period:" in line:
            mode = "matchups"
            current_period = re.search(r"Scoring Period:\s*(\d+)", line).group(1)
            matchups[current_period] = []
            continue
            
        reader = csv.reader([line])
        row = next(reader)
        
        if mode == "standings":
            if row[0] == "Rank":
                continue
            standings.append({
                "Rank": int(row[0]),
                "Team": row[1].strip(),
                "W": int(row[2]),
                "L": int(row[3]),
                "T": int(row[4]),
                "Win%": float(row[5]),
                "GB": float(row[6]) if row[6] != '-' else 0.0,
                "WW": int(row[7]),
                "PtsF": float(row[8]),
                "PtsA": float(row[9])
            })
        elif mode == "matchups":
            if row[0].startswith("Team"):
                continue
            matchups[current_period].append({
                "Team": row[0].strip(),
                "W": int(row[1]),
                "L": int(row[2]),
                "T": int(row[3]),
                "Pts": float(row[4]),
                "R": int(row[5]),
                "HR": int(row[6]),
                "RBI": int(row[7]),
                "SB": int(row[8]),
                "OPS": float(row[9]),
                "QS": int(row[10]),
                "K": int(row[11]),
                "ERA": float(row[12]),
                "WHIP": float(row[13]),
                "SVH": int(row[14])
            })
            
    return standings, matchups

# Load Standings & Matchups
standings, matchups = parse_standings("trade-deadline/standings.csv")

# Apply scoring period 13
p13 = matchups.get("13", [])
p13_dict = {m["Team"]: m for m in p13}

# Helper to normalize for lookup
def clean_team_name(name):
    n = name.replace("’", "'").replace("‘", "'").strip()
    if "Busch Lights" in n:
        return "Fightin' (Michael) Busch Lights"
    return n

p13_norm = {norm(k): v for k, v in p13_dict.items()}

for s in standings:
    t_norm = norm(s["Team"])
    match = p13_norm.get(t_norm)
    if match:
        s["W_prev"] = s["W"]
        s["L_prev"] = s["L"]
        s["T_prev"] = s["T"]
        s["W"] += match["W"]
        s["L"] += match["L"]
        s["T"] += match["T"]
        total_games = s["W"] + s["L"] + s["T"]
        s["Win%"] = (s["W"] + 0.5 * s["T"]) / total_games if total_games > 0 else 0
        s["Matchup_Result"] = f"{match['W']}-{match['L']}-{match['T']}"
        s["Matchup_Pts"] = match["Pts"]
    else:
        s["W_prev"] = s["W"]
        s["L_prev"] = s["L"]
        s["T_prev"] = s["T"]
        s["Matchup_Result"] = "N/A"
        s["Matchup_Pts"] = 0.0

# Sort standings
updated_standings = sorted(standings, key=lambda x: (x["Win%"], x["W"]), reverse=True)

# Compute GB
leader = updated_standings[0]
for i, s in enumerate(updated_standings):
    s["Rank"] = i + 1
    gb = ((leader["W"] - s["W"]) + (s["L"] - leader["L"])) / 2.0
    s["GB"] = gb

# Categorize tiers
# Heavy Buyers: GB <= 2.0
# Moderate Buyers: GB > 2.0 and GB <= 10.0
# Bubble: GB > 10.0 and GB <= 20.0
# Sellers: GB > 20.0
def get_tier(s):
    if s["GB"] <= 2.0:
        return "Heavy Buyer (Contender)"
    elif s["GB"] <= 10.0:
        return "Moderate Buyer (Fringe Contender)"
    elif s["GB"] <= 20.0:
        return "The Bubble (Undecided / Retooling)"
    else:
        return "Seller (Rebuilder)"

for s in updated_standings:
    s["Tier"] = get_tier(s)

# Load Rosters
roster_dir = "trade-deadline/rosters"
roster_files = [f for f in os.listdir(roster_dir) if f.endswith(".csv")]

standings_teams = [s["Team"] for s in updated_standings]

def find_team_from_filename(filename):
    name_clean = filename.replace(".csv", "").replace("_", " ").strip().lower()
    for t in standings_teams:
        t_clean = t.replace("’", "'").replace("'", "").replace("<3", "").strip().lower()
        if "ped" in name_clean and "ped" in t_clean:
            return t
        if "busch" in name_clean and "busch" in t_clean:
            return t
        if name_clean in t_clean or t_clean in name_clean:
            return t
    return filename

all_players = []
for rf in roster_files:
    team_name = find_team_from_filename(rf)
    file_path = os.path.join(roster_dir, rf)
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    mode = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line == '"","Hitting"':
            mode = "hitting"
            continue
        elif line == '"","Pitching"':
            mode = "pitching"
            continue
            
        reader = csv.reader([line])
        row = next(reader)
        if row[0] == "ID" or not row[0]:
            continue
            
        if mode == "hitting" and len(row) >= 14:
            try:
                all_players.append({
                    "TeamName": team_name,
                    "Type": "Hitter",
                    "ID": row[0],
                    "Pos": row[1],
                    "Player": row[2],
                    "MLBTeam": row[3],
                    "Eligible": row[4],
                    "Status": row[5],
                    "Age": int(row[6]) if row[6].isdigit() else 0,
                    "AB": int(row[7]) if row[7].isdigit() else 0,
                    "R": int(row[8]) if row[8].isdigit() else 0,
                    "H": int(row[9]) if row[9].isdigit() else 0,
                    "HR": int(row[10]) if row[10].isdigit() else 0,
                    "RBI": int(row[11]) if row[11].isdigit() else 0,
                    "SB": int(row[12]) if row[12].isdigit() else 0,
                    "OPS": float(row[13]) if row[13].replace('.', '', 1).isdigit() else 0.0,
                    "GP": int(row[14]) if row[14].isdigit() else 0
                })
            except Exception as e:
                pass
        elif mode == "pitching" and len(row) >= 13:
            try:
                all_players.append({
                    "TeamName": team_name,
                    "Type": "Pitcher",
                    "ID": row[0],
                    "Pos": row[1],
                    "Player": row[2],
                    "MLBTeam": row[3],
                    "Eligible": row[4],
                    "Status": row[5],
                    "Age": int(row[6]) if row[6].isdigit() else 0,
                    "IP": float(row[7]) if row[7].replace('.', '', 1).isdigit() else 0.0,
                    "ERA": float(row[8]) if row[8].replace('.', '', 1).isdigit() else 0.0,
                    "WHIP": float(row[9]) if row[9].replace('.', '', 1).isdigit() else 0.0,
                    "K": int(row[10]) if row[10].isdigit() else 0,
                    "QS": int(row[11]) if row[11].isdigit() else 0,
                    "SVH": int(row[12]) if row[12].isdigit() else 0,
                    "GP": int(row[13]) if row[13].isdigit() else 0 if len(row) > 13 else 0
                })
            except Exception as e:
                pass

# Let's map teams to their tier for easy access
team_tiers = {s["Team"]: s["Tier"] for s in updated_standings}

# We want to identify the top trade chips from Seller & Bubble teams.
# Sellers: Fightin' (Michael) Busch Lights, gochargers, We <3 PEDs, Short Porch Soldiers
# Bubble: pcorcoran3, Sasaki Bombs, Mount My Castle
trade_source_teams = [
    "Fightin' (Michael) Busch Lights", 
    "gochargers", 
    "We <3 PEDs", 
    "Short Porch Soldiers",
    "pcorcoran3",
    "Sasaki Bombs",
    "Mount My Castle"
]

# Let's filter players on these teams and find the absolute elite ones to feature on the big board.
# Hitters: AB > 100 and (OPS > 0.750 or HR > 10 or SB > 10)
# Pitchers (SP): IP > 40 and (ERA < 4.20 or K > 60)
# Pitchers (RP): SVH > 10
big_board_candidates = []

for p in all_players:
    if p["TeamName"] not in trade_source_teams:
        continue
    
    tier = team_tiers.get(p["TeamName"], "Unknown")
    is_seller = "Seller" in tier
    
    if p["Type"] == "Hitter":
        # Calculate a simple "Score" for ranking
        # score = OPS * 100 + HR * 2 + SB * 1.5 - (Age - 27)*0.5 (older players slightly less value, but still good)
        if p["AB"] >= 50:
            score = p["OPS"] * 100 + p["HR"] * 1.5 + p["SB"] * 1.0
            # Boost if elite stats
            big_board_candidates.append({
                "Player": p["Player"],
                "Pos": p["Pos"],
                "Team": p["TeamName"],
                "Tier": tier,
                "Type": "Hitter",
                "Age": p["Age"],
                "Details": f"OPS: {p['OPS']:.3f} | HR: {p['HR']} | SB: {p['SB']} | AB: {p['AB']}",
                "Score": score
            })
    elif p["Type"] == "Pitcher":
        if p["Pos"] in ["SP", "P"] and p["IP"] >= 30:
            # lower ERA/WHIP is better, high K is better
            # score = K * 0.8 + (6.0 - ERA)*15 + (1.8 - WHIP)*30
            # Handle ERA of 0
            era_val = p["ERA"] if p["ERA"] > 0 else 4.0
            whip_val = p["WHIP"] if p["WHIP"] > 0 else 1.3
            score = p["K"] * 0.8 + (6.0 - era_val) * 12 + (1.8 - whip_val) * 20
            big_board_candidates.append({
                "Player": p["Player"],
                "Pos": p["Pos"],
                "Team": p["TeamName"],
                "Tier": tier,
                "Type": "SP",
                "Age": p["Age"],
                "Details": f"ERA: {p['ERA']:.2f} | WHIP: {p['WHIP']:.2f} | K: {p['K']} | IP: {p['IP']}",
                "Score": score
            })
        elif p["Pos"] == "RP" or p["SVH"] >= 8:
            # Reliever score: SVH * 3 + (5.0 - ERA)*10 + K * 0.5
            era_val = p["ERA"] if p["ERA"] > 0 else 4.0
            score = p["SVH"] * 4.0 + (5.0 - era_val) * 8 + p["K"] * 0.5
            big_board_candidates.append({
                "Player": p["Player"],
                "Pos": p["Pos"],
                "Team": p["TeamName"],
                "Tier": tier,
                "Type": "RP",
                "Age": p["Age"],
                "Details": f"SVH: {p['SVH']} | ERA: {p['ERA']:.2f} | WHIP: {p['WHIP']:.2f} | K: {p['K']}",
                "Score": score
            })

# Sort big board candidates by Score descending
big_board = sorted(big_board_candidates, key=lambda x: x["Score"], reverse=True)

# Select top 25 trade targets
top_trade_targets = big_board[:25]

# Write README.md inside trade-deadline/
readme_path = "trade-deadline/README.md"
with open(readme_path, "w", encoding="utf-8") as f:
    f.write("# 2026 Fantasy Baseball Trade Deadline Preview - Data Summary\n\n")
    f.write("> [!NOTE]\n")
    f.write("> This document summarizes the findings from the standings, scoring period 13 matchups, and team rosters. Use this as a reference for writing the main preview article.\n\n")
    
    f.write("## 1. Updated Standings (After Scoring Period 13)\n")
    f.write("Applying the matches from Scoring Period 13 results in a major shakeup at the top, with Scotts Tots and Vladdy's Daycare tied in Win%, and The Old Timers just 0.5 Games Behind!\n\n")
    
    f.write("| Rank | Team | Record | Win% | GB | P13 Result | Tier |\n")
    f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
    for s in updated_standings:
        f.write(f"| {s['Rank']} | {s['Team']} | {s['W']}-{s['L']}-{s['T']} | {s['Win%']:.3f} | {s['GB']} | {s['Matchup_Result']} ({s['Matchup_Pts']} pts) | {s['Tier']} |\n")
    
    f.write("\n## 2. Team Tiers\n\n")
    
    f.write("### 🏆 Heavy Buyers (Contenders)\n")
    f.write("These teams are in a direct race for the championship and will be looking to trade future assets (draft picks, cheap keepers) for immediate help.\n")
    for s in updated_standings:
        if s["Tier"] == "Heavy Buyer (Contender)":
            f.write(f"- **{s['Team']}** (Win%: {s['Win%']:.3f}, {s['GB']} GB) - Crucial match wins in P13 keep them in the absolute elite tier.\n")
            
    f.write("\n### ⚔️ Moderate Buyers (Fringe Contenders)\n")
    f.write("These teams are firmly in the playoff hunt but are a step behind the top 3. They will look for value additions to bridge the gap.\n")
    for s in updated_standings:
        if s["Tier"] == "Moderate Buyer (Fringe Contenders)":
            f.write(f"- **{s['Team']}** (Win%: {s['Win%']:.3f}, {s['GB']} GB)\n")
    # For matching "Moderate Buyer (Fringe Contender)" or similar, print all remaining
    for s in updated_standings:
        if "Moderate Buyer" in s["Tier"]:
            f.write(f"- **{s['Team']}** (Win%: {s['Win%']:.3f}, {s['GB']} GB)\n")
            
    f.write("\n### ⚖️ The Bubble (Undecided / Retooling)\n")
    f.write("These teams are in the middle of the pack. They could go either way: buy cheap help or sell off expiring veterans for future keepers.\n")
    for s in updated_standings:
        if "The Bubble" in s["Tier"]:
            f.write(f"- **{s['Team']}** (Win%: {s['Win%']:.3f}, {s['GB']} GB)\n")
            
    f.write("\n### 📉 Sellers (Rebuilders)\n")
    f.write("These teams are effectively out of the title race and should be looking to sell veteran players for draft picks or young keepers.\n")
    for s in updated_standings:
        if "Seller" in s["Tier"]:
            f.write(f"- **{s['Team']}** (Win%: {s['Win%']:.3f}, {s['GB']} GB)\n")
            
    f.write("\n## 3. Trade Deadline Player Big Board\n")
    f.write("These are the top 25 trade targets currently rostered on Seller or Bubble teams, ranked by their current performance metrics (OPS for hitters, K/ERA/WHIP for SPs, SVH for RPs).\n\n")
    
    f.write("| Rank | Player | Pos | Age | Current Team | Team Tier | Stat Line |\n")
    f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
    for idx, p in enumerate(top_trade_targets):
        f.write(f"| {idx+1} | **{p['Player']}** | {p['Pos']} | {p['Age']} | {p['Team']} | {p['Tier'].split(' (')[0]} | {p['Details']} |\n")
        
    f.write("\n\n## 4. Notable Trade Chips by Category\n\n")
    
    f.write("### 🔥 Elite Starting Pitchers (SPs)\n")
    sps = [p for p in big_board if p["Type"] == "SP"][:6]
    for p in sps:
        f.write(f"- **{p['Player']}** ({p['Pos']}, {p['Team']}): Age {p['Age']} - `{p['Details']}`\n")
        
    f.write("\n### ⚾ High-Impact Hitters\n")
    hitters = [p for p in big_board if p["Type"] == "Hitter"][:6]
    for p in hitters:
        f.write(f"- **{p['Player']}** ({p['Pos']}, {p['Team']}): Age {p['Age']} - `{p['Details']}`\n")
        
    f.write("\n### 🔒 Relief Pitchers & Closers (RPs)\n")
    rps = [p for p in big_board if p["Type"] == "RP"][:6]
    for p in rps:
        f.write(f"- **{p['Player']}** ({p['Pos']}, {p['Team']}): Age {p['Age']} - `{p['Details']}`\n")

print("Successfully generated trade-deadline/README.md")
