import os
import csv
import json
import re

def norm(name):
    return name.replace("’", "'").replace("“", '"').replace("”", '"').replace("Fightin' (Michael) Busch Lights", "Fightin' Busch Lights").strip().lower()

def md_to_html(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'[\u2600-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD10-\uDDFF]', '', text)
    return text

# Parse Standings and Matchups from standings.csv
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
                "WinPct": float(row[5]),
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

# Parse Keepers CSV
def parse_keepers(file_path):
    team_mapping = {
        1: "Fightin' Busch Lights",
        6: "OnlyDans",
        11: "Short Porch Soldiers",
        16: "gochargers",
        21: "We <3 PEDs",
        26: "Mount My Castle",
        31: "Kposer",
        36: "pcorcoran3",
        41: "Scotts Tots",
        46: "The Old Timers",
        51: "Sasaki Bombs",
        56: "Vladdy’s Daycare"
    }
    
    keepers = {}
    if not os.path.exists(file_path):
        return keepers
        
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    current_year = None
    for r_idx, row in enumerate(rows):
        if not row:
            continue
        if row[0].strip() in ["2026", "2027", "2028"]:
            current_year = row[0].strip()
            continue
        if len(row) > 1 and row[1].strip() == "Player":
            continue
            
        for offset, team_name in team_mapping.items():
            if len(row) <= offset:
                continue
            player_name = row[offset].strip()
            if not player_name or player_name in ["#REF!", "Player"]:
                continue
                
            years = row[offset+1].strip() if len(row) > offset+1 else ""
            pick = row[offset+2].strip() if len(row) > offset+2 else ""
            rank = row[offset+4].strip() if len(row) > offset+4 else ""
            
            p_norm = norm(player_name)
            if p_norm not in keepers:
                keepers[p_norm] = []
                
            keepers[p_norm].append({
                "Year": current_year,
                "Team": team_name,
                "ContractYears": years,
                "DraftPickCost": pick,
                "Rank": rank
            })
            
    return keepers

# Parse Draft CSV
def parse_draft(file_path):
    draft_picks = {}
    if not os.path.exists(file_path):
        return draft_picks
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if not row or len(row) < 6:
                continue
            player_id = row[0].replace('"', '').strip()
            if player_id == "*" or not player_id:
                continue
            round_val = row[1].strip()
            round_num = int(round_val) if round_val.isdigit() else 25
            player_name = row[5].replace('"', '').strip()
            if player_name:
                draft_picks[player_id] = round_num
                draft_picks[norm(player_name)] = round_num
    return draft_picks

# Load Standing, Keepers, Draft
standings, matchups = parse_standings("trade-deadline/standings.csv")
keepers_database = parse_keepers("trade-deadline/keepers.csv")
draft_picks = parse_draft("trade-deadline/draft.csv")

# Apply scoring period 13 to standings
p13 = matchups.get("13", [])
p13_dict = {m["Team"]: m for m in p13}
p13_norm = {norm(k): v for k, v in p13_dict.items()}

for s in standings:
    t_norm = norm(s["Team"])
    match = p13_norm.get(t_norm)
    if match:
        s["W"] += match["W"]
        s["L"] += match["L"]
        s["T"] += match["T"]
        total_games = s["W"] + s["L"] + s["T"]
        s["WinPct"] = (s["W"] + 0.5 * s["T"]) / total_games if total_games > 0 else 0
        s["Matchup_Result"] = f"{match['W']}-{match['L']}-{match['T']}"

updated_standings = sorted(standings, key=lambda x: (x["WinPct"], x["W"]), reverse=True)

leader = updated_standings[0]
for i, s in enumerate(updated_standings):
    s["Rank"] = i + 1
    s["GB"] = ((leader["W"] - s["W"]) + (s["L"] - leader["L"])) / 2.0

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

team_tiers = {s["Team"]: s["Tier"] for s in updated_standings}

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
            
        player_id = row[0].replace('"', '').strip()
        
        if mode == "hitting" and len(row) >= 14:
            try:
                p_data = {
                    "ID": player_id,
                    "Type": "Hitter",
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
                    "GP": int(row[14]) if row[14].isdigit() else 0,
                    "FantasyTeam": team_name
                }
                all_players.append(p_data)
            except Exception:
                pass
        elif mode == "pitching" and len(row) >= 13:
            try:
                p_data = {
                    "ID": player_id,
                    "Type": "Pitcher",
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
                    "GP": int(row[13]) if row[13].isdigit() else 0 if len(row) > 13 else 0,
                    "FantasyTeam": team_name
                }
                all_players.append(p_data)
            except Exception:
                pass

