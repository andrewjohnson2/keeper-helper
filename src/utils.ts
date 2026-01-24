export function getPenaltyForDroppingPlayer(player) {
  const rank = player.contractDetails.rank;
  const year = player.contractDetails.year;
  let base;
  if (rank <= 2) {
    base = 3;
  } else if (rank <= 4) {
    base = 5;
  } else if (rank <= 6) {
    base = 7;
  } else {
    base = 10;
  }

  base = base - Math.max(0, parseInt(year) - 2025);
  if (base === 0) {
    return "Cannot Drop Player";
  }
  if (base === 1) {
    return "1st round";
  }
  if (base === 2) {
    return "2nd round";
  }
  if (base === 3) {
    return "3rd round";
  }
  return base + "th round";
}

export function formatRound(base) {
  if (base === "Free") {
    return base;
  }
  if (base === 0) {
    return "Cannot Drop Player";
  }
  if (base === 1) {
    return "1st round";
  }
  if (base === 2) {
    return "2nd round";
  }
  if (base === 3) {
    return "3rd round";
  }
  return base + "th round";
}

export function getPenaltyForDroppingPlayerUnformatted(player) {
  const rank = player.contractDetails.rank;
  const year = player.contractDetails.year;
  let base;
  if (rank <= 2) {
    base = 3;
  } else if (rank <= 4) {
    base = 5;
  } else if (rank <= 6) {
    base = 7;
  } else {
    base = 10;
  }

  return base - Math.max(0, parseInt(year) - 2025);
}
