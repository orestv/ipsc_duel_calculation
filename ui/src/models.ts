export interface MatchSetupRequest {
  ranges: { [key: string]: RangeSetupRequest };
}

export interface RangeSetupRequest {
  classes: { [key: string]: ClassSetupRequest };
}

export interface ClassSetupRequest {
  participants: string[];
  twice: boolean;
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
          S: {participants: [], twice: false},
          SL: {participants: [], twice: false},
          SM: {participants: [], twice: false},
          M: {participants: [], twice: false},
          O: {participants: [], twice: false},
        }
      },
      "2": {
        classes: {
          S: {participants: [], twice: false},
          SL: {participants: [], twice: false},
          SM: {participants: [], twice: false},
          M: {participants: [], twice: false},
          O: {participants: [], twice: false},
        }
      }
    }
  }
}