# Player details blurbs
player_details_map = {
    "Chris Sale": {
        "blurb": "Chris Sale is having a spectacular resurgent season at age 37, posting a 2.14 ERA and 99 Ks. Because he is under contract through 2027 at a cheap 4th-round draft pick cost, he offers the highest surplus keeper value in the league. Vladdy's Daycare wants to secure him to solidify their postseason rotation depth, and Short Porch Soldiers will command a premium return for this bargain contract.",
    },
    "Cam Schlittler": {
        "blurb": "If you haven't been paying attention to Mount My Castle lately, you're missing a historic campaign from Cam Schlittler. The kid has been flat-out untouchable, posting a microscopic 1.62 ERA and a 0.92 WHIP. Since he is a first-year waiver pickup, he is available to sign to a long-term contract at a cheap 5th-round draft pick cost, making him an absolute goldmine. Scotts Tots is looking to pair him with Paul Skenes, and Mount My Castle is demanding a 2027 first-round pick to let him go.",
    },
    "Jhoan Duran": {
        "blurb": "Need absolute gas in the back of your bullpen? Jhoan Duran is throwing heat with a 1.63 ERA and 20 saves/holds. He's available to sign at a 4th-round cost this winter, generating massive long-term value. Scotts Tots is dead last in Saves + Holds and should be bidding aggressively to land Duran and save their bullpen.",
    },
    "Chase Burns": {
        "blurb": "The rookie starting pitcher has been spectacular, posting a 2.36 ERA and 112 Ks in 91.2 IP. Since he is available to sign in the 3rd round this winter, Short Porch Soldiers will want a massive package to let him go. Scotts Tots has the young assets and draft capital to make a play, looking to build a dominant rotation for years to come.",
    },
    "Louis Varland": {
        "blurb": "Louis Varland is quietly having a lights-out season, locking down 21 saves/holds with an elite 0.82 ERA and 1.01 WHIP. He is available to sign in the 25th round this winter, making him a high-value asset on the market. Contenders like Vladdy's Daycare and Scotts Tots are both in play to fix their relief pitching.",
    },
    "Bobby Witt Jr.": {
        "blurb": "Bobby Witt Jr. is an absolute superstar, contributing 28 SBs and an .826 OPS. Since his contract runs through 2028, Sasaki Bombs will demand a historic haul to let him go. The Old Timers—who rank near the bottom with only 68 stolen bases—have the assets to pull off a deal. Despite costing a 1st-round pick, Witt's three years of elite production make him worth every penny.",
    },
    "Zack Wheeler": {
        "blurb": "Zack Wheeler remains the gold standard for starting pitching. He's cruising with a 2.03 ERA and an elite 0.86 WHIP. Since his contract runs through 2027 at a 1st-round draft pick cost, he offers no draft discount but provides two full playoff runs of elite ace production. We &lt;3 PEDs is looking to jumpstart their rebuild and has all the leverage.",
    },
    "Yoshinobu Yamamoto": {
        "blurb": "Yoshinobu Yamamoto's elite command (2.67 ERA, 0.89 WHIP) makes him an ideal target for teams looking to secure their pitching ratios. Under contract through 2027 at a 1st-round cost, Sasaki Bombs has him on the block as they look to restock their draft cupboard, and The Old Timers are monitoring closely.",
    },
    "Dylan Cease": {
        "blurb": "If strikeouts are your bottleneck, Dylan Cease is the solution. He has racked up 128 Ks in 83.1 innings with a 3.02 ERA. Kept through 2027 at a 1st-round cost, he will command a solid package from a contender. Kposer and The Old Timers have both checked in, as Short Porch Soldiers look to swap their starting arm for early draft picks.",
    },
    "Jacob deGrom": {
        "blurb": "Even at this stage in his career, Jacob deGrom misses bats at an elite rate, racking up 106 Ks in 88.2 IP with a 3.55 ERA. Since his contract runs through 2028 at a 2nd-round draft pick cost, he gives any acquiring team three full playoff runs of control at a slight discount. We &lt;3 PEDs is looking to reload, and Vladdy's Daycare is interested.",
    },
    "Yordan Alvarez": {
        "blurb": "Yordan Alvarez is the premier offensive rental on the market. Plain and simple. He is slugging 25 homers with a 1.045 OPS. Because his keeper contract is expiring this year at a 1st-round cost, he has zero future keeper value to a buyer. OnlyDans is the obvious match; they have a massive bullpen surplus to trade but desperately need Alvarez's power to boost their bottom-tier OPS.",
    },
    "Shohei Ohtani": {
        "blurb": "It's easy to forget Ohtani's pitching value when he is rostered as a pitcher-only asset. He has been brilliant for Mount My Castle, logging a 1.58 ERA and 0.90 WHIP. Since his contract is expiring this season at a 1st-round cost, he is a pure rental. Mount My Castle will be shopping him actively before he goes back into the draft, and The Old Timers are looking to bring him in.",
    },
    "Max Meyer": {
        "blurb": "Max Meyer has been a steady rotation presence, cruising with a 2.60 ERA and 107 Ks. Since he is available to sign as a waiver pickup in the 25th round this winter, Sasaki Bombs will want a solid return. Kposer is the prime suitor; their rotation has been a disaster, and they need Meyer's ratios to climb out of the pitching basement.",
    },
    "Foster Griffin": {
        "blurb": "Foster Griffin has been a reliable workhorse, keeping a clean 2.93 ERA and 98 Ks in 98.1 IP. Because he is available to sign in the 25th round, he is a perfect low-cost target for Kposer to insulate their rotation ratios.",
    },
    "Miguel Vargas": {
        "blurb": "Miguel Vargas has been quietly producing a strong season with 18 HR, 10 SB, and an .841 OPS. Since he is available to sign in the 16th round, OnlyDans is looking to acquire him to add versatile power to their offense.",
    }
}

selling_teams = ["Fightin' Busch Lights", "gochargers", "We <3 PEDs", "Short Porch Soldiers", "pcorcoran3", "Sasaki Bombs", "Mount My Castle"]
selling_targets = []

