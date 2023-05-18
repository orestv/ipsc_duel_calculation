import React, {useEffect, useState} from "react";
import MatchSetup from "./match_setup";
import DuelsList from "./duels_list";
import {Match, MatchSetupRequest} from "../models";
import {API_ROOT, getMatchSetupFromLocalStorage, saveMatchSetupToLocalStorage} from "../storage";

export default function App() {
  const defaultMatchSetup: MatchSetupRequest = {ranges: {}}
  const [matchSetup, setMatchSetup] = useState(defaultMatchSetup)
  const [match, setMatch] = useState(null)
  const [isLoading, setLoading] = useState(false)

  const handleMatchSetup = function (r: MatchSetupRequest) {
    setMatchSetup(r)
  }

  useEffect(
    () => {
      const storedMatchSetup = getMatchSetupFromLocalStorage();
      console.log("Loaded match from storage: ");
      console.log(storedMatchSetup);
      setMatchSetup(storedMatchSetup);
    },
    []
  )
  useEffect(
    () => {
      saveMatchSetupToLocalStorage(matchSetup)
      const dataFetch = async () => {
        const requestOptions = {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(matchSetup),
        }
        const data = await (
          await fetch(`${API_ROOT}/duels`, requestOptions)
        ).json()
      }
      dataFetch()
    },
    [matchSetup]
  )

  useEffect(() => {
    (async () => {
      setLoading(true)
      const response = await fetch(
        `${API_ROOT}/duels`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          mode: "cors",
          body: JSON.stringify(matchSetup),
        }
      );
      const receivedMatch: Match = JSON.parse(await response.text())
      setLoading(false)
      setMatch(receivedMatch)

    })()
  }, [matchSetup])

  return (
    <>
      <div className="container-fluid my-4">
        <MatchSetup onMatchSetup={handleMatchSetup} matchSetup={matchSetup}/>
      </div>
      <div className="container-fluid my-4">
        <DuelsList match={match} isLoading={isLoading}/>
      </div>
    </>
  )
}
