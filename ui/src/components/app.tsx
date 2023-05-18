import React, {useEffect, useState} from "react";
import MatchLoader from "./loader";
import MatchSetup from "./match_setup";
import DuelsList from "./duels_list";
import {EmptyMatchSetupRequest, Match, MatchSetupRequest, RangeSetupRequest} from "../models";
import {API_ROOT, getMatchSetupFromLocalStorage, saveMatchSetupToLocalStorage} from "../storage";

export default function App() {
  const [matchSetup, setMatchSetup] = useState(EmptyMatchSetupRequest())
  const [match, setMatch] = useState(null)
  const [isLoading, setLoading] = useState(false)
  const [isMatchLoaderVisible, setMatchLoaderVisible] = useState(false)

  const handleMatchSetup = function (r: MatchSetupRequest) {
    setMatchSetup(r)
  }

  const handleResetMatchClick = function () {
    if (!confirm("Це скине поточне налаштування матчу: впевнені?")) {
      return;
    }
    setMatchSetup(EmptyMatchSetupRequest())
  }

  const handleMatchLoaded = function(r:  MatchSetupRequest) {
    setMatchSetup(r)
    setMatchLoaderVisible(false)
  }

  const handleMatchLoaderCanceled = () => {
    setMatchLoaderVisible(false)
  }

  useEffect(
    () => {
      const storedMatchSetup = getMatchSetupFromLocalStorage();
      setMatchSetup(storedMatchSetup);
    },
    []
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
    saveMatchSetupToLocalStorage(matchSetup);
  }, [matchSetup])

  return (
    <>
      <nav className="navbar navbar-light bg-light">
        <div className="container-fluid d-flex">
          <h1>Дуелі</h1>
          <button type="button" className="btn btn-primary"
                  onClick={() => {
                    setMatchLoaderVisible(true)
                  }}>
            Додати список з Practicarms
          </button>
          <button type={"button"} className={"btn btn-outline-danger"} onClick={handleResetMatchClick}>Очистити</button>
        </div>
      </nav>
      <div className="container-fluid my-4">
        <MatchLoader visible={isMatchLoaderVisible} onMatchLoaded={handleMatchLoaded} onCanceled={handleMatchLoaderCanceled}/>
      </div>
      <div className="container-fluid my-4">
        <MatchSetup onMatchSetup={handleMatchSetup} matchSetup={matchSetup}/>
      </div>
      <div className="container-fluid my-4">
        <DuelsList match={match} isLoading={isLoading}/>
      </div>

    </>
  )
}