for p in all_players:
    t_name = p["FantasyTeam"]
    if t_name not in selling_teams:
        continue
        
    p_norm = norm(p["Player"])
    tier = team_tiers.get(t_name, "Unknown")
    
    # Check keeper database
    keeper_options = keepers_database.get(p_norm, [])
    ko_26 = next((ko for ko in keeper_options if ko["Year"] == "2026"), None)
    
    keeper_text = ""
    keeper_round_display = ""
    keeper_bonus = 0
    
    if ko_26:
        years = ko_26["ContractYears"]
        cost_str = ko_26["DraftPickCost"].strip()
        
        # Map DraftPickCost to round
        if cost_str in ["Free", "-2", "-1", "0", ""]:
            keeper_round_num = 1
            keeper_round_str = "1st"
        else:
            digits = re.findall(r'\d+', cost_str)
            if digits:
                r_num = int(digits[0])
                keeper_round_num = r_num
                if r_num == 1: keeper_round_str = "1st"
                elif r_num == 2: keeper_round_str = "2nd"
                elif r_num == 3: keeper_round_str = "3rd"
                else: keeper_round_str = f"{r_num}th"
            else:
                keeper_round_num = 1
                keeper_round_str = "1st"

        if years == "1":
            keeper_text = "expiring"
            keeper_round_display = keeper_round_str
            keeper_bonus = 0
        elif years == "2":
            keeper_text = "through 2027"
            keeper_round_display = keeper_round_str
            if keeper_round_num > 1:
                keeper_bonus = 20
            else:
                keeper_bonus = 2
        elif years == "3":
            keeper_text = "through 2028"
            keeper_round_display = keeper_round_str
            if keeper_round_num > 1:
                keeper_bonus = 25
            else:
                keeper_bonus = 5
        else:
            keeper_text = "control"
            keeper_round_display = keeper_round_str
            keeper_bonus = 5
    else:
        # First year on roster, available to sign
        keeper_text = "available to sign"
        p_id = p["ID"].strip()
        
        # Look up in draft_picks
        if p_id in draft_picks:
            draft_round = draft_picks[p_id]
            keeper_round_num = draft_round
            if draft_round == 1: keeper_round_display = "1st"
            elif draft_round == 2: keeper_round_display = "2nd"
            elif draft_round == 3: keeper_round_display = "3rd"
            else: keeper_round_display = f"{draft_round}th"
            
            # Map keeper bonus for drafted rookies
            if draft_round >= 15:
                keeper_bonus = 25
            elif draft_round >= 10:
                keeper_bonus = 20
            elif draft_round >= 4:
                keeper_bonus = 15
            else:
                keeper_bonus = 5
        elif p_norm in draft_picks:
            draft_round = draft_picks[p_norm]
            keeper_round_num = draft_round
            if draft_round == 1: keeper_round_display = "1st"
            elif draft_round == 2: keeper_round_display = "2nd"
            elif draft_round == 3: keeper_round_display = "3rd"
            else: keeper_round_display = f"{draft_round}th"
            
            if draft_round >= 15:
                keeper_bonus = 25
            elif draft_round >= 10:
                keeper_bonus = 20
            elif draft_round >= 4:
                keeper_bonus = 15
            else:
                keeper_bonus = 5
        else:
            keeper_round_num = 25
            keeper_round_display = "Waiver/FA (25th)"
            keeper_bonus = 35 # Waiver pickups have huge keeper surplus value
            
    # Calculate performance score
    perf_score = 0
    details = ""
    if p["Type"] == "Hitter":
        perf_score = p["OPS"] * 100 + p["HR"] * 1.5 + p["SB"] * 1.0
        details = f"OPS: {p['OPS']:.3f} • {p['HR']} HR • {p['SB']} SB • {p['AB']} AB"
    else:
        era_val = p["ERA"] if p["ERA"] > 0 else 4.0
        whip_val = p["WHIP"] if p["WHIP"] > 0 else 1.3
        if p["Pos"] in ["SP", "P"]:
            perf_score = p["K"] * 0.8 + (6.0 - era_val) * 12 + (1.8 - whip_val) * 20
            details = f"SP • {p['ERA']:.2f} ERA • {p['WHIP']:.2f} WHIP • {p['K']} K • {p['IP']} IP"
        else:
            perf_score = p["SVH"] * 4.0 + (5.0 - era_val) * 8 + p["K"] * 0.5
            details = f"RP • {p['SVH']} SVH • {p['ERA']:.2f} ERA • {p['WHIP']:.2f} WHIP • {p['K']} K"
            
    final_score = perf_score + keeper_bonus
    
    # Filter minimum requirements to keep list high quality
    if p["Type"] == "Hitter" and p["AB"] < 50:
        continue
    if p["Type"] == "Pitcher" and p["Pos"] in ["SP", "P"] and p["IP"] < 25:
        continue
    if p["Type"] == "Pitcher" and p["Pos"] == "RP" and p["SVH"] < 5:
        continue
        
    blurb_str = player_details_map.get(p["Player"], {}).get("blurb", f"A productive option performing well at {p['Pos']} for {t_name}.")
    
    # Only keep players who are in the details map to ensure we have custom blurbs
    if p["Player"] in player_details_map:
        player_entry = {
            "Player": p["Player"],
            "Pos": p["Pos"],
            "Team": t_name,
            "Tier": tier,
            "Type": p["Type"] if p["Type"] == "Hitter" else ("SP" if p["Pos"] in ["SP", "P"] else "RP"),
            "Age": p["Age"],
            "Contract": keeper_text,
            "KeeperRound": keeper_round_display,
            "Details": details,
            "Score": final_score,
            "Blurb": blurb_str
        }
        selling_targets.append(player_entry)

