import * as React from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import { Link } from "react-router-dom";
import { useLocation } from "react-router-dom";
import { Typography } from "@mui/material";

import ButtonAppBar from "./AppBar";

import HelpIcon from "@mui/icons-material/Help";

import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import API_URL from "./API_URL";

import {
  Chart as ChartJS,
  RadialLinearScale,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(RadialLinearScale, ArcElement, Tooltip, Legend);

export default function GoalDetailPage() {
  const [goalsLoaded, setGoalsLoaded] = React.useState(false);
  const [goals, setGoals] = React.useState([]);
  const [goal, setGoal] = React.useState(null);

  // Get the goal ID from the URL
  const url = useLocation().pathname;
  const goal_id = parseInt(url.match(/\d+$/)[0]);

  // Get goals
  React.useEffect(() => {
    if (!goalsLoaded) {
      // Get access token from local storage
      const user_id = localStorage.getItem("user_id");
      const access_token = localStorage.getItem("access_token");

      // Get goals
      let url = `${API_URL}/get-goals`;
      fetch(url, {
        headers: {
          "X-User-Id": user_id,
          Authorization: "Bearer " + access_token,
        },
        method: "GET",
      })
        .then((response) => response.json())
        .then((response) => {
          if ("error" in response) {
            // If there is an error
            setGoals([]);
          } else {
            // Successful response
            let goalsList = [];
            let goalsResponse = JSON.parse(response.goals);
            for (let goal in goalsResponse) {
              goalsResponse[goal].key = goalsResponse[goal].goal_id; // Key
              goalsResponse[goal].goal_activities = goalsResponse[
                goal
              ].goal_activities.map((activity) => {
                return {
                  ...activity, // Activity object
                  key: activity.activity_id, // Add a key
                };
              });

              goalsList.push(goalsResponse[goal]);
            }
            setGoals(goalsList);

            // Set the goal for this page
            setGoal(goalsList.filter((goal) => goal.key === goal_id)[0]);
          }
          setGoalsLoaded(true);
        });
    }
  });

  document.body.style.backgroundColor = "#F4FFFE";

  return (
    <Box sx={{ flexGrow: 1 }}>
      <ButtonAppBar page={goal ? goal.goal_name : "null"} goals={goals} />
      <GoalDetailContent goal={goal} />
    </Box>
  );
}

function GoalDetailContent(props) {
  // progression chart: https://www.npmjs.com/package/react-circular-progressbar
  let { goal } = props;

  if (goal === null) {
    // Goal is still loading
    // Set empty goal
    goal = {
      goal_current_state: 0,
      goal_activities: [],
      goal_notes: [],
      key: 0,
    };
  } else if (goal === undefined) {
    // The goal does not exist
    // Go to the home page
    window.location.href = "/home";
  }
  console.log(goal);

  const helpfulActivities = goal.goal_activities.filter(
    (activity) => parseInt(activity.activity_impact) > 0
  );
  const unhelpfulActivities = goal.goal_activities.filter(
    (activity) => parseInt(activity.activity_impact) < 0
  );

  return (
    <div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Box sx={{ margin: "50px" }}>
          <CircularProgressbar
            value={goal.goal_current_state}
            maxValue={100}
            text={`${goal.goal_current_state}%`}
            styles={buildStyles({
              textColor: "#08948c",
            })}
          />
        </Box>
      </div>
      <div>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-evenly",
            flexWrap: "wrap",
            margin: "20px",
          }}
        >
          <br />
          <Box>
            <h2 style={{ color: "#178E5A" }}>Activities which help</h2>
            {helpfulActivities.map((activity) => (
              <p key={activity.key}>
                {`${activity.activity_name} (impact score: ${activity.activity_impact})`}
              </p>
            ))}
          </Box>
          <Box>
            <h2 style={{ color: "red" }}>Activities which don't help</h2>
            {unhelpfulActivities.map((activity) => (
              <p key={activity.key}>
                {`${activity.activity_name} (impact score: ${activity.activity_impact})`}
              </p>
            ))}
          </Box>
          <Box>
            <h2>Personal notes</h2>
            <p> {goal.goal_notes}</p>
          </Box>
        </Box>
      </div>
      <div>
        <Box sx={{ display: "flex", justifyContent: "center", m: "30px" }}>
          <Link to="/edit">
            <Button
              size="large"
              variant="contained"
              style={{ background: "#178E5A" }}
            >
              Edit
            </Button>
          </Link>
        </Box>
      </div>
      <Link to="/help">
        <Box sx={{ position: "fixed", bottom: 5, right: 5 }}>
          <Button variant="outlined" color="success">
            <HelpIcon style={{ color: "#08948c" }} />
            <Typography
              variant="h6"
              component="h2"
              style={{ color: "#08948c" }}
            >
              HELP
            </Typography>
          </Button>
        </Box>
      </Link>
    </div>
  );
}
