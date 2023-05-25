export interface MatchSetupRequest {
  ranges: { [key: string]: RangeSetupRequest };
}

export interface RangeSetupRequest {
  classes: { [key: string]: ClassSetupRequest };
}

export interface ClassSetupRequest {
  participants: string[];
  times: number;
}

export interface Match {
  ranges: { [key: string]: Duel[] }
}

export interface Duel {
  left: Participant
  right: Participant
  clazz: string
}

export interface Participant {
  name: string
}

export const CLASSES = ["S", "SL", "SM", "M", "O"];
export const RANGES = ["1", "2"];

export function EmptyMatchSetupRequest(): MatchSetupRequest {
  return {
    ranges: {
      "1": {
        classes: {
          S: {participants: [], times: 1},
          SL: {participants: [], times: 1},
          SM: {participants: [], times: 1},
          M: {participants: [], times: 1},
          O: {participants: [], times: 1},
        }
      },
      "2": {
        classes: {
          S: {participants: [], times: 1},
          SL: {participants: [], times: 1},
          SM: {participants: [], times: 1},
          M: {participants: [], times: 1},
          O: {participants: [], times: 1},
        }
      }
    }
  }
}