# Sort by Score descending
selling_targets = sorted(selling_targets, key=lambda x: x["Score"], reverse=True)

# Build dynamic Big Board list
bigboard_html = ""
for idx, p in enumerate(selling_targets):
    badge_color = "text-emerald-800 bg-emerald-50"
    if p["Contract"] == "expiring":
        badge_color = "text-red-800 bg-red-50"
    elif "through" in p["Contract"]:
        badge_color = "text-blue-800 bg-blue-50"
        
    bigboard_html += f"""
      <!-- Player {idx+1} -->
      <div class="space-y-3 font-serif">
        <div class="flex items-baseline justify-between border-b border-neutral-350 pb-2">
          <h3 class="text-xl font-bold text-neutral-900">{idx+1}. {p['Player']}</h3>
          <span class="text-xs font-mono font-bold uppercase tracking-wider {badge_color} px-2 py-0.5 rounded">{p['Contract']}</span>
        </div>
        <div class="text-xs font-mono text-neutral-500 uppercase tracking-wider">
          {p['Details']} • Keeper Round: {p['KeeperRound']}
        </div>
        <p class="text-neutral-700">
          {p['Blurb']}
        </p>
      </div>
    """

# Build dynamic README.md top players
readme_players = ""
for idx, p in enumerate(selling_targets):
    readme_players += f"{idx+1}. **{p['Player']}** ({p['Pos']} - {p['Team']}) [{p['Contract']}]\n"
    readme_players += f"   * *Stats:* {p['Details']} | *Keeper Round:* {p['KeeperRound']}\n"
    readme_players += f"   * *Analysis:* {p['Blurb']}\n\n"

# JavaScript tab switcher — must be outside f-string to avoid // comment conflicts
js_block = """
  <script>
    function switchTab(tabId) {
      // Hide all sections
      const sections = document.querySelectorAll('.tab-section');
      sections.forEach(sec => sec.classList.add('hidden'));

      // Show target section
      const activeSection = document.getElementById('tab-content-' + tabId);
      if (activeSection) {
        activeSection.classList.remove('hidden');
      }

      // Remove active class from all buttons
      const buttons = document.querySelectorAll('.tab-btn');
      buttons.forEach(btn => {
        btn.classList.remove('text-[#8b1e1e]', 'border-[#8b1e1e]', 'active');
        btn.classList.add('text-slate-500', 'border-transparent');
      });

      // Add active class to clicked button
      const activeBtn = document.getElementById('btn-' + tabId);
      if (activeBtn) {
        activeBtn.classList.remove('text-slate-500', 'border-transparent');
        activeBtn.classList.add('text-[#8b1e1e]', 'border-[#8b1e1e]', 'active');
      }
    }

    // Default initialization
    document.addEventListener("DOMContentLoaded", function() {
      switchTab('editorial');
    });
  </script>
"""

# HTML Template - news article
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>2026 Fantasy Baseball Trade Deadline Preview | Sports Column</title>
  <!-- Google Fonts: Outfit (headers), Lora (serif body) -->
  <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Outfit:wght@450;600;800&display=swap" rel="stylesheet">
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['Outfit', 'sans-serif'],
            serif: ['Lora', 'serif'],
            display: ['Outfit', 'sans-serif'],
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{
      background-color: #faf9f6; /* Warm off-white print paper */
      color: #2b2b2a; /* Soft print black */
    }}
    .active {{
      border-bottom-width: 2px;
    }}
  </style>
