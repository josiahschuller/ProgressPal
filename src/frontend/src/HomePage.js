import * as React from "react";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import API_URL from "./API_URL";
import Stack from "@mui/material/Stack";
import { Link } from "react-router-dom";
import { Typography } from "@mui/material";

import ButtonAppBar from "./AppBar";
import HelpIcon from "@mui/icons-material/Help";

import { PolarArea } from "react-chartjs-2";

import {
  Chart as ChartJS,
  RadialLinearScale,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(RadialLinearScale, ArcElement, Tooltip, Legend);

export default function ReviewPage() {
  // get the goals and corresponding goal progression
  const [goals, setGoals] = React.useState([]);
  const [goalsLoaded, setGoalsLoaded] = React.useState(false);

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
              goalsResponse[goal].key = goalsResponse[goal].goal_id;
              goalsResponse[goal].activities = goalsResponse[
                goal
              ].goal_activities.map((activity) => {
                return {
                  score: activity.activity_impact,
                  key: activity.activity_id,
                  name: activity.activity_name,
                };
              });

              goalsList.push(goalsResponse[goal]);
            }
            console.log(goalsList);
            setGoals(goalsList);
          }
          setGoalsLoaded(true);
        });
    }
  });

  document.body.style.backgroundColor = "#F4FFFE";

  return (
    <Box sx={{ flexGrow: 1 }}>
      <ButtonAppBar page="Home" goals={goals} />
      <ReviewContent goals={goals} />
    </Box>
  );
}

function ReviewContent(props) {
  const { goals } = props;

  const reportActivitiesButton = () => {
    if (goals.length !== 0) {
      return (
        <Link to="/report">
          <Button
            variant="contained"
            sx={{ m: 2 }} // Margin
            style={{
              maxWidth: "500px",
              minWidth: "200px",
              background: "#0EB8A7",
            }}
          >
            Report Activities
          </Button>
        </Link>
      )
    }
  }

  const allZero = goals.every((score) => score === 0);

  let caption = "";
  if (goals.length === 0) {
    caption = "Welcome to ProgressPal! This diagram is blank now but will display your progress towards your goal. Looks like you do not have any goals yet, so to the Edit Goals page to add a goal and start tracking your progress.";
  } else if (allZero.length === 0) {
    caption = "Now that you have a goal, you can start reporting your completed activities to achieve your goal. Go to the Report Activities page to report your activities.";
  } else {
    caption = "This chart indicates how far you have come to achieve your goal.";
  }

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "center",
        }}
      >
        <RoseChart goals={goals} />
      </div>
      <Box sx={{ display: "flex", justifyContent: "center" }}>
        <Box width="700px">
          <Box sx={{ display: "flex", justifyContent: "center" }}>
            <p>{caption}</p>
          </Box>
        </Box>
      </Box>
      <Box display="flex" sx={{ justifyContent: "center" }}>
        <Stack direction="row">
          <Link to="/edit">
            <Button
              variant="contained"
              sx={{ m: 2 }} // Margin
              style={{
                maxWidth: "500px",
                minWidth: "200px",
                background: "#0EB8A7",
              }}
            >
              Edit goals & activities
            </Button>
          </Link>
          {reportActivitiesButton()}
        </Stack>
      </Box>
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

function RoseChart(props) {
  // rose chart: https://react-chartjs-2.js.org/examples/polar-area-chart/
  const { goals } = props;

  document.body.style.backgroundColor = "#F4FFFE";


  const goalLabels = goals.map((goal) => goal.goal_name);
  const scores = goals.map((goal) => goal.goal_current_state);

  const data = {
    labels: goalLabels,
    datasets: [
      {
        label: "Goal progression rose chart",
        data: scores,
        backgroundColor: [
          "rgba(255, 99, 132, 0.5)",
          "rgba(54, 162, 235, 0.5)",
          "rgba(255, 206, 86, 0.5)",
          "rgba(75, 192, 192, 0.5)",
          "rgba(153, 102, 255, 0.5)",
          "rgba(255, 159, 64, 0.5)",
        ],
        borderWidth: 1,
      },
    ],
  };

  // Set the default range of the chart to 0...100
  // NOTE: the chart will still display data that exceeds this range
  const options = {
    scales: {
      r: {
        suggestedMin: 0,
        suggestedMax: 100,
      },
    },
    onClick: (event, chartElements) => {
      // If the user clicks on a goal
      if (chartElements.length > 0) {
        // Get the goal that was clicked
        const goal = goals[chartElements[0].index];
        // Redirect to the goal page
        window.location.href = `/goals/${goal.goal_id}`;
      }
    },
  };

  return (
    <Box sx={{ width: "700px", justifyContent: "center", m: 3 }}>
      <Stack direction="row">
        <Box sx={{ width: "20%" }}/>
        <Box sx={{ width: "60%", justifyContent: "center" }}>
          <PolarArea data={data} options={options} />
        </Box>
        <Box sx={{ width: "20%" }}/>
      </Stack>
    </Box>
  );
}
