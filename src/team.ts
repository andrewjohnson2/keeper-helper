import { reactive } from "vue";
import { getCommaSeparatedValues } from "./csv";

interface Player {
  id: string;
  position: string;
  name: string;
  team: string;
  age: string;
  contract: string;
  contractDetails?: ContractDetails;
  draftPick?: DraftPick;
  selected: boolean;
  isNewSelection: boolean;
}

interface ContractDetails {
  rank: string;
  draftPick: string;
}

interface Team {
  players: Player[];
  id: Number;
  name: string;
}

interface TeamStore {
  teams: Team[];
  draft: DraftPick[];
  currentTeamId: Number | undefined;
}

const store: TeamStore = reactive({
  teams: [],
  draft: [],
  currentTeamId: undefined
});

export class DraftPick {
  round: string;
  pick: string;
  year: string;
  playerId: string;
}
// export const TEAM_IDS: Number[] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];

export const TEAMS_DEFINITION_FILE = "data/teams.json";
export const DRAFT_DEFINITION_FILE = "data/drafts/2024.csv";

export function init(): void {
  const reader = new FileReader();

  const draftPromise = fetch(DRAFT_DEFINITION_FILE)
    .then((response) => response.text())
    .then((response) => response.split("\n"))
    .then((picks) => {
      store.draft = picks
        .map((pick) => {
          const values = getCommaSeparatedValues(pick);

          const draftPick = new DraftPick();
          draftPick.playerId = values[0];
          draftPick.pick = values[2];
          draftPick.round = values[1];
          draftPick.year = "2024";

          return draftPick;
        })
        .filter((p) => p.playerId !== "*");
    });

  fetch(TEAMS_DEFINITION_FILE)
    .then((response) => response.json())
    .then((response) => response.teams)
    .then((teams) => {
      teams.forEach((team) => {
        const contractsPromise = fetch(
          "data/contracts/" + team.id + ".csv"
        )
          .then((response) => response.text())
          .then((ranks) => {
            const team = ranks.split("\n").map((rank) => {
              const values = getCommaSeparatedValues(rank);

              return {
                playerId: values[0],
                rank: parseInt(values[3]),
                draftPick: values[4],
              };
            });

            return team;
          });

        const playersPromise = fetch("data/teams/" + team.id + ".csv")
          .then((response) => response.text())
          .then((t) => {
            const players = t.split("\n").map((player) => {
              const attributes = getCommaSeparatedValues(player);
              if (attributes.length > 8) {
                if (attributes[0] === 'ID') {
                  return undefined;
                }
                return {
                  id: attributes[0].replaceAll('"', ""),
                  position: attributes[1].replaceAll('"', ""),
                  name: attributes[2].replaceAll('"', ""),
                  team: attributes[3].replaceAll('"', ""),
                  age: attributes[6].replaceAll('"', ""),
                  contract: attributes[7].replaceAll('"', ""),
                  selected: false,
                  isNewSelection: false,
                  isMinorLeagueEligible: attributes[5].replaceAll('"', "") === "Min"
                };
            
              }
              return undefined;
            });
            return players.filter((p) => p !== undefined);
          });

        Promise.all([contractsPromise, playersPromise]).then(
          (contractsAndPlayers) => {
            console.log(contractsAndPlayers);

            const contracts = contractsAndPlayers[0];
            const players = contractsAndPlayers[1];

            players.forEach((p) => {
              const contract = contracts.find((c) => c.playerId === p.id);
              if (contract !== undefined) {
                p.contractDetails = contract;
                p.selected = true;
              } else {
                draftPromise.then((ignored) => {
                  const pick = store.draft.find((pick) => pick.playerId === p.id);

                  if (p.isMinorLeagueEligible && !pick) {
                    p.isMinorLeagueEligible = false;
                  }

                  if (pick) {
                    p.draftPick = pick;
                  } else {
                    p.draftPick = {
                      round: 26,
                      pick: 12,
                      year: 2024,
                      playerId: p.id
                    }
                  }
                });
              }
            });

            store.teams.push({
              ...team,
              players: players,
            });
          }
        );
      });
    });
}

export function getTeamForId(id: Number) : Team {
  return store.teams.find((t) => t.id === id);
}

export function setCurrentTeam(id) {
    store.currentTeamId = id;
}

export function getCurrentTeam() : Team {
    return getTeamForId(store.currentTeamId);
}

export function getAllTeams(): Team[] {
  return store.teams;
}