</head>
<body class="font-sans antialiased pb-20">

  <!-- Main News Column Container -->
  <article class="max-w-xl mx-auto px-4 pt-8 md:max-w-3xl font-sans">
    
    <!-- Publication Logo Header -->
    <div class="border-b-2 border-double border-neutral-900 pb-3 mb-6 text-center">
      <p class="font-display text-xs tracking-widest text-[#8b1e1e] font-extrabold uppercase">THE LEAGUE PRESS</p>
    </div>

    <!-- Article Headings -->
    <header class="mb-10 space-y-4 text-center">
      <h1 class="font-serif text-4xl md:text-5xl font-black text-neutral-900 leading-tight">
        Championship Deadline: Who Buys, Who Sells, and the Moves That Will Decimate the League
      </h1>
      <p class="text-neutral-600 text-base font-medium md:text-lg max-w-xl mx-auto leading-relaxed">
        With Scotts Tots and Vladdy's Daycare locked in a death match at the top and The Old Timers breathing down their necks, next week's trade deadline is about to be a bloodbath.
      </p>
      
      <!-- Byline -->
      <div class="flex items-center justify-center space-x-2 pt-4 border-t border-neutral-350 text-xs text-neutral-500 font-mono">
        <span>By <strong class="text-neutral-800">The Commish</strong></span>
        <span>•</span>
        <span>June 2026</span>
      </div>
    </header>

    <!-- Sticky Navigation Tabs -->
    <div class="sticky top-0 z-50 bg-[#faf9f6]/95 backdrop-blur-md border-b border-neutral-350 mb-10 py-3">
      <nav class="flex justify-around text-xs font-bold font-display tracking-widest uppercase">
        <button id="btn-editorial" onclick="switchTab('editorial')" class="tab-btn pb-1 hover:text-[#8b1e1e] transition-colors duration-150 text-[#8b1e1e] border-[#8b1e1e] active">
          📰 Editorial
        </button>
        <button id="btn-bigboard" onclick="switchTab('bigboard')" class="tab-btn pb-1 hover:text-[#8b1e1e] transition-colors duration-150 text-slate-500 border-transparent">
          📋 Big Board
        </button>
        <button id="btn-blockbusters" onclick="switchTab('blockbusters')" class="tab-btn pb-1 hover:text-[#8b1e1e] transition-colors duration-150 text-slate-500 border-transparent">
          🤝 Blockbusters
        </button>
      </nav>
    </div>

    <!-- TAB 1: EDITORIAL COLUMN -->
    <div id="tab-content-editorial" class="tab-section space-y-6">
      
      <p class="first-letter:text-7xl first-letter:font-serif first-letter:font-bold first-letter:text-neutral-900 first-letter:float-left first-letter:mr-3 first-letter:line-height-1">
        We have an absolute dogfight at the summit. Following Scoring Period 13, Scotts Tots and Vladdy's Daycare are tied for first place with identical .612 win percentages, while The Old Timers sit just a half-game back in third. In a league where H2H matchups can turn on a single blown save or a cold week from an outfielder, standing pat at the deadline is essentially waving a white flag.
      </p>

      <p>
        Championships here aren't won by building the most well-rounded paper roster—they are won by targeted category acquisitions. The top contenders all have glaring statistical deficits that must be repaired immediately if they want to survive the playoff bracket.
      </p>

      <p>
        The league's keeper rules add a fascinating layer of leverage. Rebuilding teams holding expiring star contracts face a ticking clock: move them now, or watch them walk for nothing in the offseason. Meanwhile, stars who are in their first year on a roster are available to sign to long-term keeper extensions this winter. That makes guys like Cam Schlittler and Jhoan Duran incredibly expensive. Rebuilders don't have to move them, which means contenders will need to cough up premium draft pick capital to get them to the table.
      </p>

      <h2 class="font-serif text-2xl font-bold text-neutral-900 pt-6">The Bullpen Crisis at the Top</h2>
      <p>
        The most glaring opportunity on the board is the bullpen market. It is almost comical that Scotts Tots and Vladdy's Daycare occupy the top two spots in the standings given how awful their bullpens have been. Scotts Tots has registered a pathetic 16 Saves + Holds all year, and Vladdy’s Daycare is barely surviving with 24. A single shutdown reliever completely shifts the leverage at the top, making a high-volume arm the ultimate deadline prize.
      </p>
      <p>
        Relief depth is concentrated in just a few hands. OnlyDans sits in fifth, trailing by 9.0 games, but their bullpen is absolutely stacked with a league-best 63 Saves + Holds. However, they are starved for offensive juice, ranking near the bottom in both home runs (119) and OPS (.729). That mismatch sets up OnlyDans as the ultimate deadline gatekeeper—they can easily spare saves and holds if a contender is willing to pay in bats.
      </p>

      <h2 class="font-serif text-2xl font-bold text-neutral-900 pt-6">The Rotation Market Heating Up</h2>
      <p>
        While the leaders scrap over late-inning relief, The Old Timers have their sights set on a different prize: starting pitching stability. Despite pacing the league in home runs (178) and RBIs (535), they are bleeding ratios, posting a 4.09 team ERA and a 1.202 WHIP. Adding a sub-3.00 ERA starter is an absolute priority if they want to secure first place.
      </p>
      <p>
        Then there is Kposer. Despite holding some of the most productive hitters in the league, Kposer has pitching ratios that look like a horror show: a league-worst 4.45 ERA and an ugly 1.300 WHIP. If they do not add starting depth, their season is effectively over.
      </p>
      <p>
        Sellers are ready to capitalize. We &lt;3 PEDs is shopping Zack Wheeler, who is carrying an elite 2.03 ERA and a 0.86 WHIP. Because Wheeler's contract runs through 2027, he is the ultimate prize. Meanwhile, Short Porch Soldiers are taking calls on Dylan Cease (128 Ks) and Chris Sale (2.14 ERA), both under contract through 2027. If you want ratio control, the options are there—if you have the draft capital to pay for it.
      </p>

      <h2 class="font-serif text-2xl font-bold text-neutral-900 pt-6">The Veteran Bubble Dilemma: Pushing All-In</h2>
      <p>
        The most fascinating scenario at the deadline belongs to the <strong>Fightin' Busch Lights</strong>. Currently sitting in 7th place (.487 win percentage) and just outside the playoff bracket, the temptation to sell is high. But look at their roster: Salvador Perez (36), Nolan Arenado (35), Giancarlo Stanton (36), Jorge Soler (34), Pete Alonso (31), Willy Adames (30), Nathan Eovaldi (36), Carlos Rodon (33), and Max Fried (32).
      </p>
      <p>
        This is a roster built for <em>now</em>. Their championship window isn't just closing—it is slammed shut after this season. Selling off elite controllable pitching like Logan Gilbert (under contract through 2028) or reliever Bryan Baker might net them future assets, but it forfeits their last genuine shot at a title with this veteran core. If the Busch Lights are smart, they will reverse course, buy starting pitching depth, and make one final, aggressive run at the championship before the age curve and expiring contracts dissolve their roster.
      </p>

      <!-- Minimalist Draft Capital & Roster Assets List -->
      <h2 class="font-serif text-2xl font-bold text-neutral-900 pt-8 pb-2">Contender Draft Pick & Roster Assets</h2>
      <div class="space-y-4 font-serif text-sm text-neutral-700">
        <div class="border-b border-neutral-200 pb-3">
          <strong class="text-neutral-900 font-semibold block text-base font-sans">Scotts Tots</strong>
          Holds all original 2027 draft picks (Rounds 1–10). Best young trade chips include infield prospect Brooks Lee, outfielder Jackson Merrill, and young high-strikeout arm Nolan McLean.
        </div>
        <div class="border-b border-neutral-200 pb-3">
          <strong class="text-neutral-900 font-semibold block text-base font-sans">Vladdy’s Daycare</strong>
          Holds original 2027 picks plus an extra 3rd-round pick. Best young trade chips are outfielder Roman Anthony, utility prospect Sam Antonacci, and reliever Rico Garcia.
        </div>
        <div class="border-b border-neutral-200 pb-3">
          <strong class="text-neutral-900 font-semibold block text-base font-sans">The Old Timers</strong>
          Holds original picks, plus extra 2027 2nd and 4th round picks. Best trade chips are catcher Dillon Dingler, starter Reid Detmers, and veteran Corey Seager.
        </div>
        <div class="border-b border-neutral-200 pb-3">
          <strong class="text-neutral-900 font-semibold block text-base font-sans">OnlyDans</strong>
          Holds all original picks. Primary trade assets are outfielder Steven Kwan and young infielder Matt Shaw.
        </div>
        <div class="pb-3">
          <strong class="text-neutral-900 font-semibold block text-base font-sans">Kposer</strong>
          Holds original picks, minus their 3rd-round pick. Primary trade assets are Christian Walker and starter Nick Martinez.
        </div>
      </div>

    </div>

    <!-- TAB 2: THE BIG BOARD -->
    <div id="tab-content-bigboard" class="tab-section hidden space-y-12">
      {bigboard_html}
    </div>

    <!-- TAB 3: BLOCKBUSTER TRADES -->
    <div id="tab-content-blockbusters" class="tab-section hidden space-y-12">

      <!-- Trade 1 -->
      <div class="space-y-4 font-serif">
        <h3 class="text-lg font-bold font-display uppercase tracking-wider text-[#8b1e1e] border-b border-neutral-350 pb-1">Trade 1: The First-Place Bullpen Overhaul</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-sans font-medium text-neutral-800 pb-2">
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">Mount My Castle receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Brooks Lee (2B/3B/SS)</li>
              <li>Joey Cantillo (SP/RP)</li>
              <li>2027 1st Round Draft Pick</li>
            </ul>
          </div>
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">Scotts Tots receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Cam Schlittler (SP)</li>
              <li>Louis Varland (RP)</li>
            </ul>
          </div>
        </div>
        <p class="text-neutral-700">
          First-place Scotts Tots cannot ignore their catastrophic relief pitching situation any longer. The team has logged a pathetic 16 Saves + Holds all season, a weakness that will destroy them in the playoffs. By packaging Brooks Lee and Joey Cantillo alongside a 2027 first-round pick, they land two premium arms available to sign: Louis Varland to salvage their bullpen, and Cam Schlittler to anchor their starting rotation ratios alongside Paul Skenes. Mount My Castle secures their future core with high-end prospects and a top-tier draft pick.
        </p>
      </div>

      <!-- Trade 2 -->
      <div class="space-y-4 font-serif">
        <h3 class="text-lg font-bold font-display uppercase tracking-wider text-[#8b1e1e] border-b border-neutral-350 pb-1">Trade 2: The Ratio Reclamation Project</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-sans font-medium text-neutral-800 pb-2">
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">We &lt;3 PEDs receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>JJ Wetherholt (2B/SS)</li>
              <li>Reid Detmers (SP/RP)</li>
              <li>2027 1st Round Draft Pick</li>
            </ul>
          </div>
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">The Old Timers receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Zack Wheeler (SP)</li>
              <li>Jacob deGrom (SP)</li>
            </ul>
          </div>
        </div>
        <p class="text-neutral-700">
          The Old Timers are slugging their way through the league but are bleeding ratios, posting a 4.09 team ERA and 1.202 WHIP. They capitalize on We &lt;3 PEDs' rebuilding phase by shipping away JJ Wetherholt, Reid Detmers, and an early pick to bring in Zack Wheeler and Jacob deGrom. For a team trying to secure a championship, adding two elite starters under contract through 2027 is a absolute game-changer.
        </p>
      </div>

      <!-- Trade 3 -->
      <div class="space-y-4 font-serif">
        <h3 class="text-lg font-bold font-display uppercase tracking-wider text-[#8b1e1e] border-b border-neutral-350 pb-1">Trade 3: The Power-Bullpen Blockbuster</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-sans font-medium text-neutral-800 pb-2">
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">pcorcoran3 receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Steven Kwan (OF)</li>
              <li>2027 1st Round Draft Pick</li>
            </ul>
          </div>
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">OnlyDans receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Yordan Alvarez (OF)</li>
              <li>Jhoan Duran (RP)</li>
            </ul>
          </div>
        </div>
        <p class="text-neutral-700">
          OnlyDans holds a league-leading Saves + Holds total (63 SVH) but lacks offensive punch, ranking near the bottom in home runs and OPS. This trade swaps their bullpen surplus for elite bats, landing Yordan Alvarez and Jhoan Duran to instantly fix their offense. pcorcoran3 retools by converting Alvarez's expiring contract and Duran into Steven Kwan and a first-round selection.
        </p>
      </div>

      <!-- Trade 4 -->
      <div class="space-y-4 font-serif">
        <h3 class="text-lg font-bold font-display uppercase tracking-wider text-[#8b1e1e] border-b border-neutral-350 pb-1">Trade 4: The Strikeout Arms Race</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-sans font-medium text-neutral-800 pb-2">
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">Short Porch Soldiers receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Roman Anthony (OF)</li>
              <li>Sam Antonacci (2B/3B/SS/OF)</li>
              <li>2027 2nd Round Draft Pick</li>
            </ul>
          </div>
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">Vladdy's Daycare receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Dylan Cease (SP)</li>
              <li>Chris Sale (SP)</li>
            </ul>
          </div>
        </div>
        <p class="text-neutral-700">
          With Scotts Tots threatening to pull away, Vladdy’s Daycare shores up their starting pitching by acquiring Dylan Cease and Chris Sale. Both starters run through 2027, giving Vladdy's Daycare the depth they need to survive a long postseason run. Short Porch Soldiers pick up a premier outfield keeper in Roman Anthony, Sam Antonacci, and draft picks to anchor their future lineup.
        </p>
      </div>

      <!-- Trade 5 -->
      <div class="space-y-4 font-serif">
        <h3 class="text-lg font-bold font-display uppercase tracking-wider text-[#8b1e1e] border-b border-neutral-350 pb-1">Trade 5: The Speed & Aces Superdeal</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-sans font-medium text-neutral-800 pb-2">
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">Sasaki Bombs receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Corey Seager (SS)</li>
              <li>Paul Goldschmidt (1B)</li>
              <li>2027 1st Round Draft Pick</li>
              <li>2027 2nd Round Draft Pick</li>
            </ul>
          </div>
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">The Old Timers receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Bobby Witt Jr. (SS)</li>
              <li>Yoshinobu Yamamoto (SP)</li>
            </ul>
          </div>
        </div>
        <p class="text-neutral-700">
          The Old Timers are near the bottom of the league in speed with only 68 stolen bases. Acquiring Bobby Witt Jr. and Yoshinobu Yamamoto solves their base-running speed and starting pitching WHIP issues in a single move. Sasaki Bombs secures Corey Seager, Paul Goldschmidt, and a massive haul of early 2027 picks to rebuild their roster.
        </p>
      </div>

      <!-- Trade 6 -->
      <div class="space-y-4 font-serif">
        <h3 class="text-lg font-bold font-display uppercase tracking-wider text-[#8b1e1e] border-b border-neutral-350 pb-1">Trade 6: The Ratios Restoration Swap</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-sans font-medium text-neutral-800 pb-2">
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">Sasaki Bombs receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Christian Walker (1B)</li>
              <li>2027 2nd Round Draft Pick</li>
            </ul>
          </div>
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">Kposer receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Max Meyer (SP)</li>
              <li>Foster Griffin (SP)</li>
            </ul>
          </div>
        </div>
        <p class="text-neutral-700">
          Kposer's pitching statistics are a disaster, posting a league-worst 4.45 ERA and 1.300 WHIP. This trade stabilizes their starting rotation by acquiring Max Meyer and Foster Griffin. Sasaki Bombs adds Christian Walker's power hitting and a 2027 second-round pick to reload their roster.
        </p>
      </div>

      <!-- Trade 7 -->
      <div class="space-y-4 font-serif">
        <h3 class="text-lg font-bold font-display uppercase tracking-wider text-[#8b1e1e] border-b border-neutral-350 pb-1">Trade 7: The Reliever Sweep</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-sans font-medium text-neutral-800 pb-2">
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">Fightin' Busch Lights receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Jackson Merrill (OF)</li>
              <li>Nolan McLean (P)</li>
              <li>2027 3rd Round Draft Pick</li>
            </ul>
          </div>
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">Scotts Tots receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Bryan Baker (RP)</li>
              <li>Logan Gilbert (SP)</li>
            </ul>
          </div>
        </div>
        <p class="text-neutral-700">
          Scotts Tots continues their deadline aggressive buying phase, landing Bryan Baker to help fix their Saves + Holds deficit and Logan Gilbert to anchor their rotation. Fightin' Busch Lights retools by picking up Jackson Merrill and Nolan McLean to build their future lineup.
        </p>
      </div>

      <!-- Trade 8 -->
      <div class="space-y-4 font-serif">
        <h3 class="text-lg font-bold font-display uppercase tracking-wider text-[#8b1e1e] border-b border-neutral-350 pb-1">Trade 8: The Infield Depth Package</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-sans font-medium text-neutral-800 pb-2">
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">pcorcoran3 receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Matt Shaw (3B)</li>
              <li>2027 3rd Round Draft Pick</li>
              <li>2027 4th Round Draft Pick</li>
            </ul>
          </div>
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">OnlyDans receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Miguel Vargas (CI)</li>
              <li>Oneil Cruz (UT)</li>
            </ul>
          </div>
        </div>
        <p class="text-neutral-700">
          OnlyDans continues to address their hitting power shortage by bringing in Miguel Vargas and Oneil Cruz. pcorcoran3 retools by adding Matt Shaw, a premium young infield keeper, along with two middle-round picks to anchor their future infield.
        </p>
      </div>

      <!-- Trade 9 -->
      <div class="space-y-4 font-serif">
        <h3 class="text-lg font-bold font-display uppercase tracking-wider text-[#8b1e1e] border-b border-neutral-350 pb-1">Trade 9: The Outfield Rental Blockbuster</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-sans font-medium text-neutral-800 pb-2">
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">We &lt;3 PEDs receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>2027 4th Round Draft Pick</li>
              <li>2027 5th Round Draft Pick</li>
            </ul>
          </div>
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">Vladdy's Daycare receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Mickey Moniak (OF)</li>
              <li>Ian Happ (OF)</li>
            </ul>
          </div>
        </div>
        <p class="text-neutral-700">
          Vladdy's Daycare adds outfield depth for the stretch run by trading away mid-round selections. We &lt;3 PEDs continues to stockpile draft picks to rebuild their roster during the offseason.
        </p>
      </div>

      <!-- Trade 10 -->
      <div class="space-y-4 font-serif">
        <h3 class="text-lg font-bold font-display uppercase tracking-wider text-[#8b1e1e] border-b border-neutral-350 pb-1">Trade 10: The Veteran Power Swap</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-sans font-medium text-neutral-800 pb-2">
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">pcorcoran3 receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Dillon Dingler (C)</li>
              <li>2027 2nd Round Draft Pick</li>
            </ul>
          </div>
          <div>
            <span class="text-xs text-neutral-400 font-bold uppercase block tracking-wider mb-1">The Old Timers receives</span>
            <ul class="list-disc list-inside space-y-0.5">
              <li>Willson Contreras (1B/C)</li>
              <li>Aaron Judge (OF)</li>
            </ul>
          </div>
        </div>
        <p class="text-neutral-700">
          The Old Timers complete an offensive dynasty by adding Aaron Judge and Willson Contreras. pcorcoran3 lands a highly productive young catcher in Dillon Dingler and a valuable 2027 second-round draft selection.
        </p>
      </div>

    </div>

  </article>

  <!-- Interactive Tabs Logic -->
  {js_block}

</body>
</html>
"""

# Write index.html
with open("trade-deadline/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Generated trade-deadline/index.html")

# Write README.md
with open("trade-deadline/README.md", "w", encoding="utf-8") as f:
    f.write(f"""# 2026 Fantasy Baseball Trade Deadline Preview - News Column

> [!NOTE]
> This document acts as an editorial log summarizing the key news storylines of the fantasy trade deadline.

## Standings Recap
Applying Scoring Period 13 results reveals an absolute dead tie at the top between Scotts Tots and Vladdy's Daycare, with The Old Timers breathing down their necks just 0.5 GB.

## Contender Needs & Fits
- **Scotts Tots** - Need: Relief Pitching / SVH (severe bullpen crisis, only 16 saves/holds)
- **Vladdy's Daycare** - Need: Relief Pitching / SVH (bullpen depth, only 24 saves/holds)
- **The Old Timers** - Need: Starting Pitching ERA/WHIP (4.09 ERA) & Stolen Bases (only 68 SB)
- **OnlyDans** - Need: Hitting power / HR (119 HR) & OPS (.729 OPS)
- **Kposer** - Need: Desperate starting pitching (worst ERA and WHIP in the league)

## Contender Draft Pick & Roster Assets Glance
* **Scotts Tots**: Holds all original 2027 draft picks. Key assets: Brooks Lee (2B), Jackson Merrill (OF), Nolan McLean (P).
* **Vladdy’s Daycare**: Holds original picks plus an extra 2027 3rd. Key assets: Roman Anthony (OF), Sam Antonacci (2B/SS), Rico Garcia (RP).
* **The Old Timers**: Holds original picks plus extra 2nd and 4th rounders. Key assets: Dillon Dingler (C), Reid Detmers (SP), Corey Seager (SS), Paul Goldschmidt (1B).
* **OnlyDans**: Holds original picks. Key assets: Steven Kwan (OF), Matt Shaw (3B).
* **Kposer**: Holds original picks (minus 3rd). Key assets: Christian Walker (1B), Nick Martinez (SP).

## Editorial Feature: The Veteran Bubble Dilemma (Fightin' Busch Lights)
Currently sitting in 7th place (.487 win percentage) and just outside the playoff bracket, the temptation to sell is high for the **Fightin' Busch Lights**. However, their roster is heavily built for the present: Salvador Perez (36), Nolan Arenado (35), Giancarlo Stanton (36), Jorge Soler (34), Pete Alonso (31), Willy Adames (30), Nathan Eovaldi (36), Carlos Rodon (33), and Max Fried (32).

This championship window is closed after this season. Trading controllable assets like Logan Gilbert (through 2028) or reliever Bryan Baker nets picks but kills their last title shot. Instead, they should reverse course, buy pitching depth, and make one final run with their aging squad before the age curve catches up.

## Top Players Available on Selling Teams (Keeper-Value Ranked)
{readme_players}
""")

print("Generated trade-deadline/README.md")
